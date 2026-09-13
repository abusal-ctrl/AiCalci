"""
Explicit LangChain @tool wrappers.
These are the tools a LangChain agent could call by name.
The math is still done by SymPy behind the scenes.
"""
from langchain_core.tools import tool
from backend.tools.calculator_tool import calculate_tool
from backend.tools.algebra_tool import solve_equation_tool, factor_tool, expand_tool, simplify_tool
from backend.tools.calculus_tool import differentiate_tool, integrate_tool
from backend.tools.statistics_tool import statistics_tool


@tool
def lc_calculate(expression: str) -> str:
    """Evaluate an arithmetic expression, e.g. '2 + 3 * 4' or '5*pi'."""
    return calculate_tool(expression)


@tool
def lc_solve(expression: str, variable: str = "x") -> str:
    """Solve an equation for a variable, e.g. 'x**2 + 5*x + 6 = 0'."""
    return solve_equation_tool(expression, variable)


@tool
def lc_factor(expression: str) -> str:
    """Factor a polynomial, e.g. 'x**2 - 7*x + 12'."""
    return factor_tool(expression)


@tool
def lc_expand(expression: str) -> str:
    """Expand products, e.g. '(x+1)*(x-2)'."""
    return expand_tool(expression)


@tool
def lc_simplify(expression: str) -> str:
    """Simplify an expression."""
    return simplify_tool(expression)


@tool
def lc_differentiate(expression: str, variable: str = "x") -> str:
    """Differentiate a function with respect to a variable."""
    return differentiate_tool(expression, variable)


@tool
def lc_integrate(expression: str, variable: str = "x") -> str:
    """Integrate a function with respect to a variable."""
    return integrate_tool(expression, variable)


@tool
def lc_statistics(numbers: str) -> str:
    """Compute mean/median/mode/stdev. Pass comma-separated numbers."""
    return statistics_tool(numbers)


# Registry — a LangChain agent could bind these to an LLM
ALL_TOOLS = [
    lc_calculate, lc_solve, lc_factor, lc_expand, lc_simplify,
    lc_differentiate, lc_integrate, lc_statistics,
]