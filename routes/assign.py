# routes/assign.py
from flask import Blueprint, request, jsonify, send_file
from utils.db import get_connection
from utils.latex import latex_to_docx_file
import random

assign_bp = Blueprint("assign", __name__)


# ------------------------------------------------------------
# 1）为一批学生随机分配一道题
# ------------------------------------------------------------
@assign_bp.route("/one", methods=["POST"])
def assign_one_question():
    data = request.get_json()
    student_ids = data.get("student_ids", [])
    topic = data.get("topic")
    level = data.get("difficulty_level")

    if not student_ids or not topic or not level:
        return jsonify({"error": "缺少参数"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # 查询题库
    cursor.execute("""
        SELECT question_id FROM questions
        WHERE topic=%s AND difficulty_level=%s
    """, (topic, level))
    pool = cursor.fetchall()

    if not pool:
        return jsonify({"error": "题库没有符合条件的题"}), 400

    pool_ids = [p["question_id"] for p in pool]

    results = []

    for sid in student_ids:
        qid = random.choice(pool_ids)

        # 它已经有多少题了？
        cursor.execute(
            "SELECT COUNT(*) AS c FROM assigned_questions WHERE student_id=%s",
            (sid,)
        )
        pos = cursor.fetchone()["c"] + 1

        cursor.execute("""
            INSERT INTO assigned_questions (student_id, question_id, position)
            VALUES (%s, %s, %s)
        """, (sid, qid, pos))

        results.append({
            "student_id": sid,
            "question_id": qid,
            "position": pos
        })

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"assigned": results})


# ------------------------------------------------------------
# 2）生成所有学生的总 DOCX（你问的第二步代码就在这里）
# ------------------------------------------------------------
@assign_bp.route("/final_docx", methods=["GET"])
def generate_final_docx():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.student_name, a.position, q.question_text
        FROM assigned_questions a
        JOIN students s ON a.student_id = s.student_id
        JOIN questions q ON a.question_id = q.question_id
        ORDER BY s.student_name, a.position
    """)
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
