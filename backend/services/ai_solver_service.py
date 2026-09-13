"""
Bridges Flask routes to the LangGraph workflow.
"""
from backend.graph.workflow import math_graph


def solve_with_ai(question: str) -> dict:
    initial_state = {"question": question}
    final_state = math_graph.invoke(initial_state)

    return {
        "intent": final_state.get("intent"),
        "operation": final_state.get("operation"),
        "expression": final_state.get("expression"),
        "result": final_state.get("raw_result"),
        "verified": final_state.get("verified"),
        "verification_note": final_state.get("verification_note"),
        "steps": final_state.get("steps", []),
        "final_answer": final_state.get("final_answer"),
        "error": final_state.get("error"),
    }