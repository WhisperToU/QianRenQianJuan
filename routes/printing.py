# routes/printing.py
from flask import Blueprint, request, send_file, jsonify
from utils.db import get_connection
from utils.latex import latex_to_docx_file   # 根据你实际路径调整

printing_bp = Blueprint("printing", __name__)

@printing_bp.route("/exam", methods=["POST"])
def make_exam():
    data = request.get_json()
    ids = data.get("question_ids", [])
    if not ids:
        return jsonify({"error": "缺少题目ID"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = f"SELECT * FROM questions WHERE question_id IN ({','.join(['%s']*len(ids))})"
    cursor.execute(sql, ids)
    questions = cursor.fetchall()

    latex_str = ""
    for i, q in enumerate(questions, 1):
        latex_str += f"{i}. {q['question_text']}\n\n"

    docx_path = latex_to_docx_file(latex_str)
    return send_file(docx_path, as_attachment=True, download_name="exam.docx")


@printing_bp.route("/answers", methods=["POST"])
def make_answers():
    data = request.get_json()
    ids = data.get("question_ids", [])
    if not ids:
        return jsonify({"error": "缺少题目ID"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = f"SELECT * FROM questions WHERE question_id IN ({','.join(['%s']*len(ids))})"
    cursor.execute(sql, ids)
    questions = cursor.fetchall()

    latex_str = ""
    for i, q in enumerate(questions, 1):
        latex_str += f"{i}. {q['answer_text']}\n\n"

    docx_path = latex_to_docx_file(latex_str)
    return send_file(docx_path, as_attachment=True, download_name="answers.docx")
