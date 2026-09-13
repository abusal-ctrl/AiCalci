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
    s = re.sub(r"^\s*[a-zA-Z]\s*\(\s*[a-zA-Z]\s*\)\s*=\s*", "", s)
    s = re.sub(r"^\s*[a-zA-Z]\s*=\s*", "", s)
    s = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", s)
    return s


def _parse(expr: str):
    return parse_expr(_clean(expr), transformations=TRANSFORMS)


def _parse_eq(expression: str):
    """Handle 'lhs = rhs' or a single expression (= 0)."""
    if "=" in expression:
        left, right = expression.split("=", 1)
        return sp.Eq(_parse(left), _parse(right))
    return sp.Eq(_parse(expression), 0)


def solve_equation_tool(expression: str, variable: str = "x") -> str:
    var = sp.Symbol(variable)
    eq = _parse_eq(expression)
    solutions = sp.solve(eq, var)
    return ", ".join(f"{variable} = {s}" for s in solutions)


def factor_tool(expression: str) -> str:
    return str(sp.factor(_parse(expression)))


def expand_tool(expression: str) -> str:
    return str(sp.expand(_parse(expression)))


def simplify_tool(expression: str) -> str:
    return str(sp.simplify(_parse(expression)))