# routes/students.py
from flask import Blueprint, jsonify, g, request
from utils.db import get_connection
from utils.auth import auth_required

students_bp = Blueprint("students", __name__)

@students_bp.route("/list", methods=["GET"])
@auth_required
def list_students():
    school_id = g.user.get("school_id")
    if school_id is None:
        return jsonify({"error": "缺少 school_id，无法过滤数据"}), 400
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT student_id, student_name FROM students WHERE school_id=%s ORDER BY student_name",
        (school_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

@students_bp.route("/by_class", methods=["GET"])
@auth_required
def list_by_class():
    from flask import request
    class_id = request.args.get("class_id")

    if not class_id:
        return jsonify({"error": "缺少 class_id"}), 400
    school_id = g.user.get("school_id")
    if school_id is None:
        return jsonify({"error": "缺少 school_id，无法过滤数据"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    # 确认班级归属当前学校
    cursor.execute("SELECT school_id FROM classes WHERE class_id=%s", (class_id,))
    cls = cursor.fetchone()
    if not cls or cls.get("school_id") != school_id:
        cursor.close()
        conn.close()
        return jsonify({"error": "班级不存在或不属于当前学校"}), 404
    cursor.execute("""
        SELECT student_id, student_name 
        FROM students 
        WHERE class_id=%s AND school_id=%s
        ORDER BY student_name
    """, (class_id, school_id))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)


@students_bp.route("/bulk", methods=["POST"])
@auth_required
def bulk_add_students():
    data = request.get_json() or {}
    class_id = data.get("class_id")
    students = data.get("students", [])
    if not class_id or not isinstance(students, list) or not students:
        return jsonify({"error": "class_id 和 students 必填"}), 400
    school_id = g.user.get("school_id")
    user_id = g.user.get("id")
    if school_id is None:
        return jsonify({"error": "缺少 school_id，无法创建学生"}), 400

    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # 校验班级归属
        cursor.execute("SELECT school_id FROM classes WHERE class_id=%s", (class_id,))
        cls = cursor.fetchone()
        if not cls or cls[0] != school_id:
            return jsonify({"error": "班级不存在或不属于当前学校"}), 404
        inserted = []
        for stu in students:
            name = (stu.get("name") or "").strip()
            if not name:
                continue
            cursor.execute(
                "INSERT INTO students (class_id, student_name, school_id, user_id) VALUES (%s, %s, %s, %s)",
                (class_id, name, school_id, user_id)
            )
            inserted.append({"id": cursor.lastrowid, "name": name, "class_id": class_id})
        conn.commit()
        if not inserted:
            return jsonify({"error": "没有有效的学生姓名"}), 400
        return jsonify({"students": inserted}), 201
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
@students_bp.route("/add", methods=["POST"])
@auth_required
def add_student():
    data = request.get_json() or {}
    class_id = data.get("class_id")
    name = (data.get("student_name") or "").strip()

    if not class_id or not name:
        return jsonify({"error": "class_id 和 student_name 必填"}), 400

    school_id = g.user.get("school_id")
    user_id = g.user.get("id")

    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # 校验班级归属
        cursor.execute("SELECT school_id FROM classes WHERE class_id=%s", (class_id,))
        cls = cursor.fetchone()
        if not cls or cls["school_id"] != school_id:
            return jsonify({"error": "班级不存在或不属于当前学校"}), 404

        cursor.execute(
            "INSERT INTO students (class_id, student_name, school_id, user_id) VALUES (%s, %s, %s, %s)",
            (class_id, name, school_id, user_id)
        )
        conn.commit()

        return jsonify({
            "student_id": cursor.lastrowid,
            "student_name": name,
            "class_id": class_id
        }), 201

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@students_bp.route("/delete", methods=["POST"])
@auth_required
def delete_student():
    data = request.get_json() or {}
    student_id = data.get("student_id")
    print("学生姓名ID:", student_id)

    if not student_id:
        return jsonify({"error": "student_id 必填"}), 400

    school_id = g.user.get("school_id")

    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # 检查学生是否属于当前学校
        cursor.execute(
            "SELECT school_id FROM students WHERE student_id=%s",
            (student_id,)
        )
        stu = cursor.fetchone()
        if not stu or stu["school_id"] != school_id:
            return jsonify({"error": "学生不存在或不属于当前学校"}), 404

        cursor.execute("DELETE FROM students WHERE student_id=%s", (student_id,))
        conn.commit()

        return jsonify({"success": True}), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

