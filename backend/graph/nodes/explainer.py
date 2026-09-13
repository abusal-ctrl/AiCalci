"""
EXPLAINER NODE
Gemini writes friendly steps. The FINAL ANSWER is always the SymPy result.
"""
import re
from backend.graph.state import MathState
from backend.services.llm_service import narrate_steps


def _pretty(expr: str) -> str:
    if not isinstance(expr, str):
        expr = str(expr)
    s = expr.replace("**", "^").replace("*", "·")
    s = re.sub(r"\bpi\b", "π", s)
    s = re.sub(r"\bE\b", "e", s)
    s = s.replace("sqrt", "√")
    s = re.sub(r"\s*·\s*", " · ", s)
    return s


def _fallback_steps(intent, operation, expr, result):
    if operation == "percentage":
        return [
            "**Step 1.** Interpret as a percentage problem.",
            "**Step 2.** Divide the percent by 100.",
            f"**Step 3.** Multiply by the total: **{result}**",
        ]
    if operation == "factor":
        return [f"**Step 1.** Expression: `{expr}`",
                "**Step 2.** Factor over the rationals.",
                f"**Step 3.** Factored form: **{result}**"]
    if operation == "solve":
        return [f"**Step 1.** Equation: `{expr}`",
                "**Step 2.** Apply SymPy's symbolic solver.",
                f"**Step 3.** Roots: **{result}**"]
    if operation == "differentiate":
        return [f"**Step 1.** Function: `f(x) = {expr}`",
                "**Step 2.** Differentiate with respect to x.",
                f"**Step 3.** Derivative: **{result}**"]
    if operation == "integrate":
        return [f"**Step 1.** Integrand: `{expr}`",
                "**Step 2.** Symbolic integration.",
                f"**Step 3.** Antiderivative: **{result} + C**"]
    if operation == "expand":
        return [f"**Step 1.** Expression: `{expr}`",
                "**Step 2.** Expand products.",
                f"**Step 3.** Expanded: **{result}**"]
    if operation == "simplify":
        return [f"**Step 1.** Expression: `{expr}`",
                "**Step 2.** Simplify.",
                f"**Step 3.** Result: **{result}**"]
    if intent == "statistics":
        return [f"**Step 1.** Data: `{expr}`",
                "**Step 2.** Compute descriptive stats.",
                f"**Step 3.** Result: **{result}**"]
    return [f"**Step 1.** Expression: `{expr}`",
            "**Step 2.** Evaluate with SymPy.",
            f"**Step 3.** Result: **{result}**"]


def explainer_node(state: MathState) -> MathState:
    if state.get("error"):
        state["steps"] = [f"❌ {state['error']}"]
        state["final_answer"] = "Could not solve."
        return state

    operation = state.get("operation", "evaluate")
    intent = state.get("intent", "arithmetic")
    expr = _pretty(state.get("expression", ""))
    result = _pretty(state.get("raw_result", ""))

    llm_steps = narrate_steps(
        question=state.get("question", ""),
        expression=expr,
        operation=operation,
        result=result,
    )

    if llm_steps:
        state["steps"] = llm_steps
        state["explainer_source"] = "gemini"
    else:
        state["steps"] = _fallback_steps(intent, operation, expr, result)
        state["explainer_source"] = "templates"

    state["final_answer"] = f"{result} + C" if operation == "integrate" else result
    return state