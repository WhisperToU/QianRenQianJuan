import json
from services.ai_service import generate_secure_response
from services.dispatcher import get_model_fields


class CrudService:
    """
    CRUD 业务：负责构建提示词 + 调 AI 生成 JSON 草稿 + 校验
    """

    @staticmethod
    def build_template(action, target, user_prompt):
        """
        构建给 AI 的提示词，让 AI 严格按照数据库字段生成 JSON
        """
        fields = get_model_fields(target)

        # 字段展示成列表行
        field_list = "\n".join([f"- {f}" for f in fields])

        return f"""
你是教学助手系统的 CRUD JSON 构造器。
现在用户想要进行数据库操作。

【操作类型】{action}
【对象类型】{target}

以下是 {target} 的合法字段（必须严格使用这些字段，不可发明新字段）：
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

请务必输出严格 JSON，不要写任何多余文本。
"""

    @staticmethod
    def handle(action, target, user_prompt):
        """
        CRUD 模式的入口函数
        """
        # 没识别到 target
        if not target:
            return {
                "action": action,
                "target": None,
                "fields": {},
                "message": "你想操作哪个对象？（班级/学生/题目/母题/专题/作业…）"
            }

        # 构建系统提示词
        template = CrudService.build_template(action, target, user_prompt)

        # 调用 LLM 生成 JSON
        raw = generate_secure_response(template)

        # 尝试解析 JSON
        try:
            data = json.loads(raw)
        except Exception:
            # AI 有时会输出自然语言或格式错误
            return {
                "action": action,
                "target": target,
                "fields": {},
                "message": "AI 输出格式不是合法 JSON，请你重新描述或更明确地给出字段。"
            }

        # 确保必要字段存在
        if "fields" not in data:
            data["fields"] = {}

        # 自动过滤掉数据库里不存在的字段
        legal_fields = get_model_fields(target)
        data["fields"] = {
            k: v for k, v in data["fields"].items() if k in legal_fields
        }

        # 如果没有 message 字段，自动补充
        if "message" not in data:
            data["message"] = "已生成字段草稿，请检查是否正确。"

        return data
