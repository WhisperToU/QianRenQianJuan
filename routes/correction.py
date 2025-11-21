# routes/correction.py
from flask import Blueprint, request, jsonify, g
from utils.db import get_connection
from utils.auth import auth_required

correction_bp = Blueprint('correction', __name__)

@correction_bp.route('/student_records', methods=['GET'])
@auth_required
def get_student_records():
    student_name = request.args.get('student_name')
    target_date = request.args.get('date')
    if not student_name:
        return jsonify({'error': '缺少学生姓名'}), 400
    school_id = g.user.get("school_id")
    group_id = g.user.get("group_id")
    if school_id is None or group_id is None:
        return jsonify({'error': '缺少 school_id 或 group_id，无法过滤数据'}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT student_id FROM students WHERE student_name = %s AND school_id=%s",
            (student_name, school_id)
        )
        student = cursor.fetchone()
        if not student:
            return jsonify({'error': '找不到该学生'}), 404

        query = """
            SELECT sr.record_id, sr.create_at, q.question_id, q.question_text, q.answer_text,
                   sr.student_answer, sr.performance_score, sr.student_feedback
            FROM student_records sr
            JOIN questions q ON sr.question_id = q.question_id
            WHERE sr.student_id = %s AND q.group_id=%s
        """
        params = [student['student_id'], group_id]
        if target_date:
            query += " AND DATE(sr.create_at) = %s"
            params.append(target_date)

        query += " ORDER BY sr.create_at"
        cursor.execute(query, params)
        return jsonify(cursor.fetchall())

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@correction_bp.route('/update_record/<int:record_id>', methods=['PUT'])
@auth_required
def update_record(record_id):
    data = request.get_json()
    try:
        school_id = g.user.get("school_id")
        if school_id is None:
            return jsonify({'error': '缺少 school_id，无法更新记录'}), 400
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sr.record_id
            FROM student_records sr
            JOIN students s ON sr.student_id = s.student_id
            WHERE sr.record_id = %s AND s.school_id=%s
        """, (record_id, school_id))
        if cursor.fetchone() is None:
            return jsonify({'error': '记录不存在或无权限'}), 404
        cursor.execute("""
            UPDATE student_records
            SET performance_score = %s, student_feedback = %s
            WHERE record_id = %s
        """, (data['performance_score'], data['student_feedback'], record_id))
        conn.commit()
        return jsonify({'message': '记录更新成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@correction_bp.route('/update_question/<int:question_id>', methods=['PUT'])
@auth_required
def update_question_content(question_id):
    data = request.get_json()
    try:
        group_id = g.user.get("group_id")
        if group_id is None:
            return jsonify({'error': '缺少 group_id，无法更新题目'}), 400
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE questions
            SET question_text = %s, answer_text = %s
            WHERE question_id = %s AND group_id=%s
        """, (data['question_text'], data['answer_text'], question_id, group_id))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({'error': '题目不存在或无权限'}), 404
        return jsonify({'message': '题目已更新'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
