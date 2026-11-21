"""Small whitelist parser for mathematical expressions; never evaluates Python code."""
import ast
import math
import re
import sympy as sp

x, y = sp.symbols("x y", real=True)
dx, dy = sp.symbols("dx dy")
FUNCTIONS = {"sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "exp": sp.exp,
             "log": sp.log, "sqrt": sp.sqrt, "Abs": sp.Abs}
CONSTANTS = {"pi": sp.pi, "E": sp.E, "e": sp.E}


def parse_expr(source: str):
    if not isinstance(source, str) or not source.strip() or len(source) > 300:
        raise ValueError("La expresión está vacía o supera 300 caracteres.")
    text = latex_to_ascii(source.strip()).replace("^", "**")
    # MathLive omits the multiplication sign in forms such as 3y and 2(x+1).
    text = re.sub(r"(?<=[0-9])\s*(?=[xy(])", "*", text)
    text = re.sub(r"(?<=[xy)])\s*(?=[xy(])", "*", text)
    text = re.sub(r"(?<=[xy0-9)])\s*(?=d[xy]\b)", "*", text)
    if not re.fullmatch(r"[A-Za-z0-9_+*/().,\-\s*]+", text):
        raise ValueError("La expresión contiene caracteres no permitidos.")
    try:
        tree = ast.parse(text, mode="eval")
    except (SyntaxError, ValueError):
        raise ValueError("No se pudo interpretar la expresión matemática.")

    def visit(node):
        if isinstance(node, ast.Expression): return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            if isinstance(node.value, float) and not math.isfinite(node.value):
                raise ValueError("No se permiten valores numéricos infinitos o NaN.")
            return sp.sympify(node.value)
        if isinstance(node, ast.Name):
            if node.id in {"x", "y", "dx", "dy"}: return {"x": x, "y": y, "dx": dx, "dy": dy}[node.id]
            if node.id in CONSTANTS: return CONSTANTS[node.id]
            raise ValueError(f"Símbolo no permitido: {node.id}")
        if isinstance(node, ast.BinOp) and type(node.op) in {ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow}:
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add): result = left + right
            elif isinstance(node.op, ast.Sub): result = left - right
            elif isinstance(node.op, ast.Mult): result = left * right
            elif isinstance(node.op, ast.Div): result = left / right
            else:
                if right.is_number and (right > 20 or right < -20): raise ValueError("Exponente fuera del límite permitido.")
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
    """Translate a deliberately small, strict MathLive LaTeX subset.

    This is a syntax converter, not a TeX macro expander. Unknown commands,
    malformed groups, and unsupported constructs fail closed and the result
    is still parsed by the AST whitelist in :func:`parse_expr`.
    """
    if not isinstance(text, str):
        raise ValueError("La expresión matemática debe ser texto.")
    if len(text) > 600:
        raise ValueError("La expresión supera 600 caracteres.")

    # MathLive represents prime marks as a superscript group. Accept only the
    # supported first and second derivatives and preserve them for the ODE
    # classifier; arbitrary prime commands remain invalid.
    text = re.sub(r"\by\s*\^\s*\{\s*\\prime\s*\\prime\s*\}", "y''", text)
    text = re.sub(r"\by\s*\^\s*\{\s*\\prime\s*\}", "y'", text)
    text = re.sub(r"\by\s*\^\s*\\prime\b", "y'", text)

    allowed_commands = {
        "cdot": "*", "times": "*", "pi": "pi",
        "sin": "sin", "cos": "cos", "tan": "tan",
        "ln": "log", "log": "log", "exp": "exp",
    }
    spacing_commands = {",", ";", ":", "!", "quad", "qquad", "enspace", " "}

    def group_at(source: str, start: int) -> tuple[str, int]:
        if start >= len(source) or source[start] != "{":
            raise ValueError("Se esperaba un grupo entre llaves en la expresión.")
        depth = 1
        i = start + 1
        while i < len(source):
            if source[i] == "\\":
                i += 2
                continue
            if source[i] == "{": depth += 1
            elif source[i] == "}":
                depth -= 1
                if depth == 0:
                    return source[start + 1:i], i + 1
            i += 1
        raise ValueError("Las llaves de la expresión no están balanceadas.")

    def convert(source: str, depth: int = 0) -> str:
        if depth > 30:
            raise ValueError("La expresión tiene demasiados grupos anidados.")
        out: list[str] = []
        delimiters: list[str] = []
        i = 0
        while i < len(source):
            char = source[i]
            if char == "\\":
                i += 1
                if i >= len(source):
                    raise ValueError("Comando LaTeX incompleto.")
                if source[i].isalpha():
                    end = i + 1
                    while end < len(source) and source[end].isalpha(): end += 1
                    command = source[i:end]
                    i = end
                else:
                    command = source[i]
                    i += 1
                if command in spacing_commands:
                    continue
                if command == "left" or command == "right":
                    while i < len(source) and source[i].isspace(): i += 1
                    if i >= len(source) or source[i] not in "()[]|":
                        raise ValueError(f"Delimitador inválido para \\{command}.")
                    delimiter = source[i]
                    i += 1
                    if command == "left":
                        matching = {"(": ")", "[": "]", "|": "|"}[delimiter]
                        delimiters.append(matching)
                        out.append("Abs(" if delimiter == "|" else "(")
                    else:
                        if not delimiters or delimiters.pop() != delimiter:
                            raise ValueError("Los delimitadores \\left y \\right no coinciden.")
                        out.append(")")
                    continue
                if command == "frac":
                    numerator, i = group_at(source, i)
                    denominator, i = group_at(source, i)
                    out.append(f"(({convert(numerator, depth + 1)})/({convert(denominator, depth + 1)}))")
                    continue
                if command == "sqrt":
                    radicand, i = group_at(source, i)
                    out.append(f"sqrt({convert(radicand, depth + 1)})")
                    continue
                if command == "operatorname":
                    name, i = group_at(source, i)
                    name = name.strip()
                    if name not in {"sin", "cos", "tan", "log", "ln", "exp", "sqrt"}:
                        raise ValueError(f"Función no permitida: {name or 'vacía'}.")
                    out.append("log" if name == "ln" else name)
                    continue
                if command in allowed_commands:
                    function = allowed_commands[command]
                    out.append(function)
                    if function in {"sin", "cos", "tan", "log", "exp"}:
                        argument = i
                        while argument < len(source) and source[argument].isspace(): argument += 1
                        # MathLive can serialize an unparenthesized one-token
                        # function argument (for example ``\\sin x``).
                        if argument < len(source) and source[argument] in "xy":
                            out.append(f"({source[argument]})")
                            i = argument + 1
                    continue
                raise ValueError(f"Comando matemático no permitido: \\{command}.")
            elif char == "{":
                content, i = group_at(source, i)
                out.append(f"({convert(content, depth + 1)})")
            elif char == "}":
                raise ValueError("Las llaves de la expresión no están balanceadas.")
            elif char in "[]":
                out.append("(" if char == "[" else ")")
                i += 1
            else:
                if not (char.isalnum() or char.isspace() or char in "_+-*/^().,'="):
                    raise ValueError("La expresión contiene caracteres no permitidos.")
                out.append(char)
                i += 1
        if delimiters:
            raise ValueError("Falta un delimitador \\right en la expresión.")
        return "".join(out)

    converted = convert(text)
    # A left/right pair must have resulted in balanced parentheses; ordinary
    # AST parsing below validates the expression grammar and its operators.
    return converted


def normalize_equation(source: str) -> str:
    """Convert a MathLive equation to the backend's narrow ODE text format."""
    if not isinstance(source, str) or not source.strip() or len(source) > 600:
        raise ValueError("La ecuación está vacía o supera 600 caracteres.")
    normalized = latex_to_ascii(source.strip())
    if normalized.count("=") != 1:
        raise ValueError("La ecuación debe contener exactamente un signo igual.")
    if not re.fullmatch(r"[A-Za-z0-9_+*/().,\-^\s' =*]+", normalized):
        raise ValueError("La ecuación contiene caracteres no permitidos.")
    if "'''" in normalized:
        raise ValueError("Solo se admiten derivadas de primer y segundo orden.")
    depth = 0
    for char in normalized:
        if char == "(": depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0: raise ValueError("Los paréntesis de la ecuación no están balanceados.")
    if depth:
        raise ValueError("Los paréntesis de la ecuación no están balanceados.")
    return normalized


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
