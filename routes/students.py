# routes/students.py
from flask import Blueprint, jsonify
from utils.db import get_connection

students_bp = Blueprint("students", __name__)

@students_bp.route("/list", methods=["GET"])
def list_students():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT student_id, student_name FROM students ORDER BY student_name")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

@students_bp.route("/by_class", methods=["GET"])
def list_by_class():
    from flask import request
    class_id = request.args.get("class_id")

    if not class_id:
        return jsonify({"error": "缺少 class_id"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT student_id, student_name 
        FROM students 
        WHERE class_id=%s 
        ORDER BY student_name
    """, (class_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)
