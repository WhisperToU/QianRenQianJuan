# utils/auth.py
# 简单的 JWT（HS256）生成与校验工具，减少外部依赖。
# 使用说明：
#   from utils.auth import generate_token, auth_required
#   token = generate_token({'id': user_id, 'username': 'xxx'})
#   @auth_required
#   def protected_route(): ...

import base64
import hashlib
import hmac
import json
import os
import time
from functools import wraps
from flask import request, jsonify, g


# 2 小时有效期
DEFAULT_EXP_SECONDS = 2 * 3600
SECRET_KEY = os.environ.get("JWT_SECRET", "please_change_me")


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def generate_token(payload: dict, exp_seconds: int = DEFAULT_EXP_SECONDS) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    body = {**payload, "iat": now, "exp": now + exp_seconds}

    h_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    b_b64 = _b64url_encode(json.dumps(body, separators=(",", ":")).encode())
    signing_input = f"{h_b64}.{b_b64}".encode()
    signature = hmac.new(SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
    s_b64 = _b64url_encode(signature)
    return f"{h_b64}.{b_b64}.{s_b64}"


def verify_token(token: str) -> dict:
    try:
        h_b64, b_b64, s_b64 = token.split(".")
    except ValueError:
        raise ValueError("token 格式错误")

    signing_input = f"{h_b64}.{b_b64}".encode()
    expected_sig = hmac.new(SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(expected_sig, _b64url_decode(s_b64)):
        raise ValueError("token 签名无效")

    body = json.loads(_b64url_decode(b_b64))
    now = int(time.time())
    if body.get("exp") and now > body["exp"]:
        raise ValueError("token 已过期")
    return body


def auth_required(func):
    """路由装饰器：要求 Authorization: Bearer <token>，解析后将用户信息放到 g.user"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "未授权"}), 401
        token = auth_header.split(" ", 1)[1].strip()
        try:
            user_payload = verify_token(token)
        except Exception as e:
            return jsonify({"error": f"未授权: {e}"}), 401
        g.user = user_payload
        return func(*args, **kwargs)

    return wrapper
