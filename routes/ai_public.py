from flask import Blueprint, request, jsonify

from routes.ai_service import generate_public_response

ai_public_bp = Blueprint("ai_public", __name__)


@ai_public_bp.route("/generate", methods=["POST"])
def generate_public():
    body = request.get_json() or {}
    prompt = body.get("prompt")
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400
    try:
        text = generate_public_response(
            prompt,
            temperature=body.get("temperature", 0.3),
        )
        return jsonify({"text": text})
    except Exception as exc:  # keep error visible for debugging
        return jsonify({"error": str(exc)}), 500
