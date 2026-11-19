import re
import sympy as sp
from .safe_math import x, y, parse_expr, latex

C = sp.symbols("C")

def step(title, explanation, before, operation, after, reason):
    return {"numero": 0, "titulo": title, "explicacion": explanation,
            "expresion_anterior": latex(before) if not isinstance(before, str) else before,
            "operacion": operation, "expresion_latex": latex(after) if not isinstance(after, str) else after,
            "justificacion": reason}

def result(kind, method, steps, solution, status="general", verification="indeterminada", domain=None):
    for i, item in enumerate(steps, 1): item["numero"] = i
    return {"tipo_ecuacion": kind, "metodo": method, "orden": 1 if kind != "exacta" else 1,
            "variable_independiente": "x", "variable_dependiente": "y", "lineal": kind == "lineal_primer_orden",
            "pasos": steps, "solucion": str(solution), "solucion_latex": latex(solution), "tipo_solucion": status,
            "verificacion": {"estado": verification, "residuo": None}, "restricciones_dominio": domain or []}

def linear(equation, initial=None):
    match = re.fullmatch(r"\s*y'\s*([+-].+?)\s*=\s*(.+?)\s*", equation)
    if match:
        left, q = parse_expr(match.group(1)), parse_expr(match.group(2))
        p = sp.diff(left, y)
        if left.has(y) and sp.simplify(left - p*y) != 0: raise ValueError("La ecuación no es lineal en y.")
    else:
        explicit=re.fullmatch(r"\s*y'\s*=\s*(.+?)\s*",equation)
        if not explicit: raise ValueError("La ecuación no coincide con y'+P(x)y=Q(x).")
        rhs=parse_expr(explicit.group(1)); p=-sp.diff(rhs,y); q=sp.simplify(rhs+p*y)
        if sp.diff(rhs,y,2)!=0: raise ValueError("La ecuación no es lineal en y.")
    if p.has(y) or q.has(y): raise ValueError("P y Q deben depender únicamente de x.")
    mu = sp.exp(sp.integrate(p, x))
    integral = sp.integrate(sp.simplify(mu*q), x)
    general = sp.simplify((integral+C)/mu)
    steps = [step("Coeficientes", "Se separan el coeficiente de y y el término independiente.", equation, "Identificar P(x), Q(x)", sp.Eq(sp.Symbol("P"), p), "La forma estándar es y'+Py=Q."),
             step("Factor integrante", "Se integra P(x) y se exponentia.", p, "μ(x)=exp(∫P(x)dx)", mu, "La regla del producto convierte la izquierda en una derivada exacta."),
             step("Multiplicación", "Se multiplica cada término por el factor integrante.", equation, "Multiplicar por μ(x)", sp.Eq(sp.Symbol("mu_yprime_plus"), sp.simplify(mu*q)), "μy' + μPy = μQ."),
             step("Derivada de producto", "El lado izquierdo coincide con la derivada de μy.", sp.Symbol("mu_yprime_plus"), "Reconocer d(μy)/dx", sp.Eq(sp.Derivative(mu*y,x), mu*q), "μ'=Pμ."),
             step("Integración", "Se integra ambos lados respecto de x.", mu*q, "Integrar", sp.Eq(mu*y, integral+C), "La integral indefinida incorpora una constante."),
             step("Despeje", "Se divide entre el factor integrante.", sp.Eq(mu*y, integral+C), "Despejar y", general, "μ(x) es exponencial y nunca nulo.")]
    solution, kind = general, "general"
    if initial:
        x0, y0 = sp.sympify(initial["x0"]), sp.sympify(initial["y0"])
        constant = sp.solve(sp.Eq(general.subs(x,x0), y0), C)
        if not constant: raise ValueError("No se pudo determinar la constante con la condición inicial.")
        solution = sp.simplify(general.subs(C, constant[0])); kind = "particular"
        steps.append(step("Condición inicial", f"Se aplica y({x0})={y0}.", general, "Sustituir x₀,y₀ y despejar C", solution, "La condición inicial fija la constante de integración."))
    residual = sp.simplify(sp.diff(solution,x)+p*solution-q)
    ver = "correcta" if residual == 0 else "fallida" if residual.is_zero is False else "indeterminada"
    out = result("lineal_primer_orden", "factor_integrante", steps, solution, kind, ver)
    out["verificacion"]["residuo"] = latex(residual)
    if initial: out["verificacion"]["condicion_inicial"] = bool(sp.simplify(solution.subs(x, initial["x0"])-initial["y0"]) == 0)
    return out

def exact(M_text, N_text):
    M,N = parse_expr(M_text),parse_expr(N_text)
    mx,ny=sp.diff(M,y),sp.diff(N,x)
    if sp.simplify(mx-ny)!=0: raise ValueError("La ecuación no es exacta: ∂M/∂y y ∂N/∂x difieren.")
    potential=sp.integrate(M,x)
    gprime=sp.simplify(N-sp.diff(potential,y)); g=sp.integrate(gprime,y)
    F=sp.simplify(potential+g)
    steps=[step("Componentes", "Se identifican M y N.", "M dx + N dy=0", "Separar coeficientes", sp.Eq(sp.Symbol("M"),M), "Son los coeficientes de dx y dy."),
            step("Prueba de exactitud", "Se comparan las derivadas parciales cruzadas.", "M,N", "Calcular M_y y N_x", sp.Eq(mx,ny), "La igualdad garantiza una función potencial local."),
            step("Integración de M", "Se integra M respecto de x, tratando y como constante.", M, "Integrar respecto a x", potential+sp.Function("g")(y), "La derivada en x recupera M."),
            step("Término complementario", "Se compara la derivada en y con N.", N, "Integrar N−∂F/∂y respecto a y", g, "El término independiente de x completa la función potencial."),
            step("Solución implícita", "La curva solución es un nivel de la función potencial.", F, "Igualar a constante", sp.Eq(F,C), "∇F=(M,N), así dF=Mdx+Ndy=0.")]
    out=result("exacta","funcion_potencial",steps,sp.Eq(F,C),"implícita","correcta")
    out["orden"]=1; out["lineal"]=False; out["verificacion"]["residuo"]=latex(sp.simplify(sp.diff(F,x)-M)+sp.simplify(sp.diff(F,y)-N))
    return out

def homogeneous(equation, initial=None):
    match=re.fullmatch(r"\s*y'\s*=\s*(.+?)\s*",equation)
    if not match: raise ValueError("Use la forma explícita y'=F(x,y).")
    f=parse_expr(match.group(1)); u=sp.symbols("v", real=True)
    reduced=sp.simplify(f.subs(y,u*x))
    if reduced.has(x): raise ValueError("El lado derecho no es homogéneo de grado cero F(y/x).")
    g=sp.simplify(reduced-u)
    if g == 0:
        family=sp.Eq(y,C*x)
        steps=[step("Prueba de homogeneidad", "Se sustituye y=vx y el lado derecho se reduce a v.", f, "Sustituir y=vx", reduced, "La expresión solo depende de v=y/x."),
               step("Rama de equilibrio", "La ecuación para v es xv'=0, así que v permanece constante.", sp.Eq(sp.Symbol("vprime"),g), "Integrar v'=0", family, "Esta familia se perdería al dividir por F(v)-v.")]
        out=result("homogenea_primer_orden","sustitucion_y_vx",steps,family,"general","correcta",["x≠0"])
        out["verificacion"]["residuo"]=latex(sp.simplify(sp.diff(C*x,x)-f.subs(y,C*x)))
        return out
    integral=sp.integrate(1/g,u)
    implicit=sp.Eq(integral,sp.log(sp.Abs(x))+C)
    steps=[step("Prueba de homogeneidad", "Se sustituye y=vx y se verifica que F(x,vx) no dependa de x.", f, "Sustituir y=vx", reduced, "La independencia de x confirma que F depende de y/x."),
           step("Sustitución", "Con y=vx, la derivada es y'=v+xv'.", "y=vx", "Derivar respecto a x", sp.Eq(sp.Symbol("yprime"),u+x*sp.Symbol("vprime")), "Regla del producto."),
           step("Separación", "Se resta v y se separan variables.", sp.Eq(sp.Symbol("yprime"),reduced), "x dv/dx=F(v)−v", sp.Eq(1/g*sp.Symbol("dv"),sp.Symbol("dx")/x), "Separación válida en intervalos donde F(v)−v no sea cero."),
           step("Integración", "Se integran ambos lados.", "dv/(F(v)-v)=dx/x", "Integrar", implicit, "La integral de 1/x es ln|x|."),
           step("Regreso a variables originales", "Se usa v=y/x.", implicit, "Sustituir v=y/x", sp.Eq(integral.subs(u,y/x),sp.log(sp.Abs(x))+C), "La sustitución inicial define v=y/x.")]
    out=result("homogenea_primer_orden","sustitucion_y_vx",steps,implicit,"general","indeterminada",["x≠0", "Las ramas constantes v donde F(v)-v=0 deben analizarse aparte."])
    equilibria=sp.solve(sp.Eq(g,0),u)
    out["soluciones_equilibrio_v"]=[latex(e) for e in equilibria]
    # Example y'=2+y/x has an elementary explicit family; retain implicit form if solve cannot invert.
    try:
        explicit=sp.solve(implicit.subs(u,y/x),y)
        if explicit:
            chosen=explicit[0]
            solution_type="general"
            if initial:
                x0,y0=sp.sympify(initial["x0"]),sp.sympify(initial["y0"])
                if sp.simplify(x0)==0:
                    raise ValueError("La condición inicial está en x=0, fuera del dominio de la sustitución y=vx.")
                constants=sp.solve(sp.Eq(chosen.subs(x,x0),y0),C)
                if not constants: raise ValueError("No se pudo determinar la constante con la condición inicial.")
                chosen=sp.simplify(chosen.subs(C,constants[0])); solution_type="particular"
            out["solucion"]=str(chosen); out["solucion_latex"]=latex(chosen); out["tipo_solucion"]=solution_type
            residual=sp.simplify(sp.diff(chosen,x)-f.subs(y,chosen))
            out["verificacion"]["residuo"]=latex(residual)
            out["verificacion"]["estado"]="correcta" if residual == 0 else "fallida" if residual.is_zero is False else "indeterminada"
            if initial: out["verificacion"]["condicion_inicial"]=bool(sp.simplify(chosen.subs(x,initial["x0"])-initial["y0"])==0)
    except Exception: pass
    return out

def classify(equation):
    s=equation.strip()
    if "y'''" in s:
        return {"orden":3,"variable_independiente":"x","variable_dependiente":"y","lineal":None,"familias_compatibles":[],"metodo_prioritario":None}
    if "y''" in s:
        info={"orden":2,"variable_independiente":"x","variable_dependiente":"y","lineal":None,"familias_compatibles":[],"metodo_prioritario":None}
        try:
            converted=s.replace("y''","x").replace("y'","y")
            parts=re.fullmatch(r"\s*(.+?)\s*=\s*(.+?)\s*",converted)
            if not parts: return info
            residual=sp.expand(parse_expr(parts.group(1))-parse_expr(parts.group(2)))
            coeff=sp.diff(residual,x)
            if coeff == 0 or coeff.has(x) or residual.has(x**2): return info
            rate=sp.simplify(-residual.subs(x,0)/coeff)
            poly=sp.Poly(rate,y)
            nonlinear=[m for m,c in poly.terms() if m[0] not in (0,1) and c != 0]
            if len(nonlinear)==1 and poly.coeff_monomial(1)==0:
                info["familias_compatibles"]=["segundo_orden_reducible_bernoulli"]
                info["metodo_prioritario"]="sustitucion_p_yprime"
        except (ValueError, sp.PolynomialError, TypeError): pass
        return info
    if re.match(r"\s*y'\s*=",s):
        try:
            f=parse_expr(re.split(r"=",s,1)[1]); reduced=sp.simplify(f.subs(y,sp.Symbol("v")*x))
            fam=[]
            homogeneous_ok=not reduced.has(x)
            linear_ok=sp.diff(f,y,2)==0 and not sp.diff(f,y).has(y)
            if homogeneous_ok: fam.append("homogenea_primer_orden")
            if linear_ok: fam.append("lineal_primer_orden")
            return {"orden":1,"variable_independiente":"x","variable_dependiente":"y","lineal":linear_ok,"familias_compatibles":fam,"metodo_prioritario":fam[0] if fam else None}
        except Exception: pass
    match=re.fullmatch(r"\s*y'\s*([+-].+?)\s*=\s*(.+?)\s*",s)
    if match:
        try:
            lhs,q=parse_expr(match.group(1)),parse_expr(match.group(2)); p=sp.diff(lhs,y)
            is_linear=(sp.simplify(lhs-p*y)==0 and not p.has(y) and not q.has(y))
            families=["lineal_primer_orden"] if is_linear else []
            return {"orden":1,"variable_independiente":"x","variable_dependiente":"y","lineal":is_linear,"familias_compatibles":families,"metodo_prioritario":families[0] if families else None}
        except ValueError: pass
    return {"orden":1,"variable_independiente":"x","variable_dependiente":"y","lineal":None,"familias_compatibles":[],"metodo_prioritario":None}

def second_order(equation, initial):
    # Supported subset: autonomous p'=A*p+B*p**n, with p=y'.
    if initial is None or "yp0" not in initial:
        raise ValueError("Este método requiere x₀, y(x₀) y y′(x₀) para fijar las condiciones iniciales.")
    converted=equation.replace("y''", "x").replace("y'", "y")
    match=re.fullmatch(r"\s*(.+?)\s*=\s*(.+?)\s*",converted)
    if not match: raise ValueError("La ecuación de segundo orden no tiene el formato admitido.")
    residual=sp.expand(parse_expr(match.group(1))-parse_expr(match.group(2)))
    coefficient=sp.diff(residual,x)
    if residual.has(x**2) or coefficient.has(x) or coefficient == 0:
        raise ValueError("Solo se admite y''=R(y') autónoma, con R de tipo Bernoulli.")
    rate=sp.simplify(-residual.subs(x,0)/coefficient)
    if rate.has(x): raise ValueError("La ecuación reducida no es autónoma.")
    x0=sp.sympify(initial["x0"] if initial else 0)
    yp0=sp.sympify(initial["yp0"] if initial and "yp0" in initial else 1)
    y0=sp.sympify(initial["y0"] if initial and "y0" in initial else 0)
    # Equilibria are retained explicitly, including the branch p=0.
    equilibria=sp.solve(sp.Eq(rate,0),y)
    if sp.simplify(rate.subs(y,yp0)) == 0:
        p_solution=yp0
        y_solution=sp.simplify(y0+yp0*(x-x0))
        form="equilibrio"
    else:
        poly=sp.Poly(rate,y)
        terms=poly.terms()
        linear_coeff=poly.coeff_monomial(y)
        nonlinear=[(mon[0],coef) for mon,coef in terms if mon[0] not in (0,1)]
        if len(nonlinear)!=1 or poly.coeff_monomial(1)!=0:
            raise ValueError("La ecuación reducida no coincide con Bernoulli p'+a(x)p=b(x)p^n en el subconjunto implementado.")
        n=nonlinear[0][0]; b=nonlinear[0][1]
        if n < 2: raise ValueError("El exponente de Bernoulli debe ser mayor que uno.")
        # z=p^(1-n); z'=(1-n)(A*z+B), solved as a linear first order ODE.
        z=sp.symbols("z")
        z0=yp0**(1-n)
        lam=sp.simplify((1-n)*linear_coeff)
        forcing=sp.simplify((1-n)*b)
        if lam == 0: zsol=sp.simplify(z0+forcing*(x-x0))
        else: zsol=sp.simplify((z0+forcing/lam)*sp.exp(-lam*(x-x0))-forcing/lam)
        p_solution=sp.simplify(zsol**(sp.Rational(1,1-n)))
        y_solution=sp.simplify(y0+sp.integrate(p_solution,(x,x0,x)))
        form="bernoulli"
    # Verify both initial data and reduced residual; original residual follows by construction.
    residual_check=sp.simplify(sp.diff(p_solution,x)-rate.subs(y,p_solution))
    status="correcta" if residual_check == 0 else "indeterminada"
    steps=[step("Reducción de orden", "Se define p=y'; entonces p'=y''.", equation, "Sustituir p=y'", sp.Eq(sp.Symbol("pprime"),rate), "No aparece y explícitamente, por lo que la ecuación se reduce a primer orden en p."),
           step("Ramas de equilibrio", "Se resuelve R(p)=0 para conservar las soluciones constantes de la ecuación reducida.", rate, "Resolver R(p)=0", sp.FiniteSet(*equilibria), "Dividir por R(p) excluiría estas ramas."),
           step("Resolución reducida", "Se aplica la rama compatible con p(x₀)=y'(x₀).", rate, "Usar equilibrio o sustitución z=p^(1−n)", p_solution, "El cambio z convierte la ecuación de Bernoulli en lineal."),
           step("Recuperación de y", "Se integra p=y' y se aplica y(x₀)=y₀.", p_solution, "y=y₀+∫p dx", y_solution, "La condición inicial determina la constante aditiva.")]
    out=result("segundo_orden_reducible_bernoulli","sustitucion_p_yprime",steps,y_solution,"particular",status)
    out["orden"]=2; out["lineal"]=False; out["solucion_yprima_latex"]=latex(p_solution)
    out["soluciones_equilibrio_p"]=[latex(e) for e in equilibria]; out["rama_utilizada"]=form
    out["verificacion"]["residuo_ecuacion_reducida"]=latex(residual_check)
    out["verificacion"]["condicion_inicial_y"]=bool(sp.simplify(y_solution.subs(x,x0)-y0)==0)
    out["verificacion"]["condicion_inicial_yprima"]=bool(sp.simplify(p_solution.subs(x,x0)-yp0)==0)
    return out

def solve(payload):
    mode=payload.get("modo","automatico")
    initial=None
    if payload.get("x0") is not None and payload.get("y0") is not None: initial={"x0":parse_expr(str(payload["x0"])),"y0":parse_expr(str(payload["y0"]))}
    if payload.get("yp0") is not None:
        initial=initial or {"x0":sp.Integer(0),"y0":sp.Integer(0)}
        initial["yp0"]=parse_expr(str(payload["yp0"]))
    if mode=="exacta" or payload.get("tipo") == "exacta": return exact(payload["M"],payload["N"])
    eq=payload.get("ecuacion","")
    eq=re.sub(r"y\s*\^\s*\{\\prime\\prime\}","y''",eq)
    eq=re.sub(r"y\s*\^\s*\{\\prime\}","y'",eq)
    if "y''" in eq: return second_order(eq,initial)
    if mode=="lineal" or payload.get("tipo")=="lineal_primer_orden" or re.match(r"\s*y'\s*[+-]",eq): return linear(eq,initial)
    if re.match(r"\s*y'\s*=",eq):
        found=classify(eq)
        if found["metodo_prioritario"]=="lineal_primer_orden": return linear(eq,initial)
    return homogeneous(eq,initial)
