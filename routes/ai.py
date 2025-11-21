from flask import Blueprint, request, jsonify
from utils.llm_client import chat
from utils.auth import auth_required

ai_bp = Blueprint('ai', __name__)


@ai_bp.route('/generate', methods=['POST'])
@auth_required
def generate():
    body = request.get_json() or {}
    prompt = body.get('prompt')
    if not prompt:
        return jsonify({'error': 'prompt is required'}), 400
    try:
        text = chat(prompt, system=body.get('system'), temperature=body.get('temperature', 0.3))
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
