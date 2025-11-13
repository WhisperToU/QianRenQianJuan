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
    data = request.get_json()
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO questions (question_text, topic, difficulty_level, answer_text)
            VALUES (%s, %s, %s, %s)
        """, (data['question_text'], data['topic'], data['difficulty_level'], data.get('answer_text', '')))
        conn.commit()
        return jsonify({'message': '添加成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@questions_bp.route('/<int:question_id>', methods=['PUT'])
@questions_bp.route("/<int:question_id>", methods=["PUT"])
def update_question(question_id):
    try:
        data = request.json
        print("收到修改请求：", question_id, data)

        conn = get_connection()   # 从 db.py 获取新的连接
        cursor = conn.cursor()

        sql = """
        UPDATE questions
        SET question_text=%s, topic=%s, difficulty_level=%s, answer_text=%s
        WHERE question_id=%s
        """
        cursor.execute(sql, (
            data.get("question_text"),
            data.get("topic"),
            data.get("difficulty_level"),
            data.get("answer_text"),
            question_id
        ))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": f"未找到 question_id={question_id} 的记录"}), 404

        return jsonify({"message": "修改成功"})

    except Exception as e:
        print("更新错误：", e)
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
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
