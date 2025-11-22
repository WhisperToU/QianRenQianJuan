# 这个文件的意图识别是简单的关键词识别，开发阶段之后会改成更加智能的模式。

# 可扩展的 target→字段映射
MODEL_FIELDS = {
    "class": [
        "class_id",
        "class_name",
        "user_id",
        "school_id"
    ],
    "student": [
        "student_id",
        "class_id",
        "student_name",
        "user_id",
        "school_id"
    ],
    "question": [
        "question_id",
        "topic_id",
        "difficulty_level",
        "question_text",
        "question_image",
        "answer_text"
    ],
    "topic": [
        "id",
        "source_id",
        "name",
        "author_name",
        "student_description",
        "easy_description",
        "medium_description",
        "difficult_description",
        "group_id",
        "school_id"
    ],
    "source_question": [
        "id",
        "exam_type",
        "exam_year",
        "exam_region",
        "question_no",
        "question_stem",
        "answer",
        "group_id",
        "school_id"
    ],
    "assign": [
        "id",
        "student_id",
        "question_id",
        "position",
        "session_id",
        "assigned_at",
        "user_id",
        "school_id"
    ],
    "group": [
        "group_id",
        "group_name",
        "school_id"
    ],
    "user": [
        "id",
        "username",
        "password_hash",
        "is_new_user",
        "group_id",
        "role",
        "school_id"
    ]
}



def get_model_fields(target: str):
    return MODEL_FIELDS.get(target, [])


def detect_action(prompt: str):
    if any(w in prompt for w in ["新增", "添加", "创建"]):
        return "create"
    if any(w in prompt for w in ["修改", "更新"]):
        return "update"
    if any(w in prompt for w in ["删除", "移除"]):
        return "delete"
    if any(w in prompt for w in ["查看", "查一下", "显示"]):
        return "view"
    return None


def detect_target(prompt):
    mapping = {
        "班级": "class",
        "学生": "student",
        "题目": "question",
        "母题": "source_question",
        "专题": "topic",
        "分配": "assign",
        "组": "group",
        "用户": "user"
    }

    for word, target in mapping.items():
        if word in prompt:
            return target
    return None



def dispatch_intent(prompt: str):
    """
    返回结构：
    - mode: chat 或 crud
    - action: create/update/delete/view
    - target: student/class/topic...
    """

    action = detect_action(prompt)
    target = detect_target(prompt)

    if not action:
        return {"mode": "chat", "action": None, "target": None}

    return {"mode": "crud", "action": action, "target": target}
