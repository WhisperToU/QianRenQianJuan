# routes/questions.py
from flask import Blueprint, request, jsonify, g
import mysql.connector
from utils.db import get_connection
from utils.auth import auth_required

questions_bp = Blueprint('questions', __name__)


@questions_bp.route('', methods=['GET'])
@auth_required
def list_questions():
    group_id = g.user.get("group_id")
    if group_id is None:
        return jsonify({'error': '缺少 group_id，无法过滤数据'}), 400
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM questions WHERE group_id=%s ORDER BY question_id DESC", (group_id,))
        rows = cursor.fetchall()
        for row in rows:
            row['persisted'] = True
        return jsonify(rows)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@questions_bp.route('', methods=['POST'])
@auth_required
def add_question():
    data = request.get_json() or {}
    conn = cursor = None
    try:
        question_text = data.get('question_text')
        if not question_text:
            return jsonify({'error': 'question_text 为必填项'}), 400
        group_id = g.user.get("group_id")
        if group_id is None:
            return jsonify({'error': '缺少 group_id，无法创建题目'}), 400

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO questions (question_text, topic, topic_id, difficulty_level, answer_text, question_image, group_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
            (
                question_text,
                data.get('topic'),
                data.get('topic_id'),
                data.get('difficulty_level', 'medium'),
                data.get('answer_text', ''),
                data.get('question_image'),
                group_id
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
        return jsonify({'message': '添加成功', 'question_id': new_id}), 201
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@questions_bp.route('/<int:question_id>', methods=['PUT'])
@auth_required
def update_question(question_id):
    data = request.get_json() or {}
    conn = cursor = None
    try:
        group_id = g.user.get("group_id")
        if group_id is None:
            return jsonify({"error": "缺少 group_id，无法修改题目"}), 400
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
        UPDATE questions
        SET question_text=%s, topic=%s, topic_id=%s, difficulty_level=%s, answer_text=%s, question_image=%s
        WHERE question_id=%s AND group_id=%s
        """
        cursor.execute(
            sql,
            (
                data.get('question_text'),
                data.get('topic'),
                data.get('topic_id'),
                data.get('difficulty_level'),
                data.get('answer_text'),
                data.get('question_image'),
                question_id,
                group_id
            )
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": f"未找到 question_id={question_id} 的记录，或无权限"}), 404

        return jsonify({"message": "修改成功", "question_id": question_id})

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@questions_bp.route('/<int:question_id>', methods=['DELETE'])
@auth_required
def delete_question(question_id):
    group_id = g.user.get("group_id")
    if group_id is None:
        return jsonify({'error': '缺少 group_id，无法删除题目'}), 400
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM questions WHERE question_id = %s AND group_id=%s", (question_id, group_id))
        conn.commit()
        return jsonify({'message': '删除成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@questions_bp.route("/topics", methods=["GET"])
@auth_required
def list_topics():
    group_id = g.user.get("group_id")
    if group_id is None:
        return jsonify({"error": "缺少 group_id，无法过滤数据"}), 400
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT topic FROM questions WHERE group_id=%s ORDER BY topic", (group_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([r["topic"] for r in rows if r["topic"]])


@questions_bp.route("/count", methods=["GET"])
@auth_required
def count_questions():
    topic = request.args.get("topic")
    difficulty = request.args.get("difficulty_level")
    topic_id = request.args.get("topic_id")
    if not difficulty or (not topic and not topic_id):
        return jsonify({"error": "缺少 topic/topic_id 和 difficulty_level 参数"}), 400
    group_id = g.user.get("group_id")
    if group_id is None:
        return jsonify({"error": "缺少 group_id，无法统计"}), 400

    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if topic_id:
            cursor.execute(
                "SELECT COUNT(*) AS total FROM questions WHERE topic_id=%s AND difficulty_level=%s AND group_id=%s",
                (topic_id, difficulty, group_id)
            )
        else:
            cursor.execute(
                "SELECT COUNT(*) AS total FROM questions WHERE topic=%s AND difficulty_level=%s AND group_id=%s",
                (topic, difficulty, group_id)
            )
        row = cursor.fetchone()
        total = row[0] if row else 0
        return jsonify({"count": total})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
