"""
SOLVER NODE
-----------
Runs the correct SymPy tool based on `operation`.

If SymPy raises (malformed expression), we ask Gemini to rewrite the
expression and retry once. The math itself is always done by SymPy.
"""
import re
from backend.graph.state import MathState

from backend.tools.calculator_tool import calculate_tool
from backend.tools.algebra_tool import (
    solve_equation_tool, factor_tool, expand_tool, simplify_tool
)
from backend.tools.calculus_tool import differentiate_tool, integrate_tool
from backend.tools.statistics_tool import statistics_tool

from backend.services.llm_service import rewrite_expression_for_sympy


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt(x):
    """Compact number formatting — no trailing '.000000'."""
    try:
        f = float(x)
    except (TypeError, ValueError):
        return str(x)
    if f.is_integer() and abs(f) < 1e15:
        return str(int(f))
    return f"{f:.10g}"


def _guard_expression(expr: str) -> str:
    """Undo accidental 'f * (x)' from bad implicit multiplication."""
    if not isinstance(expr, str):
        return str(expr)
    expr = re.sub(r"\b([a-zA-Z])\s*\*\s*\(", r"\1(", expr)
    return expr


# ---------------------------------------------------------------------------
# Operation dispatcher
# ---------------------------------------------------------------------------

def _run_operation(operation: str, expression: str, variables: list, question: str):
    """Execute the correct SymPy tool. Raises on failure."""

    # ---- Percentage -------------------------------------------------------
    # Trigger on the operation, the intent, or the presence of '%'/'percent'
    q_lower = question.lower()
    if operation == "percentage" or "%" in question or "percent" in q_lower:
        # Prefer numbers from expression ('25 840'), fall back to question
        nums = re.findall(r"\d+\.?\d*", expression) or re.findall(r"\d+\.?\d*", question)
        if len(nums) >= 2:
            pct, total = float(nums[0]), float(nums[1])
            return _fmt((pct / 100) * total)
        raise ValueError(f"Percentage problem needs two numbers; found {nums}.")

    # ---- All other operations --------------------------------------------
    expression = _guard_expression(expression)

    if operation == "solve":
        var = variables[0] if variables else "x"
        return solve_equation_tool(expression, var)

    if operation == "factor":
        return factor_tool(expression)

    if operation == "expand":
        return expand_tool(expression)

    if operation == "simplify":
        return simplify_tool(expression)

    if operation == "differentiate":
        var = variables[0] if variables else "x"
        return differentiate_tool(expression, var)

    if operation == "integrate":
        var = variables[0] if variables else "x"
        return integrate_tool(expression, var)

    if operation == "statistics":
        return statistics_tool(expression)

    # default: arithmetic
    return calculate_tool(expression)


# ---------------------------------------------------------------------------
# Node
# ---------------------------------------------------------------------------

def solver_node(state: MathState) -> MathState:
    if state.get("error"):
        return state

    operation = state.get("operation", "evaluate")
    expression = state.get("expression", "")
    variables = state.get("variables", [])
    question = state.get("question", "")

    # ---- First attempt: SymPy directly ----
    try:
        state["raw_result"] = _run_operation(operation, expression, variables, question)
        state["solver_used_llm_fix"] = False
        return state
    except Exception as first_error:
        first_msg = str(first_error)

    # ---- Second attempt: ask Gemini to rewrite, then retry ----
    print(f"[solver] SymPy failed on '{expression}': {first_msg}")
    fixed = rewrite_expression_for_sympy(expression, first_msg)

    if fixed and fixed != expression:
        print(f"[solver] LLM rewrote expression → '{fixed}'")
        try:
            state["raw_result"] = _run_operation(operation, fixed, variables, question)
            state["expression"] = fixed
            state["solver_used_llm_fix"] = True
            return state
        except Exception as second_error:
            state["error"] = (
                f"Solver error after LLM rewrite: {second_error} "
                f"(original: {first_msg})"
            )
            return state

    state["error"] = f"Solver error: {first_msg}"
    return state