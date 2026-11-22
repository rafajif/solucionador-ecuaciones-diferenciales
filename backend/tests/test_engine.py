import sys
from pathlib import Path
import sympy as sp
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

def test_automatic_exact_form_classification_and_solution():
    equation="(4*x*y+2)*dx+(2*x^2+6*y)*dy=0"
    info=classify(equation)
    assert info["familias_compatibles"] == ["exacta"]
    answer=solve({"ecuacion":equation})
    assert answer["tipo_ecuacion"] == "exacta"
    assert answer["verificacion"]["estado"] == "correcta"

def test_automatic_exact_form_with_equal_cross_partials_is_solved():
    equation="(x+y)*dx+(x+2*y)*dy=0"
    info=classify(equation)
    assert info["familias_compatibles"] == ["exacta"]

    answer=solve({"ecuacion":equation})
    assert answer["tipo_ecuacion"] == "exacta"
    assert answer["verificacion"]["estado"] == "correcta"
    assert "x^{2}" in answer["solucion_latex"]
    assert "x y" in answer["solucion_latex"]
    assert "y^{2}" in answer["solucion_latex"]

def test_automatic_exactness_rejects_nonexact_form():
    equation="(x+y)*dx+(2*x+y)*dy=0"
    assert classify(equation)["familias_compatibles"] == []
    try: solve({"ecuacion":equation})
    except ValueError as exc: assert "no es exacta" in str(exc)
    else: assert False, "no debe tratar una forma no exacta como exacta"

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

def test_reject_infinite_numeric_literal():
    try: solve({"ecuacion":"y'=1e999"})
    except ValueError: return
    assert False, "el parser debe rechazar valores no finitos"

def test_non_exact_is_rejected():
    try: solve({"modo":"exacta","M":"x+y","N":"2*x+y"})
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

def test_mathlive_latex_linear_equation_integration():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    # MathLive getValue('latex') serializes derivative superscripts and
    # multiplication using LaTeX commands, unlike the parser's ASCII syntax.
    response = client.post("/api/resolver", json={
        "ecuacion": r"y^{\prime}+3\cdot y=9", "x0": "0", "y0": "2"
    })
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["solucion_latex"] == r"3 - e^{- 3 x}"
    assert result["verificacion"]["estado"] == "correcta"
    identified = client.post("/api/identificar", json={"ecuacion": r"y^{\prime}+3\cdot y=9"})
    assert identified.status_code == 200, identified.text
    assert identified.json()["familias_compatibles"] == ["lineal_primer_orden"]

def test_mathlive_latex_second_order_derivatives_and_exponent():
    from fastapi.testclient import TestClient
    from app.main import app
    response = TestClient(app).post("/api/resolver", json={
        "ecuacion": r"y^{\prime\prime}+y^{\prime}=(y^{\prime})^{2}",
        "x0": "0", "y0": "0", "yp0": "1"
    })
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["solucion_latex"] == "x"
    assert result["verificacion"]["estado"] == "correcta"

def test_mathlive_fraction_and_unknown_tex_command_validation():
    from app.safe_math import parse_expr, normalize_equation, x as parser_x
    parsed = parse_expr(r"\frac{x^2+1}{2}")
    expected = (parser_x**2 + 1) / 2
    assert parsed.free_symbols == {parser_x}
    assert sp.simplify(parsed - expected) == 0
    assert parse_expr(r"\sin x") == sp.sin(parser_x)
    try:
        normalize_equation(r"y'=\input{file}=0")
    except ValueError as exc:
        assert "no permitido" in str(exc)
    else:
        assert False, "no se deben aceptar comandos TeX arbitrarios"

def test_mathlive_nested_fractions_exponents_and_symbol_assumptions():
    from app.safe_math import parse_expr, x as parser_x

    unconstrained_x = sp.Symbol("x")
    assert parser_x != unconstrained_x
    assert parser_x.assumptions0.get("real") is True
    assert unconstrained_x.assumptions0.get("real") is None

    nested = parse_expr(r"\frac{1}{\frac{2}{x^2}}")
    assert nested.free_symbols == {parser_x}
    assert sp.simplify(nested - parser_x**2 / 2) == 0

    powered = parse_expr(r"\left(\frac{x+1}{2}\right)^2")
    assert sp.simplify(powered - ((parser_x + 1) / 2)**2) == 0

def test_linear_initial_value_zero_is_preserved_and_steps_are_complete():
    from fastapi.testclient import TestClient
    from app.main import app

    result = solve({"ecuacion": "y'+2*y=6", "x0": "0", "y0": "1"})
    assert result["solucion_latex"] == r"3 - 2 e^{- 2 x}"
    assert result["tipo_solucion"] == "particular"
    assert result["verificacion"]["estado"] == "correcta"
    assert result["verificacion"]["residuo"] == "0"
    assert result["verificacion"]["condicion_inicial"] is True
    assert result["verificacion"]["residuo_condicion_inicial"] == "0"
    titles = [step["titulo"] for step in result["pasos"]]
    assert "Sustitución de la condición inicial" in titles
    assert "Cálculo de la constante" in titles
    assert "Solución particular" in titles

    response = TestClient(app).post("/api/resolver", json={
        "ecuacion": "y'+2*y=6", "x0": "0", "y0": "1"
    })
    assert response.status_code == 200, response.text
    assert response.json()["solucion_latex"] == r"3 - 2 e^{- 2 x}"

def test_linear_without_initial_values_returns_general_solution():
    result = solve({"ecuacion": "y'+2*y=6"})
    assert result["tipo_solucion"] == "general"
    assert "C" in result["solucion_latex"]
    assert result["verificacion"]["estado"] == "correcta"

def test_api_rejects_incomplete_initial_value_pair():
    from fastapi.testclient import TestClient
    from app.main import app
    response = TestClient(app).post("/api/resolver", json={
        "ecuacion": "y'+2*y=6", "x0": "0"
    })
    assert response.status_code == 422
    assert "x0" in response.json()["detail"]
