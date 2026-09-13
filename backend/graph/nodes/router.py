"""
ROUTER NODE
-----------
Decides which branch of the workflow to take. In this simple version, it
just validates the intent and prepares a routing key. In a bigger version,
you could use `add_conditional_edges` in the graph to actually branch.
"""
from backend.graph.state import MathState

VALID_INTENTS = {"arithmetic", "algebra", "calculus", "statistics", "percentage"}


def router_node(state: MathState) -> MathState:
    intent = state.get("intent", "arithmetic")
    if intent not in VALID_INTENTS:
        state["intent"] = "arithmetic"
    if not state.get("expression"):
        state["error"] = "Could not extract a mathematical expression."
    return state