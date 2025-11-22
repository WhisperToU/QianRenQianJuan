import json

from flask import Blueprint, request, jsonify

from routes.ai_service import generate_secure_response
from utils.auth import auth_required

ai_secure_bp = Blueprint("ai_secure", __name__)


@ai_secure_bp.route("/generate", methods=["POST"])
@auth_required
def generate_secure():
    body = request.get_json() or {}
    prompt = body.get("prompt")
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400
    try:
        text = generate_secure_response(
            prompt,
            temperature=body.get("temperature", 0.3),
        )
        try:
            payload = json.loads(text)
            return jsonify({"mode": "card", "data": payload})
        except json.JSONDecodeError:
            return jsonify({"mode": "chat", "text": text})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
