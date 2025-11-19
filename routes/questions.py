# routes/questions.py
from flask import Blueprint, request, jsonify
import mysql.connector
from utils.db import get_connection

questions_bp = Blueprint('questions', __name__)

@questions_bp.route('', methods=['GET'])
def list_questions():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM questions ORDER BY question_id DESC")
        return jsonify(cursor.fetchall())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@questions_bp.route('', methods=['POST'])
def add_question():
    data = request.get_json() or {}
    conn = cursor = None
    try:
        question_text = data.get('question_text')
        if not question_text:
            return jsonify({'error': 'question_text 为必填项'}), 400

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO questions (question_text, topic, difficulty_level, answer_text)
            VALUES (%s, %s, %s, %s)
        """,
            (
                question_text,
                data.get('topic'),
                data.get('difficulty_level', 'medium'),
                data.get('answer_text', '')
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
def update_question(question_id):
    data = request.get_json() or {}
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
        UPDATE questions
        SET question_text=%s, topic=%s, difficulty_level=%s, answer_text=%s
        WHERE question_id=%s
        """
        cursor.execute(
            sql,
            (
                data.get("question_text"),
                data.get("topic"),
                data.get("difficulty_level"),
                data.get("answer_text"),
                question_id
            )
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": f"未找到 question_id={question_id} 的记录"}), 404

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
def delete_question(question_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM questions WHERE question_id = %s", (question_id,))
        conn.commit()
        return jsonify({'message': '删除成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# routes/questions.py 添加：
@questions_bp.route("/topics", methods=["GET"])
def list_topics():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT topic FROM questions ORDER BY topic")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([r["topic"] for r in rows if r["topic"]])

@questions_bp.route("/count", methods=["GET"])
def count_questions():
    topic = request.args.get("topic")
    difficulty = request.args.get("difficulty_level")
    if not topic or not difficulty:
        return jsonify({"error": "缺少 topic 或 difficulty_level 参数"}), 400

    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) AS total FROM questions WHERE topic=%s AND difficulty_level=%s",
            (topic, difficulty)
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
