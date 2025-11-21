# routes/assign.py
from flask import Blueprint, request, jsonify, send_file, g
from utils.db import get_connection
from utils.auth import auth_required
from utils.latex import latex_to_docx_file
import random

assign_bp = Blueprint("assign", __name__)


# ------------------------------------------------------------
# 1）为一批学生随机分配一道题
# ------------------------------------------------------------
@assign_bp.route("/one", methods=["POST"])
@auth_required
def assign_one_question():
    data = request.get_json() or {}
    student_ids = data.get("student_ids", [])
    slots = data.get("slots", [])

    if not student_ids or not slots:
        return jsonify({"error": "缺少参数"}), 400
    school_id = g.user.get("school_id")
    group_id = g.user.get("group_id")
    if school_id is None or group_id is None:
        return jsonify({"error": "缺少 school_id 或 group_id"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # 校验学生归属当前学校
    placeholders = ",".join(["%s"] * len(student_ids))
    cursor.execute(
        f"SELECT student_id FROM students WHERE student_id IN ({placeholders}) AND school_id=%s",
        (*student_ids, school_id)
    )
    valid_students = {row["student_id"] for row in cursor.fetchall()}
    if len(valid_students) != len(set(student_ids)):
        cursor.close()
        conn.close()
        return jsonify({"error": "学生不存在或不属于当前学校"}), 400

    results = []
    question_cache = {}

    def fetch_pool(topic, topic_id, level):
        cursor.execute("""
            SELECT question_id FROM questions
            WHERE {} AND difficulty_level=%s AND group_id=%s
        """.format("topic_id=%s" if topic_id else "topic=%s"),
            (topic_id if topic_id else topic, level, group_id))
        pool = cursor.fetchall()
        if not pool:
            return []
        return [p["question_id"] for p in pool]

    for slot in slots:
        topic = slot.get("topic")
        topic_id = slot.get("topic_id")
        level = slot.get("difficulty_level")
        quantity = slot.get("quantity", 1)

        if not (topic or topic_id) or not level:
            cursor.close()
            conn.close()
            return jsonify({"error": "缺少参数"}), 400

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            quantity = 1

        if quantity < 1:
            quantity = 1

        key = (topic_id or topic, level)
        if key not in question_cache:
            question_cache[key] = fetch_pool(topic, topic_id, level)

        pool_ids = question_cache[key]
        if not pool_ids:
            cursor.close()
            conn.close()
            return jsonify({"error": "题库没有符合条件的题"}), 400

        for sid in student_ids:
            for _ in range(quantity):
                qid = random.choice(pool_ids)

                cursor.execute(
                    "SELECT COUNT(*) AS c FROM assigned_questions WHERE student_id=%s AND school_id=%s",
                    (sid, school_id)
                )
                pos = cursor.fetchone()["c"] + 1

                cursor.execute("""
                    INSERT INTO assigned_questions (student_id, question_id, position, school_id, user_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (sid, qid, pos, school_id, g.user.get("id")))

                results.append({
                    "student_id": sid,
                    "question_id": qid,
                    "position": pos
                })

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"assigned": results})

# 2）生成所有学生的总 DOCX（你问的第二步代码就在这里）
# ------------------------------------------------------------
@assign_bp.route("/final_docx", methods=["GET"])
@auth_required
def generate_final_docx():
    school_id = g.user.get("school_id")
    group_id = g.user.get("group_id")
    if school_id is None or group_id is None:
        return jsonify({"error": "缺少 school_id 或 group_id"}), 400
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.student_name, a.position, q.question_text
        FROM assigned_questions a
        JOIN students s ON a.student_id = s.student_id
        JOIN questions q ON a.question_id = q.question_id
        WHERE a.school_id=%s AND s.school_id=%s AND q.group_id=%s
        ORDER BY s.student_name, a.position
    """, (school_id, school_id, group_id))
    rows = cursor.fetchall()

    latex = ""
    currentName = None

    for row in rows:
        if row["student_name"] != currentName:
            currentName = row["student_name"]
            latex += f"\\section*{{{currentName}}}\n\n"

        latex += f"{row['position']}. {row['question_text']}\n\n"

    docx_path = latex_to_docx_file(latex)

    return send_file(docx_path, as_attachment=True, download_name="all_students.docx")
