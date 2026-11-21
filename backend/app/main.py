from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging
from .engine import solve, classify, exact
from .safe_math import normalize_equation
import re
from pathlib import Path
from fastapi.staticfiles import StaticFiles

app=FastAPI(title="EDO Local", version="0.1.0")
logger=logging.getLogger("edo_lab")
# CORS is only needed for the optional Vite development server. Production is same-origin.
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:5173","http://localhost:5173"], allow_methods=["GET","POST"], allow_headers=["Content-Type"])

def project_root() -> Path:
    import sys
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]

class EquationRequest(BaseModel):
    ecuacion: str = Field(default="", max_length=600)
    modo: str = Field(default="automatico", pattern="^(automatico|lineal|exacta|homogenea|separable|bernoulli)$")
    tipo: str | None = Field(default=None, max_length=50)
    M: str | None = Field(default=None, max_length=300)
    N: str | None = Field(default=None, max_length=300)
    x0: str | None = Field(default=None, max_length=50)
    y0: str | None = Field(default=None, max_length=50)
    yp0: str | None = Field(default=None, max_length=50)

@app.get("/api/health")
def health(): return {"estado":"local", "version":"0.1.0"}

@app.post("/api/identificar")
def identify(request: EquationRequest):
    try:
        if request.modo == "exacta":
            analysis=exact(request.M or "",request.N or "")
            return {"orden":1,"variable_independiente":"x","variable_dependiente":"y","lineal":False,"familias_compatibles":["exacta"],"metodo_prioritario":"funcion_potencial","verificacion":analysis["verificacion"]}
        equation=normalize_equation(request.ecuacion)
        return classify(equation)
    except (ValueError, TypeError) as exc: raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception("Error inesperado durante la clasificación")
        raise HTTPException(status_code=500, detail="No se pudo completar la clasificación simbólica. Simplifica la entrada e inténtalo de nuevo.") from exc

@app.post("/api/resolver")
def resolve(request: EquationRequest):
    try: return solve(request.model_dump(exclude_none=True))
    except (ValueError, KeyError, TypeError, NotImplementedError) as exc: raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception("Error inesperado durante la resolución simbólica")
        raise HTTPException(status_code=500, detail="No se pudo completar la operación simbólica. Simplifica la entrada e inténtalo de nuevo.") from exc

_frontend_dist=project_root()/"frontend"/"dist"
if (_frontend_dist/"index.html").is_file():
    # Register last: API endpoints must win before the catch-all frontend mount.
    app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="frontend")
