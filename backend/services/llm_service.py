"""
Central Gemini (Google Generative AI) service.
"""
import os
import re
import json
from typing import Optional

_llm_instance = None
_init_error: Optional[str] = None


# ---------------------------------------------------------------------------
# Client management
# ---------------------------------------------------------------------------

def get_llm():
    """Lazy-init and cache the Gemini chat client. Returns None if unavailable."""
    global _llm_instance, _init_error

    if _llm_instance is not None:
        return _llm_instance
    if _init_error is not None:
        return None

    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key:
        _init_error = "GOOGLE_API_KEY not set in environment"
        print(f"[llm_service] {_init_error} — falling back to regex mode")
        return None

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        _llm_instance = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            google_api_key=api_key,
            convert_system_message_to_human=True,
        )
        print("[llm_service] Gemini client initialized ✅")
        return _llm_instance
    except Exception as e:
        _init_error = f"Could not initialize Gemini: {e}"
        print(f"[llm_service] {_init_error}")
        return None


def is_llm_available() -> bool:
    return get_llm() is not None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_json(text: str) -> str:
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(),
                  flags=re.MULTILINE).strip()


def _invoke(prompt: str) -> Optional[str]:
    """Send a single prompt to Gemini, return text or None on failure."""
    llm = get_llm()
    if llm is None:
        return None
    try:
        resp = llm.invoke(prompt)
        content = resp.content if hasattr(resp, "content") else resp

        # Newer Gemini models return a list of content blocks
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and "text" in block:
                    parts.append(block["text"])
                elif isinstance(block, str):
                    parts.append(block)
                else:
                    parts.append(str(block))
            content = "\n".join(parts)

        return str(content) if content is not None else None
    except Exception as e:
        print(f"[llm_service] Gemini call failed: {e}")
        return None


# ---------------------------------------------------------------------------
# 1. ANALYZER helper
# ---------------------------------------------------------------------------

def parse_question(question: str) -> Optional[dict]:
    system = (
        "You convert math questions into JSON. "
        "Return ONLY a JSON object with exactly these keys:\n"
        "  intent      — one of: arithmetic, algebra, calculus, statistics, percentage\n"
        "  operation   — one of: evaluate, solve, differentiate, integrate, "
        "factor, expand, simplify, percentage, statistics\n"
        "  expression  — a SymPy-parseable string, OR the raw numbers for percentages\n"
        "  variables   — list of single-letter variables present, e.g. [\"x\"]\n"
        "Rules:\n"
        "  - Always insert '*' between numbers and variables (2x → 2*x)\n"
        "  - Use '**' for powers (x^2 → x**2, x³ → x**3)\n"
        "  - Function names lowercase: sin, cos, tan, log, sqrt, exp\n"
        "  - Constants: pi, E\n"
        "  - For 'f(x) = ...' questions, return ONLY the right-hand side as expression\n"
        "  - For 'derivative of ...' questions, return ONLY the function, no '='\n"
        "  - PERCENTAGE QUESTIONS: set intent='percentage', operation='percentage', "
        "    and set expression to the two numbers separated by a space, e.g. '25 840'.\n"
        "  - No prose, no code fences, just JSON."
    )
    prompt = f"{system}\n\nQuestion: {question}"
    text = _invoke(prompt)
    if not text:
        return None
    try:
        data = json.loads(_clean_json(text))
        return data
    except Exception as e:
        print(f"[llm_service] parse_question JSON error: {e} | raw: {text[:200]}")
        return None


# ---------------------------------------------------------------------------
# 2. ROUTER helper
# ---------------------------------------------------------------------------

def choose_operation(question: str, candidates: list) -> Optional[str]:
    if not candidates:
        return None
    prompt = (
        "Pick the single best math operation for this question.\n"
        f"Question: {question}\n"
        f"Options: {candidates}\n"
        "Return ONLY the operation name, nothing else."
    )
    text = _invoke(prompt)
    if not text:
        return None
    choice = _clean_json(text).strip().lower()
    return choice if choice in candidates else None


# ---------------------------------------------------------------------------
# 3. SOLVER helper
# ---------------------------------------------------------------------------

def rewrite_expression_for_sympy(original: str, error: str) -> Optional[str]:
    prompt = (
        "You are a SymPy expression fixer. "
        "This expression failed to parse:\n"
        f"  {original}\n"
        f"Error: {error}\n\n"
        "Rewrite it as valid SymPy syntax. Rules:\n"
        "  - Use '*' between numbers and variables (2x → 2*x)\n"
        "  - Use '**' for powers (x^2 → x**2)\n"
        "  - Function names lowercase: sin, cos, tan, sqrt, log, exp\n"
        "  - Constants: pi, E\n"
        "  - Return ONLY the corrected expression, no quotes, no prose."
    )
    text = _invoke(prompt)
    if not text:
        return None
    fixed = _clean_json(text).strip().strip('"').strip("'")
    return fixed or None


# ---------------------------------------------------------------------------
# 4. VERIFIER helper
# ---------------------------------------------------------------------------

def verify_result(question: str, expression: str,
                  operation: str, result: str) -> Optional[dict]:
    prompt = (
        "You are a math verifier. Given the original question and the computed "
        "result, decide if the result is a plausible answer. Do NOT recompute; "
        "just sanity-check.\n\n"
        f"Question: {question}\n"
        f"Operation: {operation}\n"
        f"Expression: {expression}\n"
        f"Result: {result}\n\n"
        "Return ONLY a JSON object: "
        '{"ok": true|false, "note": "short reason (<= 20 words)"}'
    )
    text = _invoke(prompt)
    if not text:
        return None
    try:
        data = json.loads(_clean_json(text))
        if "ok" in data and "note" in data:
            return data
    except Exception as e:
        print(f"[llm_service] verify_result JSON error: {e}")
    return None


# ---------------------------------------------------------------------------
# 5. EXPLAINER helper
# ---------------------------------------------------------------------------

def narrate_steps(question: str, expression: str,
                  operation: str, result: str) -> Optional[list]:
    prompt = (
        "You are a math tutor. Write a short step-by-step explanation "
        "(2–4 steps) for this solved problem.\n\n"
        f"Question: {question}\n"
        f"Expression: {expression}\n"
        f"Operation: {operation}\n"
        f"Verified result: {result}\n\n"
        "Rules:\n"
        "  - Trust the given result completely. Do NOT recompute.\n"
        "  - Plain English.\n"
        "  - Return ONLY a JSON array of strings.\n"
        '  - Example: ["Identify the equation.", "Isolate x.", "x = 3."]'
    )
    text = _invoke(prompt)
    if not text:
        return None
    try:
        steps = json.loads(_clean_json(text))
        if isinstance(steps, list) and all(isinstance(s, str) for s in steps):
            return steps
    except Exception as e:
        print(f"[llm_service] narrate_steps JSON error: {e}")
    return None