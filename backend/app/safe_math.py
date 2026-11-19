"""Small whitelist parser for mathematical expressions; never evaluates Python code."""
import ast
import re
import sympy as sp

x, y = sp.symbols("x y", real=True)
FUNCTIONS = {"sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "exp": sp.exp,
             "log": sp.log, "sqrt": sp.sqrt, "Abs": sp.Abs}
CONSTANTS = {"pi": sp.pi, "E": sp.E}


def parse_expr(source: str):
    if not isinstance(source, str) or not source.strip() or len(source) > 300:
        raise ValueError("La expresión está vacía o supera 300 caracteres.")
    text = latex_to_ascii(source.strip()).replace("^", "**")
    # MathLive omits the multiplication sign in forms such as 3y and 2(x+1).
    text = re.sub(r"(?<=[0-9])\s*(?=[xy(])", "*", text)
    text = re.sub(r"(?<=[xy)])\s*(?=[xy(])", "*", text)
    if not re.fullmatch(r"[A-Za-z0-9_+*/().,\-\s*]+", text):
        raise ValueError("La expresión contiene caracteres no permitidos.")
    try:
        tree = ast.parse(text, mode="eval")
    except (SyntaxError, ValueError):
        raise ValueError("No se pudo interpretar la expresión matemática.")

    def visit(node):
        if isinstance(node, ast.Expression): return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)): return sp.sympify(node.value)
        if isinstance(node, ast.Name):
            if node.id in {"x", "y"}: return {"x": x, "y": y}[node.id]
            if node.id in CONSTANTS: return CONSTANTS[node.id]
            raise ValueError(f"Símbolo no permitido: {node.id}")
        if isinstance(node, ast.BinOp) and type(node.op) in {ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow}:
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add): result = left + right
            elif isinstance(node.op, ast.Sub): result = left - right
            elif isinstance(node.op, ast.Mult): result = left * right
            elif isinstance(node.op, ast.Div): result = left / right
            else:
                if right.is_number and abs(float(right)) > 20: raise ValueError("Exponente fuera del límite permitido.")
                result = left ** right
            if sp.count_ops(result) > 300: raise ValueError("La expresión es demasiado compleja.")
            return result
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in FUNCTIONS and len(node.args) == 1 and not node.keywords:
            return FUNCTIONS[node.func.id](visit(node.args[0]))
        raise ValueError("Solo se permiten números, x, y, operaciones básicas y funciones matemáticas conocidas.")
    return visit(tree)


def latex_to_ascii(text: str) -> str:
    """Translate a small MathLive LaTeX subset to the whitelist grammar."""
    if "\\" not in text: return text
    text = text.replace("\\left", "").replace("\\right", "").replace("\\,", "").replace("\\!", "")
    text = text.replace("\\cdot", "*").replace("\\times", "*").replace("\\pi", "pi").replace("\\infty", "infty")
    text = text.replace("\\ln", "log").replace("\\sin", "sin").replace("\\cos", "cos").replace("\\tan", "tan").replace("\\exp", "exp")
    text = text.replace("\\operatorname{", "").replace("\\mathrm{", "")
    # Convert nested fractions from the inside out; unsupported syntax remains and is rejected.
    fraction = re.compile(r"\\frac\{([^{}]*)\}\{([^{}]*)\}")
    for _ in range(20):
        changed = fraction.sub(r"((\1)/(\2))", text)
        if changed == text: break
        text = changed
    root = re.compile(r"\\sqrt\{([^{}]*)\}")
    for _ in range(20):
        changed = root.sub(r"sqrt(\1)", text)
        if changed == text: break
        text = changed
    text = re.sub(r"\\(?:,|;|:| )", "", text)
    text = text.replace("{", "(").replace("}", ")")
    text = re.sub(r"\\(?:quad|qquad)", " ", text)
    return text


def parse_equation(source: str):
    if len(source) > 600: raise ValueError("La ecuación supera 600 caracteres.")
    match = re.fullmatch(r"\s*y'''?\s*=\s*(.+?)\s*", source)
    if match and "'''" not in source:
        raise ValueError("Las derivadas segunda se admiten únicamente en el formato y''+...=... del módulo Bernoulli.")
    match = re.fullmatch(r"\s*y'\s*=\s*(.+?)\s*", source)
    if match: return "first", parse_expr(match.group(1))
    match = re.fullmatch(r"\s*(.+?)\s*=\s*(.+?)\s*", source)
    if not match: raise ValueError("Use formatos como y'+3*y=9, y'=(2*x+y)/x o M*dx+N*dy=0.")
    left, right = parse_expr(match.group(1)), parse_expr(match.group(2))
    # Differential one-forms are represented by an explicitly selected exact mode.
    return "implicit", sp.simplify(left - right)


def latex(expr): return sp.latex(expr)
