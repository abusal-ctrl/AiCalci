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
    if not isinstance(expr, str):
        expr = str(expr)
    s = expr.strip()
    s = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", s)
    s = s.replace("^", "**")
    return s


def _format_number(n, sig=12):
    try:
        f = float(n)
    except Exception:
        return str(n)
    if f.is_integer() and abs(f) < 1e15:
        return str(int(f))
    return f"{f:.{sig}g}"


def calculate_tool(expression: str) -> str:
    expr = parse_expr(_clean(expression), transformations=TRANSFORMS)
    result = sp.N(expr, 15)
    if result.is_Integer:
        return str(int(result))
    if result.is_real:
        return _format_number(result)
    return str(result)