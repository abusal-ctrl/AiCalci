"""
ANALYZER NODE
Gemini-first. Regex fallback if the API key is missing or the call fails.
"""
import re
from backend.graph.state import MathState
from backend.services.llm_service import parse_question


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Names that must NOT be split by the implicit-multiplication regex
KNOWN_FUNCTIONS = [
    "sin", "cos", "tan", "cot", "sec", "csc",
    "asin", "acos", "atan", "arcsin", "arccos", "arctan",
    "sinh", "cosh", "tanh",
    "log", "ln", "exp", "sqrt", "cbrt", "abs",
    "floor", "ceil", "sign", "factorial", "gamma",
]

# Unicode → ASCII for math symbols the user might paste
UNICODE_MAP = {
    "²": "**2", "³": "**3", "⁴": "**4", "⁵": "**5",
    "⁶": "**6", "⁷": "**7", "⁸": "**8", "⁹": "**9", "⁰": "**0",
    "¹": "**1",
    "√": "sqrt", "π": "pi", "×": "*", "÷": "/",
    "−": "-", "–": "-", "—": "-",
    "∞": "oo",
}

FILLER_WORDS = [
    "solve", "find", "the", "of", "what", "is", "calculate", "compute",
    "derivative", "differentiate", "differentiation", "d/dx", "dy/dx",
    "integral", "integrate", "integration", "antiderivative",
    "limit",
    "factor", "factorize", "factorise",
    "expand", "simplify",
    "for", "equals", "equation", "with", "respect", "to", "please",
    "value", "result", "roots", "root", "expression", "function",
    "given", "that",
]

WORD_TO_SYMBOL = {
    " plus ":            " + ",
    " minus ":           " - ",
    " times ":           " * ",
    " multiplied by ":   " * ",
    " divided by ":      " / ",
    " squared ":         "**2",
    " cubed ":           "**3",
    " equals ":          "=",
    " to the power of ": "**",
}

INTENT_KEYWORDS = {
    "calculus":   ["derivative", "differentiate", "d/dx", "dy/dx",
                   "integral", "integrate", "antiderivative", "limit"],
    "algebra":    ["solve", "factor", "factorize", "expand", "simplify",
                   "roots", "equation"],
    "statistics": ["mean", "median", "mode", "variance", "std", "standard deviation"],
    "percentage": ["percent", "%"],
    "arithmetic": ["+", "-", "*", "/", "**", "^"],
}


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

def _replace_unicode(text: str) -> str:
    for u, a in UNICODE_MAP.items():
        text = text.replace(u, a)
    return text


def _protect_functions(text: str):
    mapping = {}
    for i, fn in enumerate(KNOWN_FUNCTIONS):
        token = f"__FN{i}__"
        if f"{fn}(" in text:
            text = text.replace(f"{fn}(", f"{token}(")
            mapping[token] = fn
    return text, mapping


def _unprotect_functions(text: str, mapping: dict) -> str:
    for token, fn in mapping.items():
        text = text.replace(token, fn)
    return text


def _insert_implicit_multiplication(s: str) -> str:
    s = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", s)
    s = re.sub(r"(\d)\(", r"\1*(", s)
    s = re.sub(r"([a-zA-Z])\(", r"\1*(", s)
    s = re.sub(r"\)\(", r")*(", s)
    s = re.sub(r"\)([a-zA-Z0-9])", r")*\1", s)
    return s


def _strip_function_assignment(text: str) -> str:
    text = re.sub(r"\bd\s*/\s*d[a-z]\b", "", text)
    text = re.sub(r"^\s*[a-zA-Z]\s*\(\s*[a-zA-Z]\s*\)\s*=", "", text)
    text = re.sub(r"^\s*[a-zA-Z]\s*=", "", text)
    return text


def _normalize(text: str) -> str:
    text = text.lower()
    text = _replace_unicode(text)
    for w, s in WORD_TO_SYMBOL.items():
        text = text.replace(w, s)
    text = text.replace("^", "**")
    text = _strip_function_assignment(text)
    text, mapping = _protect_functions(text)
    text = _insert_implicit_multiplication(text)
    text = _unprotect_functions(text, mapping)
    return text


def _extract_expression(text: str) -> str:
    cleaned = re.sub(r"[^0-9a-zA-Z+\-*/^().=,\s]", " ", text)
    for filler in FILLER_WORDS:
        cleaned = re.sub(rf"\b{filler}\b", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    # If there's an '=', keep only the right side (the body of the equation)
    if "=" in cleaned:
        cleaned = cleaned.split("=", 1)[1].strip()
    return cleaned


# ---------------------------------------------------------------------------
# Regex fallback
# ---------------------------------------------------------------------------

def _regex_analyze(question: str) -> dict:
    normalized = _normalize(question)

    intent = "arithmetic"
    for category, keywords in INTENT_KEYWORDS.items():
        if any(kw in normalized for kw in keywords):
            intent = category
            break

    # ---- Operation detection ----
    # Percentage is checked FIRST because it uses a different code path.
    operation = "evaluate"
    if "%" in normalized or "percent" in normalized:
        operation = "percentage"
        intent = "percentage"
    elif "solve" in normalized or "root" in normalized:
        operation = "solve"
    elif ("derivative" in normalized or "differentiate" in normalized
          or "d/dx" in normalized or "dy/dx" in normalized):
        operation = "differentiate"
    elif ("integral" in normalized or "integrate" in normalized
          or "antiderivative" in normalized):
        operation = "integrate"
    elif "factor" in normalized:
        operation = "factor"
    elif "expand" in normalized:
        operation = "expand"
    elif "simplify" in normalized:
        operation = "simplify"
    elif intent == "statistics":
        operation = "statistics"

    expression = _extract_expression(normalized)

    # For percentage, keep the raw numbers in the expression field
    if operation == "percentage":
        nums = re.findall(r"\d+\.?\d*", normalized)
        expression = " ".join(nums)

    # Variable detection — exclude 'e' (Euler) and single letters inside function names
    variables = list(set(re.findall(r"\b([a-df-hj-z])\b", expression)))

    return {
        "intent":     intent,
        "operation":  operation,
        "expression": expression,
        "variables":  variables,
    }


# ---------------------------------------------------------------------------
# Node
# ---------------------------------------------------------------------------

def analyzer_node(state: MathState) -> MathState:
    question = state.get("question", "")

    # 1) Gemini
    llm_result = parse_question(question)
    source = "gemini" if llm_result else "regex"

    # 2) Regex fallback
    if not llm_result:
        llm_result = _regex_analyze(question)

    # 3) Clean up the expression regardless of source
    expr = llm_result.get("expression", "") or ""
    expr = _replace_unicode(expr)
    expr, mapping = _protect_functions(expr)
    expr = _insert_implicit_multiplication(expr)
    expr = _unprotect_functions(expr, mapping)

    # 4) Percentage safety net — ensure both numbers are in `expression`
    operation = llm_result.get("operation", "evaluate")
    intent = llm_result.get("intent", "arithmetic")
    if ("%" in question or "percent" in question.lower()
            or operation == "percentage" or intent == "percentage"):
        nums = re.findall(r"\d+\.?\d*", question)
        if len(nums) >= 2:
            operation = "percentage"
            intent = "percentage"
            expr = " ".join(nums[:2])

    state["intent"]        = intent
    state["operation"]     = operation
    state["expression"]    = expr
    state["variables"]     = llm_result.get("variables", [])
    state["parser_source"] = source
    return state