# routes/classes.py
from flask import Blueprint, jsonify, request, g
from utils.db import get_connection
from utils.auth import auth_required

classes_bp = Blueprint("classes", __name__)

@classes_bp.route("/list", methods=["GET"])
@auth_required
def list_classes():
    school_id = g.user.get("school_id")
    if school_id is None:
        return jsonify({"error": "缺少 school_id，无法过滤数据"}), 400
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT class_id, class_name FROM classes WHERE school_id=%s ORDER BY class_id",
        (school_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)


@classes_bp.route("/add", methods=["POST"])
@auth_required
def add_class():
    data = request.get_json() or {}
    class_name = (data.get("class_name") or "").strip()
    if not class_name:
        return jsonify({"error": "class_name 为必填项"}), 400
    school_id = g.user.get("school_id")
    user_id = g.user.get("id")
    if school_id is None:
        return jsonify({"error": "缺少 school_id，无法创建班级"}), 400

    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO classes (class_name, user_id, school_id) VALUES (%s, %s, %s)",
            (class_name, user_id, school_id)
        )
        conn.commit()
        new_id = cursor.lastrowid
        return jsonify({"class_id": new_id, "class_name": class_name, "school_id": school_id}), 201
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
