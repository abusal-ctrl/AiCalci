from typing import TypedDict, List, Optional, Any


class MathState(TypedDict, total=False):
    question: str
    intent: str
    operation: str
    expression: str
    variables: List[str]

    parser_source: str

    raw_result: Any
    solver_used_llm_fix: bool

    verified: bool
    verification_note: str

    steps: List[str]
    final_answer: str

    explainer_source: str

    error: Optional[str]