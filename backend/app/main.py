from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .engine import solve, classify, exact
import re

app=FastAPI(title="EDO Local", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:5173","http://localhost:5173"], allow_methods=["GET","POST"], allow_headers=["Content-Type"])

class EquationRequest(BaseModel):
    ecuacion: str = Field(default="", max_length=600)
    modo: str = Field(default="automatico", pattern="^(automatico|lineal|exacta|homogenea)$")
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
        equation=re.sub(r"y\s*\^\s*\{\\prime\\prime\}","y''",request.ecuacion)
        equation=re.sub(r"y\s*\^\s*\{\\prime\}","y'",equation)
        return classify(equation)
    except (ValueError, TypeError) as exc: raise HTTPException(status_code=422, detail=str(exc))

@app.post("/api/resolver")
def resolve(request: EquationRequest):
    try: return solve(request.model_dump(exclude_none=True))
    except (ValueError, KeyError, TypeError, NotImplementedError) as exc: raise HTTPException(status_code=422, detail=str(exc))
