# services/chat_service.py
from services.ai_service import generate_secure_response


class ChatService:
    """
    专门负责聊天模式的业务逻辑
    """

    @staticmethod
    def chat(prompt: str) -> str:
        """
        调用安全（登录）模式下的聊天回应。
        """
        return generate_secure_response(prompt)
