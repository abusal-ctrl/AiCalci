from flask import Blueprint, request, jsonify
from backend.services.calculator_service import calculate
from backend.services.ai_solver_service import solve_with_ai
from backend.services.converter_service import convert

api_bp = Blueprint("api", __name__)


@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@api_bp.route("/calculate", methods=["POST"])
def calculate_endpoint():
    data = request.get_json() or {}
    expression = data.get("expression", "").strip()
    if not expression:
        return jsonify({"error": "No expression provided"}), 400
    try:
        return jsonify({"success": True, "result": calculate(expression)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@api_bp.route("/ai-solve", methods=["POST"])
def ai_solve_endpoint():
    data = request.get_json() or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "No question provided"}), 400
    try:
        result = solve_with_ai(question)
        return jsonify({"success": True, **result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/convert", methods=["POST"])
def convert_endpoint():
    data = request.get_json() or {}
    try:
        category = data["category"]
        value    = float(data["value"])
        frm      = data["from"]
        to       = data["to"]
        result   = convert(category, value, frm, to)
        # Format nicely
        if abs(result) >= 1e6 or (0 < abs(result) < 1e-4):
            formatted = f"{result:.6e}"
        else:
            formatted = f"{round(result, 6):g}"
        return jsonify({"success": True, "result": formatted})
    except KeyError as e:
        return jsonify({"success": False, "error": f"Missing field: {e}"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400