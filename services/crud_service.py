import json
from services.ai_service import generate_secure_response
from services.dispatcher import get_model_fields


class CrudService:
    """
    CRUD 业务：负责构建 AI 提示词、解析 AI 输出，并把字段草稿转换成可交互卡片
    """

    @staticmethod
    def build_template(action, target, user_prompt):
        """
        构建 AI 提示词，让 AI 严格输出特定目标的字段 JSON
        """
        fields = get_model_fields(target)
        field_list = "\n".join([f"- {f}" for f in fields])
        return f"""
你是教学助手系统的 CRUD JSON 构造器。
现在用户想要进行数据库操作。

【操作类型】{action}
【对象类型】{target}

以下是 {target} 的合法字段（必须严格使用这些字段，不能发明新字段）：
{field_list}

【用户原文需求】
{user_prompt}

请你只返回 JSON，不要写解释，不要写自然语言。
格式如下：

{{
  "action": "{action}",
  "target": "{target}",
  "fields": {{
      // 在这里填入字段和值，例如：
      // "student_name": "张三",
      // "class_id": 3
  }},
  "message": "下一步的引导信息，例如：请确认字段是否正确"
}}

请务必严格输出合法 JSON，不要写任何多余文本。
"""

    @staticmethod
    def handle(action, target, user_prompt):
        """
        CRUD 模式处理：调用 LLM 构建 JSON，再封装成前端卡片预览
        """
        if not target:
            return {
                "action": action,
                "target": None,
                "fields": {},
                "message": "你想操作哪个对象？（班级/学生/题目/母题/专题/作业…）"
            }

        template = CrudService.build_template(action, target, user_prompt)
        raw = generate_secure_response(template)

        try:
            data = json.loads(raw)
        except Exception:
            return {
                "action": action,
                "target": target,
                "fields": {},
                "message": "AI 输出格式不是合法 JSON，请重新描述或补充字段。"
            }

        if "fields" not in data:
            data["fields"] = {}

        legal_fields = get_model_fields(target)
        data["fields"] = {k: v for k, v in data["fields"].items() if k in legal_fields}

        if "message" not in data:
            data["message"] = "已生成字段草稿，请检查是否正确。"

        return CrudService._attach_card_payload(target, data)

    @staticmethod
    def _attach_card_payload(target, data):
        if target == "question":
            payload = dict(data)
            payload.setdefault("questions", [CrudService._build_question_card(payload["fields"])])
            payload.setdefault("topicOptions", [])
            return payload
        return data

    @staticmethod
    def _build_question_card(fields):
        def pick_first(*keys):
            for key in keys:
                value = fields.get(key)
                if value not in (None, "", []):
                    return value
            return ""

        def normalize_difficulty(value):
            if not value:
                return "medium"
            text = str(value).lower()
            if "easy" in text or "简单" in text:
                return "easy"
            if any(term in text for term in ["hard", "difficult", "困难", "难"]):
                return "difficult"
            return "medium"

        return {
            "question": pick_first("question_text", "question", "content"),
            "answer": pick_first("answer_text", "answer"),
            "topic": pick_first("topic", "topic_name"),
            "topic_id": fields.get("topic_id"),
            "difficulty": normalize_difficulty(pick_first("difficulty_level", "difficulty")),
            "type": fields.get("type"),
            "duration": fields.get("duration"),
            "imageUrl": pick_first("question_image", "imageUrl"),
        }
