"""
WORKFLOW
--------
LangGraph state machine that wires the nodes together:

    analyzer → router → solver → verifier → explainer → END
"""
from langgraph.graph import StateGraph, END

from backend.graph.state import MathState
from backend.graph.nodes.analyzer import analyzer_node
from backend.graph.nodes.router   import router_node
from backend.graph.nodes.solver   import solver_node
from backend.graph.nodes.verifier import verifier_node
from backend.graph.nodes.explainer import explainer_node


def build_graph():
    graph = StateGraph(MathState)

    graph.add_node("analyzer",  analyzer_node)
    graph.add_node("router",    router_node)
    graph.add_node("solver",    solver_node)
    graph.add_node("verifier",  verifier_node)
    graph.add_node("explainer", explainer_node)

    graph.set_entry_point("analyzer")
    graph.add_edge("analyzer",  "router")
    graph.add_edge("router",    "solver")
    graph.add_edge("solver",    "verifier")
    graph.add_edge("verifier",  "explainer")
    graph.add_edge("explainer", END)

    return graph.compile()


# Compile once at import time. If this line raises, one of your node
# files failed to import — scroll up to see the real error.
math_graph = build_graph()