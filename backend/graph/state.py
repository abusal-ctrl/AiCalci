"""
The State is the shared memory that travels through the LangGraph workflow.
Every node reads from it and writes back to it.
"""
from typing import TypedDict, Optional, List, Any


class MathState(TypedDict, total=False):
    # Input
    question: str
    
    # Analyzer output
    intent: str              # "arithmetic" | "algebra" | "calculus" | "statistics" | "percentage"
    operation: str           # "solve" | "differentiate" | "integrate" | "evaluate" | "simplify"
    expression: str          # extracted math expression, e.g. "x**2 + 5*x + 6"
    variables: List[str]     # e.g. ["x"]
    
    # Solver output
    raw_result: Any          # SymPy result serialized to string
    
    # Verifier output
    verified: bool
    verification_note: str
    
    # Explainer output
    steps: List[str]
    final_answer: str
    
    # Error handling
    error: Optional[str]