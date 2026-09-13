import re
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor,
)

TRANSFORMS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)


def _clean(expr: str) -> str:
    """Repair common malformations before SymPy sees them."""
    if not isinstance(expr, str):
        expr = str(expr)

    # 1. Remove any leading/trailing whitespace
    s = expr.strip()

    # 2. Strip function-assignment prefixes: 'f(x) =', 'y =', 'g(x) ='
    s = re.sub(r"^\s*[a-zA-Z]\s*\(\s*[a-zA-Z]\s*\)\s*=\s*", "", s)
    s = re.sub(r"^\s*[a-zA-Z]\s*=\s*", "", s)

    # 3. Remove any stray 'd/dx', 'dy/dx' tokens
    s = re.sub(r"\bd\s*/\s*d[a-z]\b", "", s)

    # 4. Ensure every function name has parentheses after it.
    #    If 'sin' appears without '(' and isn't followed by a letter, add '()'
    for fn in ["sin", "cos", "tan", "cot", "sec", "csc",
               "log", "ln", "exp", "sqrt", "abs"]:
        # sin without ( and not part of a longer word
        s = re.sub(rf"\b{fn}\b(?!\s*\()", f"{fn}(", s)

    # 5. If we accidentally created an unbalanced '(' above, balance it
    if s.count("(") > s.count(")"):
        s += ")" * (s.count("(") - s.count(")"))

    # 6. Insert '*' between digit and letter: '2x' -> '2*x'
    s = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", s)

    # 7. Fix double operators introduced by mistake
    s = re.sub(r"\*\*+", "**", s)
    s = re.sub(r"\*\+", "*", s)

    return s


def _parse(expr: str):
    """Parse with implicit multiplication enabled — safer than sympify alone."""
    return parse_expr(_clean(expr), transformations=TRANSFORMS)


def differentiate_tool(expression: str, variable: str = "x") -> str:
    var = sp.Symbol(variable)
    expr = _parse(expression)
    return str(sp.diff(expr, var))


def integrate_tool(expression: str, variable: str = "x") -> str:
    var = sp.Symbol(variable)
    expr = _parse(expression)
    return str(sp.integrate(expr, var))


def limit_tool(expression: str, variable: str = "x", point: str = "0") -> str:
    var = sp.Symbol(variable)
    expr = _parse(expression)
    pt = sp.sympify(point)
    return str(sp.limit(expr, var, pt))