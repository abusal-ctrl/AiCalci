"""
VERIFIER NODE
-------------
Sanity-checks the solver output. For now, just ensures we got something
and it's not an error string. You can extend this with symbolic
substitution checks later.
"""
from backend.graph.state import MathState


def verifier_node(state: MathState) -> MathState:
    if state.get("error"):
        state["verified"] = False
        state["verification_note"] = state["error"]
        return state

    raw = state.get("raw_result", "")
    if raw is None or raw == "":
        state["verified"] = False
        state["verification_note"] = "Empty result."
        return state

    state["verified"] = True
    state["verification_note"] = "Result produced by deterministic SymPy engine."
    return state