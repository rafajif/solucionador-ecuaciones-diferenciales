import re
import sympy as sp
from .safe_math import x, y, dx, dy, parse_expr, latex, normalize_equation

C = sp.symbols("C")


def step(title, explanation, before, operation, after, reason):
    return {
        "numero": 0,
        "titulo": title,
        "explicacion": explanation,
        "expresion_anterior": latex(before) if not isinstance(before, str) else before,
        "operacion": operation,
        "expresion_latex": latex(after) if not isinstance(after, str) else after,
        "justificacion": reason,
    }


def result(kind, method, steps, solution, status="general", verification="indeterminada", domain=None):
    for i, item in enumerate(steps, 1):
        item["numero"] = i
    return {
        "tipo_ecuacion": kind,
        "metodo": method,
        "orden": 1,
        "variable_independiente": "x",
        "variable_dependiente": "y",
        "lineal": kind == "lineal_primer_orden",
        "pasos": steps,
        "solucion": str(solution),
        "solucion_latex": latex(solution),
        "tipo_solucion": status,
        "verificacion": {"estado": verification, "residuo": None},
        "restricciones_dominio": domain or [],
    }


# ---------------------------------------------------------------------------
# Lineal de primer orden  y' + P(x)y = Q(x)
# ---------------------------------------------------------------------------
def linear(equation, initial=None):
    match = re.fullmatch(r"\s*y'\s*([+-].+?)\s*=\s*(.+?)\s*", equation)
    if match:
        left = parse_expr(match.group(1))
        q = parse_expr(match.group(2))
        p = sp.diff(left, y)
        if left.has(y) and sp.simplify(left - p * y) != 0:
            raise ValueError("La ecuación no es lineal en y.")
    else:
        explicit = re.fullmatch(r"\s*y'\s*=\s*(.+?)\s*", equation)
        if not explicit:
            raise ValueError("La ecuación no coincide con y'+P(x)y=Q(x).")
        rhs = parse_expr(explicit.group(1))
        p = -sp.diff(rhs, y)
        q = sp.simplify(rhs + p * y)
        if sp.diff(rhs, y, 2) != 0:
            raise ValueError("La ecuación no es lineal en y.")
    if p.has(y) or q.has(y):
        raise ValueError("P y Q deben depender únicamente de x.")
    mu = sp.exp(sp.integrate(p, x))
    integral = sp.integrate(sp.simplify(mu * q), x)
    general = sp.simplify((integral + C) / mu)
    P_symbol = sp.Function("P")(x)
    Q_symbol = sp.Function("Q")(x)
    y_prime = sp.Derivative(y, x, evaluate=False)
    standard_equation = sp.Eq(y_prime + p * y, q, evaluate=False)
    weighted_equation = sp.Eq(mu * y_prime + mu * p * y, mu * q, evaluate=False)
    product_equation = sp.Eq(sp.Derivative(mu * y, x, evaluate=False), mu * q, evaluate=False)
    steps = [
        step(
            "Identificación de coeficientes",
            "Se escribe la EDO en forma estándar y se identifican P(x) y Q(x).",
            equation,
            "Comparar con y' + P(x)y = Q(x)",
            sp.Eq(sp.Tuple(P_symbol, Q_symbol), sp.Tuple(p, q), evaluate=False),
            "P y Q dependen solo de x; la derivada de y es ordinaria respecto de x.",
        ),
        step(
            "Factor integrante",
            "Se integra P(x) y se aplica la exponencial.",
            p,
            "mu(x) = exp(integral P(x) dx)",
            mu,
            "Esta elección hace que mu' = P·mu.",
        ),
        step(
            "Multiplicación por el factor integrante",
            "Se multiplica cada término de la ecuación estándar por mu(x).",
            standard_equation,
            "Multiplicar ambos lados por mu(x)",
            weighted_equation,
            "La igualdad se conserva al multiplicar ambos lados por la misma función.",
        ),
        step(
            "Derivada de un producto",
            "El lado izquierdo es la derivada ordinaria del producto mu(x)·y(x).",
            weighted_equation,
            "Aplicar la regla del producto",
            product_equation,
            "d(mu·y)/dx = mu·y' + mu'·y, y mu'=P·mu.",
        ),
        step(
            "Integración",
            "Se integra respecto de x y se incorpora la constante C.",
            mu * q,
            "Integrar ambos lados respecto de x",
            sp.Eq(mu * y, integral + C, evaluate=False),
            "La integral indefinida introduce la constante de integración.",
        ),
        step(
            "Solución general",
            "Se despeja y antes de aplicar datos iniciales.",
            sp.Eq(mu * y, integral + C, evaluate=False),
            "Dividir entre mu(x)",
            sp.Eq(y, general, evaluate=False),
            "mu(x)=exp(∫P dx) no se anula; C permanece libre hasta imponer una condición inicial.",
        ),
    ]
    solution, kind = general, "general"
    initial_residual = None
    x0_val = y0_val = None
    if initial:
        x0_val = sp.sympify(initial["x0"])
        y0_val = sp.sympify(initial["y0"])
        initial_equation = sp.Eq(general.subs(x, x0_val), y0_val)
        constant = sp.solve(initial_equation, C)
        if not constant:
            raise ValueError("No se pudo calcular la constante con la condición inicial.")
        constant_value = sp.simplify(constant[0])
        solution = sp.simplify(general.subs(C, constant_value))
        kind = "particular"
        steps.extend([
            step(
                "Sustitución de la condición inicial",
                f"Se sustituye x={x0_val} e y={y0_val} en la solución general.",
                general,
                "Evaluar y(x) en x=x₀ e igualar a y₀",
                initial_equation,
                "La condición inicial produce una ecuación para la constante.",
            ),
            step(
                "Cálculo de la constante",
                "Se despeja la constante de integración.",
                initial_equation,
                "Resolver respecto de C",
                sp.Eq(C, constant_value),
                "El dato inicial fija el valor de C.",
            ),
            step(
                "Solución particular",
                "Se sustituye el valor calculado de C en la solución general.",
                general,
                f"Sustituir C={constant_value}",
                sp.Eq(y, solution),
                "La solución resultante satisface la EDO y la condición inicial.",
            ),
        ])
    residual = sp.simplify(sp.diff(solution, x) + p * solution - q)
    if initial:
        initial_residual = sp.simplify(solution.subs(x, x0_val) - y0_val)
    equation_verified = residual == 0 or residual.is_zero is True
    equation_failed = residual.is_zero is False
    initial_verified = initial_residual is None or initial_residual == 0 or initial_residual.is_zero is True
    initial_failed = initial_residual is not None and initial_residual.is_zero is False
    ver = (
        "fallida" if equation_failed or initial_failed
        else "correcta" if equation_verified and initial_verified
        else "indeterminada"
    )
    out = result("lineal_primer_orden", "factor_integrante", steps, solution, kind, ver)
    out["verificacion"]["residuo"] = latex(residual)
    if initial:
        out["verificacion"]["residuo_condicion_inicial"] = latex(initial_residual)
        out["verificacion"]["condicion_inicial"] = bool(initial_verified)
    return out


# ---------------------------------------------------------------------------
# Separable  y' = f(x)·g(y)
# ---------------------------------------------------------------------------
def separable(equation, initial=None):
    match = re.fullmatch(r"\s*y'\s*=\s*(.+?)\s*", equation)
    if not match:
        raise ValueError("Use la forma explícita y'=F(x,y) para separación de variables.")
    f = parse_expr(match.group(1))
    # Try to factor as fx(x)*gy(y)
    # Strategy: replace y with a fresh symbol, factor, verify
    u = sp.Symbol("_u", real=True)
    expr_u = f.subs(y, u)
    # Attempt: collect all x-parts and y-parts
    # Rewrite as f/g(y) = dx/dy form or factor directly
    try:
        factored = sp.factor(expr_u)
    except Exception:
        factored = expr_u

    # Check by expanding ratio f(x,y)/f_at_y1 and see if it cancels y
    # Robust approach: use separation by collecting
    gx = sp.simplify(f.subs(y, 1))
    gy_candidate = sp.simplify(f / gx) if gx != 0 else None

    if gy_candidate is not None and not gy_candidate.has(x):
        gx_part = gx
        gy_part = gy_candidate
    else:
        # Try dividing by f at x=1
        fx_candidate = sp.simplify(f.subs(x, 1))
        gx_candidate2 = sp.simplify(f / fx_candidate) if fx_candidate != 0 else None
        if gx_candidate2 is not None and not gx_candidate2.has(y):
            gx_part = gx_candidate2
            gy_part = fx_candidate
        else:
            raise ValueError("La ecuación no es separable en f(x)·g(y).")

    # Validate factoring: gx_part*gy_part == f
    if sp.simplify(gx_part * gy_part - f) != 0:
        raise ValueError("La ecuación no es separable: no se pudo factorizar en f(x)·g(y).")

    # Integral 1/g(y) dy = integral h(x) dx
    int_gy = sp.integrate(1 / gy_part, y)
    int_gx = sp.integrate(gx_part, x)

    # Implicit solution: int_gy = int_gx + C
    implicit_lhs = int_gy
    implicit_rhs = int_gx + C

    steps = [
        step(
            "Identificación separable",
            "Se verifica que F(x,y) = f(x)·g(y) y se separan las variables.",
            f,
            "Separar: dy/g(y) = f(x) dx",
            sp.Eq(sp.Rational(1, 1) / gy_part * sp.Symbol("dy"), gx_part * sp.Symbol("dx"), evaluate=False),
            "La separación es válida en regiones donde g(y)≠0.",
        ),
        step(
            "Integración",
            "Se integra cada lado respecto de su variable.",
            sp.Eq(1 / gy_part, gx_part),
            "Integrar: ∫dy/g(y) = ∫f(x)dx + C",
            sp.Eq(implicit_lhs, implicit_rhs, evaluate=False),
            "La constante de integración C engloba ambas constantes.",
        ),
    ]

    # Try to solve explicitly for y
    solution_expr = None
    try:
        sol_list = sp.solve(sp.Eq(implicit_lhs, implicit_rhs), y)
        if sol_list:
            solution_expr = sp.simplify(sol_list[0])
    except Exception:
        pass

    if solution_expr is not None:
        steps.append(step(
            "Solución explícita",
            "Se despeja y en función de x.",
            sp.Eq(implicit_lhs, implicit_rhs, evaluate=False),
            "Despejar y",
            sp.Eq(y, solution_expr, evaluate=False),
            "La solución explícita permite verificar directamente la EDO.",
        ))

    solution_kind = "general"
    final_solution = solution_expr if solution_expr is not None else sp.Eq(implicit_lhs, implicit_rhs)

    if initial and solution_expr is not None:
        x0_val = sp.sympify(initial["x0"])
        y0_val = sp.sympify(initial["y0"])
        eq_c = sp.Eq(solution_expr.subs(x, x0_val), y0_val)
        c_sols = sp.solve(eq_c, C)
        if c_sols:
            cv = sp.simplify(c_sols[0])
            final_solution = sp.simplify(solution_expr.subs(C, cv))
            solution_kind = "particular"
            steps.extend([
                step(
                    "Condición inicial",
                    f"Se sustituye x={x0_val}, y={y0_val} para hallar C.",
                    solution_expr,
                    "Evaluar en la condición inicial",
                    sp.Eq(C, cv),
                    "La condición inicial determina la constante de integración.",
                ),
                step(
                    "Solución particular",
                    "Se sustituye C en la solución general.",
                    solution_expr,
                    f"Sustituir C={cv}",
                    sp.Eq(y, final_solution),
                    "La solución particular satisface la EDO y la condición dada.",
                ),
            ])

    # Verification
    if solution_expr is not None and isinstance(final_solution, sp.Basic):
        sol_check = final_solution if solution_kind == "particular" else solution_expr.subs(C, 0)
        try:
            residual = sp.simplify(sp.diff(final_solution if solution_kind == "particular" else solution_expr, x) - f.subs(y, final_solution if solution_kind == "particular" else solution_expr))
            ver = "correcta" if residual == 0 or residual.is_zero is True else "indeterminada"
        except Exception:
            residual = sp.Symbol("?")
            ver = "indeterminada"
    else:
        residual = sp.Symbol("?")
        ver = "indeterminada"

    out = result("separable", "separacion_variables", steps, final_solution, solution_kind, ver)
    out["verificacion"]["residuo"] = latex(residual)
    return out


# ---------------------------------------------------------------------------
# Ecuación exacta  M dx + N dy = 0
# ---------------------------------------------------------------------------
def exact(M_text, N_text):
    M = M_text if isinstance(M_text, sp.Basic) else parse_expr(M_text)
    N = N_text if isinstance(N_text, sp.Basic) else parse_expr(N_text)
    mx, ny = sp.diff(M, y), sp.diff(N, x)
    if sp.simplify(mx - ny) != 0:
        raise ValueError("La ecuación no es exacta: ∂M/∂y y ∂N/∂x difieren.")
    potential = sp.integrate(M, x)
    gprime = sp.simplify(N - sp.diff(potential, y))
    g = sp.integrate(gprime, y)
    F = sp.simplify(potential + g)
    steps = [
        step("Componentes", "Se identifican M y N.", "M dx + N dy=0", "Separar coeficientes",
             sp.Eq(sp.Symbol("M"), M), "Son los coeficientes de dx y dy."),
        step("Prueba de exactitud", "Se comparan las derivadas parciales cruzadas.", "M,N",
             "Calcular M_y y N_x", sp.Eq(mx, ny), "La igualdad garantiza una función potencial local."),
        step("Integración de M", "Se integra M respecto de x, tratando y como constante.", M,
             "Integrar respecto a x", potential + sp.Function("g")(y),
             "La derivada en x recupera M."),
        step("Término complementario", "Se compara la derivada en y con N.", N,
             "Integrar N−∂F/∂y respecto a y", g,
             "El término independiente de x completa la función potencial."),
        step("Solución implícita", "La curva solución es un nivel de la función potencial.", F,
             "Igualar a constante", sp.Eq(F, C),
             "∇F=(M,N), así dF=Mdx+Ndy=0."),
    ]
    out = result("exacta", "funcion_potencial", steps, sp.Eq(F, C), "implícita", "correcta")
    out["orden"] = 1
    out["lineal"] = False
    out["verificacion"]["residuo"] = latex(
        sp.simplify(sp.diff(F, x) - M) + sp.simplify(sp.diff(F, y) - N)
    )
    return out


# ---------------------------------------------------------------------------
# Homogénea de primer orden  y' = F(y/x)
# ---------------------------------------------------------------------------
def homogeneous(equation, initial=None):
    match = re.fullmatch(r"\s*y'\s*=\s*(.+?)\s*", equation)
    if not match:
        raise ValueError("Use la forma explícita y'=F(x,y).")
    f = parse_expr(match.group(1))
    u = sp.symbols("v", real=True)
    reduced = sp.simplify(f.subs(y, u * x))
    if reduced.has(x):
        raise ValueError("El lado derecho no es homogéneo de grado cero F(y/x).")
    g = sp.simplify(reduced - u)
    if g == 0:
        family = sp.Eq(y, C * x)
        steps = [
            step("Prueba de homogeneidad", "Se sustituye y=vx y el lado derecho se reduce a v.",
                 f, "Sustituir y=vx", reduced, "La expresión solo depende de v=y/x."),
            step("Rama de equilibrio",
                 "La ecuación para v es xv'=0, así que v permanece constante.",
                 sp.Eq(sp.Symbol("vprime"), g), "Integrar v'=0", family,
                 "Esta familia se perdería al dividir por F(v)-v."),
        ]
        out = result("homogenea_primer_orden", "sustitucion_y_vx", steps, family, "general", "correcta", ["x≠0"])
        out["verificacion"]["residuo"] = latex(sp.simplify(sp.diff(C * x, x) - f.subs(y, C * x)))
        return out
    integral = sp.integrate(1 / g, u)
    implicit = sp.Eq(integral, sp.log(sp.Abs(x)) + C)
    steps = [
        step("Prueba de homogeneidad",
             "Se sustituye y=vx y se verifica que F(x,vx) no dependa de x.",
             f, "Sustituir y=vx", reduced,
             "La independencia de x confirma que F depende de y/x."),
        step("Sustitución", "Con y=vx, la derivada es y'=v+xv'.", "y=vx", "Derivar respecto a x",
             sp.Eq(sp.Symbol("yprime"), u + x * sp.Symbol("vprime")), "Regla del producto."),
        step("Separación", "Se resta v y se separan variables.",
             sp.Eq(sp.Symbol("yprime"), reduced), "x dv/dx=F(v)−v",
             sp.Eq(1 / g * sp.Symbol("dv"), sp.Symbol("dx") / x),
             "Separación válida en intervalos donde F(v)−v no sea cero."),
        step("Integración", "Se integran ambos lados.", "dv/(F(v)-v)=dx/x", "Integrar", implicit,
             "La integral de 1/x es ln|x|."),
        step("Regreso a variables originales", "Se usa v=y/x.", implicit, "Sustituir v=y/x",
             sp.Eq(integral.subs(u, y / x), sp.log(sp.Abs(x)) + C),
             "La sustitución inicial define v=y/x."),
    ]
    out = result("homogenea_primer_orden", "sustitucion_y_vx", steps, implicit, "general",
                 "indeterminada", ["x≠0", "Las ramas constantes v donde F(v)-v=0 deben analizarse aparte."])
    equilibria = sp.solve(sp.Eq(g, 0), u)
    out["soluciones_equilibrio_v"] = [latex(e) for e in equilibria]
    try:
        explicit = sp.solve(implicit.subs(u, y / x), y)
        if explicit:
            chosen = explicit[0]
            solution_type = "general"
            if initial:
                x0, y0_val = sp.sympify(initial["x0"]), sp.sympify(initial["y0"])
                if sp.simplify(x0) == 0:
                    raise ValueError("La condición inicial está en x=0, fuera del dominio de la sustitución y=vx.")
                constants = sp.solve(sp.Eq(chosen.subs(x, x0), y0_val), C)
                if not constants:
                    raise ValueError("No se pudo determinar la constante con la condición inicial.")
                chosen = sp.simplify(chosen.subs(C, constants[0]))
                solution_type = "particular"
            out["solucion"] = str(chosen)
            out["solucion_latex"] = latex(chosen)
            out["tipo_solucion"] = solution_type
            residual = sp.simplify(sp.diff(chosen, x) - f.subs(y, chosen))
            out["verificacion"]["residuo"] = latex(residual)
            out["verificacion"]["estado"] = (
                "correcta" if residual == 0
                else "fallida" if residual.is_zero is False
                else "indeterminada"
            )
            if initial:
                out["verificacion"]["condicion_inicial"] = bool(
                    sp.simplify(chosen.subs(x, initial["x0"]) - initial["y0"]) == 0
                )
        elif initial:
            raise ValueError("Se obtuvo una solución implícita que no puede despejarse para aplicar esta condición inicial.")
    except Exception as exc:
        if initial:
            if isinstance(exc, ValueError):
                raise
            raise ValueError(
                "No se pudo despejar y explícitamente para aplicar la condición inicial; la solución implícita no se modificó."
            ) from exc
    return out


# ---------------------------------------------------------------------------
# Bernoulli  y' + P(x)y = Q(x)y^n
# ---------------------------------------------------------------------------
def bernoulli(equation, initial=None):
    """Resuelve ecuaciones de Bernoulli: y' + P(x)*y = Q(x)*y^n, n≠0,1."""
    match = re.fullmatch(r"\s*y'\s*=\s*(.+?)\s*", equation)
    if match:
        rhs = parse_expr(match.group(1))
    else:
        match2 = re.fullmatch(r"\s*y'\s*([+-].+?)\s*=\s*(.+?)\s*", equation)
        if not match2:
            raise ValueError("No se reconoce el formato para Bernoulli.")
        rhs = parse_expr(match2.group(2)) - parse_expr(match2.group(1))

    # Try to identify as y' = -P(x)*y + Q(x)*y^n
    # Collect by powers of y
    rhs_poly = sp.Poly(rhs, y) if rhs.is_polynomial(y) else None

    if rhs_poly is None:
        # Try partial fractions / collect manually
        try:
            rhs_expanded = sp.expand(rhs)
            rhs_poly = sp.Poly(rhs_expanded, y)
        except Exception:
            raise ValueError("La ecuación no tiene la forma de Bernoulli y' + P(x)y = Q(x)y^n.")

    terms = rhs_poly.terms()
    # Must have exactly 2 terms: one with y^1 (or y^0) and one with y^n
    nonconst_terms = [(mon[0], coef) for mon, coef in terms if mon[0] != 0]
    if len(nonconst_terms) != 2:
        raise ValueError("La ecuación no tiene exactamente dos potencias de y (Bernoulli requiere y^1 e y^n).")

    powers = sorted([t[0] for t in nonconst_terms])
    if powers[0] != 1:
        raise ValueError("La ecuación de Bernoulli requiere un término lineal en y.")
    n = powers[1]
    if n <= 1:
        raise ValueError("El exponente n de Bernoulli debe ser mayor que 1.")

    minus_P = rhs_poly.coeff_monomial(y)   # coefficient of y^1
    Q = rhs_poly.coeff_monomial(y ** n)    # coefficient of y^n

    if minus_P.has(y) or Q.has(y):
        raise ValueError("P(x) y Q(x) en Bernoulli deben depender solo de x.")

    P = -minus_P
    # Substitution: z = y^(1-n)  =>  z' + (1-n)*P(x)*z = (1-n)*Q(x)
    z = sp.Function("z")(x)
    alpha = 1 - n
    P_new = alpha * P
    Q_new = alpha * Q

    mu = sp.exp(sp.integrate(P_new, x))
    integral = sp.integrate(sp.simplify(mu * Q_new), x)
    z_general = sp.simplify((integral + C) / mu)
    y_general = sp.simplify(z_general ** sp.Rational(1, alpha))

    steps = [
        step("Identificación de Bernoulli",
             f"La ecuación tiene la forma y' + P(x)·y = Q(x)·y^n con n={n}.",
             equation, "Identificar P(x), Q(x) y n",
             sp.Tuple(sp.Symbol("P"), sp.Symbol("Q"), sp.Symbol("n"), P, Q, n),
             "Una ecuación de Bernoulli con n≠0,1 no es lineal pero se linealiza con z=y^(1-n)."),
        step("Sustitución z = y^(1-n)",
             f"Se define z = y^{alpha} para linealizar la ecuación.",
             y_general, f"z = y^{alpha}",
             sp.Eq(sp.Symbol("zprime") + P_new * sp.Symbol("z"), Q_new, evaluate=False),
             "Derivando z=y^(1-n) y dividiendo entre (1-n)·y^n se obtiene una EDO lineal en z."),
        step("Factor integrante para z",
             "Se resuelve la ecuación lineal en z con factor integrante.",
             P_new, "mu(x) = exp(∫(1-n)P dx)",
             mu,
             "Mismo procedimiento que para una lineal de primer orden."),
        step("Solución de z",
             "Se integra y se despeja z.",
             mu * Q_new, "Integrar y dividir entre mu",
             sp.Eq(sp.Symbol("z"), z_general, evaluate=False),
             "z satisface la EDO lineal reducida."),
        step("Regreso a y",
             f"Se invierte z = y^{alpha} para recuperar y.",
             z_general, f"y = z^(1/{alpha})",
             sp.Eq(y, y_general, evaluate=False),
             "La sustitución inversa restaura la variable original."),
    ]

    solution = y_general
    solution_kind = "general"

    if initial:
        x0_val = sp.sympify(initial["x0"])
        y0_val = sp.sympify(initial["y0"])
        eq_c = sp.Eq(y_general.subs(x, x0_val), y0_val)
        c_sols = sp.solve(eq_c, C)
        if not c_sols:
            raise ValueError("No se pudo calcular la constante con la condición inicial.")
        cv = sp.simplify(c_sols[0])
        solution = sp.simplify(y_general.subs(C, cv))
        solution_kind = "particular"
        steps.extend([
            step("Condición inicial",
                 f"Se sustituye x={x0_val}, y={y0_val} para hallar C.",
                 y_general, "Evaluar en la condición inicial",
                 sp.Eq(C, cv), "La condición inicial fija la constante de integración."),
            step("Solución particular",
                 "Se sustituye el valor de C.",
                 y_general, f"Sustituir C={cv}",
                 sp.Eq(y, solution), "La solución satisface la EDO y la condición inicial."),
        ])

    # Verification
    rhs_original = parse_expr(match.group(1)) if match else parse_expr(match2.group(2)) - parse_expr(match2.group(1))
    try:
        residual = sp.simplify(sp.diff(solution, x) - rhs_original.subs(y, solution))
        ver = "correcta" if residual == 0 or residual.is_zero is True else "indeterminada"
    except Exception:
        residual = sp.Symbol("?")
        ver = "indeterminada"

    out = result("bernoulli", "sustitucion_bernoulli", steps, solution, solution_kind, ver)
    out["verificacion"]["residuo"] = latex(residual)
    return out


# ---------------------------------------------------------------------------
# Segundo orden  (subconjunto autónomo reducible a Bernoulli)
# ---------------------------------------------------------------------------
def second_order(equation, initial):
    if initial is None or "yp0" not in initial:
        raise ValueError("Este método requiere x₀, y(x₀) y y′(x₀) para fijar las condiciones iniciales.")
    converted = equation.replace("y''", "x").replace("y'", "y")
    match = re.fullmatch(r"\s*(.+?)\s*=\s*(.+?)\s*", converted)
    if not match:
        raise ValueError("La ecuación de segundo orden no tiene el formato admitido.")
    residual_expr = sp.expand(parse_expr(match.group(1)) - parse_expr(match.group(2)))
    # Rationalize any floating-point coefficients so sp.Poly works reliably
    residual_expr = sp.nsimplify(residual_expr, rational=True)
    coefficient = sp.diff(residual_expr, x)
    if residual_expr.has(x ** 2) or coefficient.has(x) or coefficient.has(y) or coefficient == 0:
        raise ValueError("Solo se admite y''=R(y') autónoma, con R de tipo Bernoulli.")
    rate = sp.simplify(-residual_expr.subs(x, 0) / coefficient)
    if rate.has(x):
        raise ValueError("La ecuación reducida no es autónoma.")
    x0 = sp.sympify(initial["x0"] if initial else 0)
    yp0 = sp.sympify(initial["yp0"] if initial and "yp0" in initial else 1)
    y0 = sp.sympify(initial["y0"] if initial and "y0" in initial else 0)
    equilibria = sp.solve(sp.Eq(rate, 0), y)
    if sp.simplify(rate.subs(y, yp0)) == 0:
        p_solution = yp0
        y_solution = sp.simplify(y0 + yp0 * (x - x0))
        form = "equilibrio"
    else:
        poly = sp.Poly(rate, y)
        terms = poly.terms()
        linear_coeff = poly.coeff_monomial(y)
        nonlinear = [(mon[0], coef) for mon, coef in terms if mon[0] not in (0, 1)]
        const_coeff = poly.coeff_monomial(sp.Integer(1))
        # Accept: A*y + B*y^n  (const_coeff == 0)
        # Also accept: B*y^n alone (linear_coeff == 0, const_coeff == 0) for pure Bernoulli
        if len(nonlinear) != 1 or const_coeff != 0:
            raise ValueError("La ecuación reducida no coincide con Bernoulli p'+a(x)p=b(x)p^n.")
        n = nonlinear[0][0]
        b = nonlinear[0][1]
        if n < 2:
            raise ValueError("El exponente de Bernoulli debe ser mayor que uno.")
        z0 = yp0 ** (1 - n)
        lam = sp.simplify((1 - n) * linear_coeff)
        forcing = sp.simplify((1 - n) * b)
        if lam == 0:
            zsol = sp.simplify(z0 + forcing * (x - x0))
        else:
            zsol = sp.simplify((z0 + forcing / lam) * sp.exp(-lam * (x - x0)) - forcing / lam)
        p_solution = sp.simplify(zsol ** (sp.Rational(1, 1 - n)))
        y_solution = sp.simplify(y0 + sp.integrate(p_solution, (x, x0, x)))
        form = "bernoulli"
    residual_check = sp.simplify(sp.diff(p_solution, x) - rate.subs(y, p_solution))
    status = "correcta" if residual_check == 0 else "indeterminada"
    steps = [
        step("Reducción de orden", "Se define p=y'; entonces p'=y''.", equation,
             "Sustituir p=y'", sp.Eq(sp.Symbol("pprime"), rate),
             "No aparece y explícitamente, por lo que la ecuación se reduce a primer orden en p."),
        step("Ramas de equilibrio",
             "Se resuelve R(p)=0 para conservar las soluciones constantes.",
             rate, "Resolver R(p)=0", sp.FiniteSet(*equilibria),
             "Dividir por R(p) excluiría estas ramas."),
        step("Resolución reducida",
             "Se aplica la rama compatible con p(x₀)=y'(x₀).", rate,
             "Usar equilibrio o sustitución z=p^(1−n)", p_solution,
             "El cambio z convierte la ecuación de Bernoulli en lineal."),
        step("Recuperación de y", "Se integra p=y' y se aplica y(x₀)=y₀.", p_solution,
             "y=y₀+∫p dx", y_solution,
             "La condición inicial determina la constante aditiva."),
    ]
    out = result("segundo_orden_reducible_bernoulli", "sustitucion_p_yprime", steps, y_solution, "particular", status)
    out["orden"] = 2
    out["lineal"] = False
    out["solucion_yprima_latex"] = latex(p_solution)
    out["soluciones_equilibrio_p"] = [latex(e) for e in equilibria]
    out["rama_utilizada"] = form
    out["verificacion"]["residuo_ecuacion_reducida"] = latex(residual_check)
    out["verificacion"]["condicion_inicial_y"] = bool(sp.simplify(y_solution.subs(x, x0) - y0) == 0)
    out["verificacion"]["condicion_inicial_yprima"] = bool(sp.simplify(p_solution.subs(x, x0) - yp0) == 0)
    return out


# ---------------------------------------------------------------------------
# Clasificador
# ---------------------------------------------------------------------------
def classify(equation):
    s = normalize_equation(equation)
    if "dx" in s and "dy" in s:
        try:
            components = _exact_form_components(s)
            if components:
                M, N = components
                exact_condition = sp.simplify(sp.diff(M, y) - sp.diff(N, x)) == 0
                fam = ["exacta"] if exact_condition else []
                return {
                    "orden": 1,
                    "variable_independiente": "x",
                    "variable_dependiente": "y",
                    "lineal": False,
                    "familias_compatibles": fam,
                    "metodo_prioritario": "funcion_potencial" if fam else None,
                    "exacta": exact_condition,
                }
        except (ValueError, sp.PolynomialError, TypeError):
            pass
    if "'''" in s:
        return {
            "orden": 3,
            "variable_independiente": "x",
            "variable_dependiente": "y",
            "lineal": None,
            "familias_compatibles": [],
            "metodo_prioritario": None,
        }
    if "''" in s:
        info = {
            "orden": 2,
            "variable_independiente": "x",
            "variable_dependiente": "y",
            "lineal": None,
            "familias_compatibles": [],
            "metodo_prioritario": None,
        }
        try:
            converted = s.replace("y''", "x").replace("y'", "y")
            parts = re.fullmatch(r"\s*(.+?)\s*=\s*(.+?)\s*", converted)
            if not parts:
                return info
            residual = sp.expand(parse_expr(parts.group(1)) - parse_expr(parts.group(2)))
            coeff = sp.diff(residual, x)
            if coeff == 0 or coeff.has(x) or coeff.has(y) or residual.has(x ** 2):
                return info
            rate = sp.simplify(-residual.subs(x, 0) / coeff)
            poly = sp.Poly(rate, y)
            nonlinear = [m for m, c in poly.terms() if m[0] not in (0, 1) and c != 0]
            if len(nonlinear) == 1 and poly.coeff_monomial(sp.Integer(1)) == 0:
                info["familias_compatibles"] = ["segundo_orden_reducible_bernoulli"]
                info["metodo_prioritario"] = "sustitucion_p_yprime"
        except (ValueError, sp.PolynomialError, TypeError):
            pass
        return info
    if re.match(r"\s*y'\s*=", s):
        try:
            rhs_str = re.split(r"=", s, 1)[1]
            f = parse_expr(rhs_str)
            reduced = sp.simplify(f.subs(y, sp.Symbol("v") * x))
            fam = []
            homogeneous_ok = not reduced.has(x)
            linear_ok = sp.diff(f, y, 2) == 0 and not sp.diff(f, y).has(y)
            # Check separable
            separable_ok = False
            try:
                gx = sp.simplify(f.subs(y, 1))
                gy_cand = sp.simplify(f / gx) if gx != 0 else None
                if gy_cand is not None and not gy_cand.has(x) and sp.simplify(gx * gy_cand - f) == 0:
                    separable_ok = True
                else:
                    fx_cand = sp.simplify(f.subs(x, 1))
                    gx_cand2 = sp.simplify(f / fx_cand) if fx_cand != 0 else None
                    if gx_cand2 is not None and not gx_cand2.has(y) and sp.simplify(gx_cand2 * fx_cand - f) == 0:
                        separable_ok = True
            except Exception:
                pass
            # Check Bernoulli
            bernoulli_ok = False
            try:
                if f.is_polynomial(y):
                    rhs_poly = sp.Poly(f, y)
                    nct = [(mon[0], coef) for mon, coef in rhs_poly.terms() if mon[0] != 0]
                    if len(nct) == 2:
                        pwrs = sorted([t[0] for t in nct])
                        if pwrs[0] == 1 and pwrs[1] > 1:
                            Qb = rhs_poly.coeff_monomial(y ** pwrs[1])
                            Pb = rhs_poly.coeff_monomial(y)
                            if not Pb.has(y) and not Qb.has(y):
                                bernoulli_ok = True
            except Exception:
                pass
            if homogeneous_ok:
                fam.append("homogenea_primer_orden")
            if linear_ok:
                fam.append("lineal_primer_orden")
            if separable_ok and "lineal_primer_orden" not in fam:
                fam.append("separable")
            if bernoulli_ok:
                fam.append("bernoulli")
            return {
                "orden": 1,
                "variable_independiente": "x",
                "variable_dependiente": "y",
                "lineal": linear_ok,
                "familias_compatibles": fam,
                "metodo_prioritario": fam[0] if fam else None,
            }
        except Exception:
            pass
    match = re.fullmatch(r"\s*y'\s*([+-].+?)\s*=\s*(.+?)\s*", s)
    if match:
        try:
            lhs = parse_expr(match.group(1))
            q = parse_expr(match.group(2))
            p_coeff = sp.diff(lhs, y)
            is_linear = sp.simplify(lhs - p_coeff * y) == 0 and not p_coeff.has(y) and not q.has(y)
            # Check Bernoulli in y' + P*y = Q*y^n form
            bernoulli_ok = False
            try:
                rhs_full = q - lhs + p_coeff * y  # q - (lhs - p_coeff*y) expressed wrt p
                # Actually check if q is Q*y^n
                if q.is_polynomial(y) and lhs.is_polynomial(y):
                    q_poly = sp.Poly(q, y)
                    q_terms = q_poly.terms()
                    nonconst_q = [(mon[0], coef) for mon, coef in q_terms if mon[0] > 1]
                    if len(nonconst_q) == 1 and not q_poly.coeff_monomial(y):
                        bernoulli_ok = True
            except Exception:
                pass
            families = []
            if is_linear:
                families.append("lineal_primer_orden")
            if bernoulli_ok:
                families.append("bernoulli")
            return {
                "orden": 1,
                "variable_independiente": "x",
                "variable_dependiente": "y",
                "lineal": is_linear,
                "familias_compatibles": families,
                "metodo_prioritario": families[0] if families else None,
            }
        except ValueError:
            pass
    return {
        "orden": 1,
        "variable_independiente": "x",
        "variable_dependiente": "y",
        "lineal": None,
        "familias_compatibles": [],
        "metodo_prioritario": None,
    }


def _exact_form_components(equation):
    match = re.fullmatch(r"\s*(.+?)\s*=\s*(.+?)\s*", equation)
    if not match:
        return None
    expression = sp.expand(parse_expr(match.group(1)) - parse_expr(match.group(2)))
    polynomial = sp.Poly(expression, dx, dy)
    if any(sum(power) > 1 for power, coefficient in polynomial.terms()):
        return None
    M = sp.simplify(polynomial.coeff_monomial(dx))
    N = sp.simplify(polynomial.coeff_monomial(dy))
    constant = sp.simplify(polynomial.coeff_monomial(1))
    if constant != 0 or M.has(dx, dy) or N.has(dx, dy):
        return None
    if not (M.free_symbols | N.free_symbols).issubset({x, y}):
        return None
    if M == 0 or N == 0:
        return None
    return M, N


# ---------------------------------------------------------------------------
# Despachador principal
# ---------------------------------------------------------------------------
def solve(payload):
    mode = payload.get("modo", "automatico")
    if mode == "exacta" or payload.get("tipo") == "exacta":
        return exact(payload["M"], payload["N"])
    has_x0 = payload.get("x0") is not None
    has_y0 = payload.get("y0") is not None
    has_yp0 = payload.get("yp0") is not None
    if has_x0 != has_y0:
        raise ValueError("Completa ambos datos de la condición inicial: x0 e y(x0).")
    if has_yp0 and not (has_x0 and has_y0):
        raise ValueError("Para usar y'(x0), completa también x0 e y(x0).")
    initial = None
    if has_x0 and has_y0:
        initial = {
            "x0": parse_expr(str(payload["x0"])),
            "y0": parse_expr(str(payload["y0"])),
        }
    if has_yp0:
        initial["yp0"] = parse_expr(str(payload["yp0"]))

    eq = normalize_equation(payload.get("ecuacion", ""))

    # Exact differential form
    if "dx" in eq and "dy" in eq:
        components = _exact_form_components(eq)
        if components:
            return exact(*components)

    # Second order
    if "''" in eq:
        return second_order(eq, initial)

    # Forced modes
    if mode == "lineal":
        return linear(eq, initial)
    if mode == "homogenea":
        return homogeneous(eq, initial)
    if mode == "separable":
        return separable(eq, initial)
    if mode == "bernoulli":
        return bernoulli(eq, initial)

    # Automatic: form y' + P*y = Q (linear by pattern)
    if re.match(r"\s*y'\s*[+-]", eq):
        # Try linear first; if it fails, try Bernoulli
        try:
            return linear(eq, initial)
        except ValueError:
            pass
        try:
            return bernoulli(eq, initial)
        except ValueError:
            pass
        raise ValueError("No se pudo clasificar ni resolver la ecuación.")

    # Automatic: explicit y' = F(x,y)
    if re.match(r"\s*y'\s*=", eq):
        info = classify(eq)
        priority = info.get("metodo_prioritario")
        families = info.get("familias_compatibles", [])

        # Respect classifier order: use the first family in the list, not a
        # hardcoded precedence that ignores homogeneous-before-linear ordering.
        for family in families:
            if family == "homogenea_primer_orden":
                return homogeneous(eq, initial)
            if family == "lineal_primer_orden":
                return linear(eq, initial)
            if family == "bernoulli":
                return bernoulli(eq, initial)
            if family == "separable":
                return separable(eq, initial)

        # Last resort: try separable then homogeneous
        try:
            return separable(eq, initial)
        except ValueError:
            pass
        return homogeneous(eq, initial)

    raise ValueError("No se reconoció el tipo de ecuación. Usa el modo guiado para especificar el método.")
