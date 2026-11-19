import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.engine import solve, classify

def test_linear_initial_condition():
    r=solve({"ecuacion":"y'+3*y=9","x0":"0","y0":"2"})
    assert r["solucion_latex"] == r"3 - e^{- 3 x}"
    assert r["verificacion"]["estado"] == "correcta"
    assert len(r["pasos"]) >= 7

def test_linear_decimal():
    r=solve({"ecuacion":"y'+0.4*y=8","x0":"0","y0":"5"})
    assert r["verificacion"]["condicion_inicial"]

def test_exact_potential_examples():
    r=solve({"modo":"exacta","M":"4*x*y+2","N":"2*x^2+6*y"})
    assert "2 x^{2} y" in r["solucion_latex"]
    assert r["verificacion"]["estado"] == "correcta"
    r=solve({"modo":"exacta","M":"2*x+y","N":"x+4*y"})
    assert "x^{2}" in r["solucion_latex"]

def test_homogeneous_classification_and_solution():
    assert "homogenea_primer_orden" in classify("y'=(2*x+y)/x")["familias_compatibles"]
    r=solve({"ecuacion":"y'=(2*x+y)/x"})
    assert "log" in r["solucion_latex"]
    assert "x≠0" in r["restricciones_dominio"]

def test_second_order_equilibrium_examples():
    r=solve({"ecuacion":"y''+y'=(y')^2","x0":"0","yp0":"1","y0":"0"})
    assert r["solucion_latex"] == "x"
    assert r["rama_utilizada"] == "equilibrio"
    r=solve({"ecuacion":"y''+2*y'=2*(y')^3","x0":"0","yp0":"1","y0":"2"})
    assert r["solucion_latex"] == "x + 2"

def test_second_order_classifier_rejects_unrelated_equation():
    info=classify("y''+x*y=sin(x)")
    assert info["familias_compatibles"] == []
    assert info["metodo_prioritario"] is None

def test_classifier_does_not_call_nonlinear_linear():
    assert classify("y'+y^2=0")["familias_compatibles"] == []
    info=classify("y'=(2*x+y)/x")
    assert info["lineal"] is True
    assert info["familias_compatibles"] == ["homogenea_primer_orden", "lineal_primer_orden"]

def test_reject_code():
    try: solve({"ecuacion":"y'=__import__('os')"})
    except ValueError: return
    assert False, "el parser debe rechazar llamadas arbitrarias"

def test_non_exact_is_rejected():
    try: solve({"modo":"exacta","M":"x+y","N":"x+2*y"})
    except ValueError as exc: assert "no es exacta" in str(exc)
    else: assert False, "una forma no exacta no debe aceptarse"

def test_api_health_and_resolve():
    from fastapi.testclient import TestClient
    from app.main import app
    client=TestClient(app)
    assert client.get("/api/health").status_code == 200
    response=client.post("/api/resolver",json={"ecuacion":"y'+3*y=9","x0":"0","y0":"2"})
    assert response.status_code == 200
    assert response.json()["verificacion"]["estado"] == "correcta"
