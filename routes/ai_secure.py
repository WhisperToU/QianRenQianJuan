from flask import Blueprint, request, jsonify
import logging

from utils.auth import auth_required

from services.dispatcher import dispatch_intent
from services.chat_service import ChatService
from services.crud_service import CrudService

LOGGER = logging.getLogger(__name__)

ai_secure_bp = Blueprint("ai_secure", __name__)


@ai_secure_bp.route("/generate", methods=["POST"])
@auth_required
def generate_secure():
    body = request.get_json() or {}
    prompt = body.get("prompt")
    if not prompt:
        return jsonify({"error": "prompt required"}), 400

    # 1. 先识别意图
    intent = dispatch_intent(prompt)

    try:
        # 2. 聊天模式
        if intent["mode"] == "chat":
            reply = ChatService.chat(prompt)
            return jsonify({"mode": "chat", "text": reply})

        # 3. CRUD 模式
        action = intent.get("action")
        target = intent.get("target")
        card = CrudService.handle(action, target, prompt)
        return jsonify({"mode": "card", "data": card})
    except RuntimeError as err:
        LOGGER.warning("AI secure generate failed: %s", err)
        return jsonify({"error": str(err)}), 502
    except Exception:  # pragma: no cover - unexpected
        LOGGER.exception("Unhandled error in ai_secure.generate")
        return jsonify({"error": "internal server error"}), 500
