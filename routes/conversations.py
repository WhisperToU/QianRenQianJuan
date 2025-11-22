from flask import Blueprint, request, jsonify, g

from utils.auth import auth_required
from utils.db import get_connection

conversations_bp = Blueprint('conversations', __name__)


def _fetch_user_conversation(cursor, user_id, conversation_id):
    cursor.execute(
        """
        SELECT conversation_id FROM conversations WHERE conversation_id=%s AND user_id=%s
    """,
        (conversation_id, user_id)
    )
    return cursor.fetchone()


def _build_conversation_row(record):
    return {
        'conversation_id': record['conversation_id'],
        'title': record['title'],
        'updated_at': record['updated_at'].isoformat() if record.get('updated_at') else None,
        'created_at': record['created_at'].isoformat() if record.get('created_at') else None,
        'school_id': record.get('school_id')
    }


@conversations_bp.route('/list', methods=['GET'])
@auth_required
def list_conversations():
    user_id = g.user.get('id')
    if not user_id:
        return jsonify({'error': '缺少用户 ID'}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT conversation_id, title, created_at, updated_at, school_id
            FROM conversations
            WHERE user_id=%s
            ORDER BY updated_at DESC
        """,
            (user_id,)
        )
        return jsonify([_build_conversation_row(row) for row in cursor.fetchall()])
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500
    finally:
        cursor.close()
        conn.close()


@conversations_bp.route('/', methods=['POST'])
@auth_required
def create_conversation():
    user_id = g.user.get('id')
    title = (request.json or {}).get('title') or '新对话'
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO conversations (user_id, title, school_id)
            VALUES (%s, %s, %s)
        """,
            (user_id, title, g.user.get('school_id'))
        )
        conn.commit()
        return jsonify({
            'conversation_id': cursor.lastrowid,
            'title': title,
            'updated_at': None
        }), 201
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500
    finally:
        cursor.close()
        conn.close()


@conversations_bp.route('/<int:conversation_id>', methods=['PUT'])
@auth_required
def update_conversation(conversation_id):
    payload = request.json or {}
    title = payload.get('title')
    if not title:
        return jsonify({'error': 'title is required'}), 400
    user_id = g.user.get('id')
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE conversations
            SET title=%s
            WHERE conversation_id=%s AND user_id=%s
        """,
            (title, conversation_id, user_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({'error': '会话不存在或无权限'}), 404
        return jsonify({'conversation_id': conversation_id, 'title': title})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500
    finally:
        cursor.close()
        conn.close()


@conversations_bp.route('/<int:conversation_id>', methods=['DELETE'])
@auth_required
def delete_conversation(conversation_id):
    user_id = g.user.get('id')
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM conversations WHERE conversation_id=%s AND user_id=%s",
            (conversation_id, user_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({'error': '会话不存在或无权限'}), 404
        return jsonify({'deleted': conversation_id})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500
    finally:
        cursor.close()
        conn.close()


@conversations_bp.route('/<int:conversation_id>/messages', methods=['POST'])
@auth_required
def add_message(conversation_id):
    payload = request.json or {}
    sender = payload.get('sender')
    content = payload.get('content')
    if not sender or not content:
        return jsonify({'error': 'sender 和 content 均为必填'}), 400
    user_id = g.user.get('id')
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        convo = _fetch_user_conversation(cursor, user_id, conversation_id)
        if not convo:
            return jsonify({'error': '会话不存在或无权限'}), 404
        cursor.execute(
            """
            INSERT INTO messages (conversation_id, sender, content)
            VALUES (%s, %s, %s)
        """,
            (conversation_id, sender, content)
        )
        conn.commit()
        return jsonify({'message_id': cursor.lastrowid, 'conversation_id': conversation_id}), 201
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500
    finally:
        cursor.close()
        conn.close()


@conversations_bp.route('/<int:conversation_id>/messages', methods=['GET'])
@auth_required
def list_messages(conversation_id):
    user_id = g.user.get('id')
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        convo = _fetch_user_conversation(cursor, user_id, conversation_id)
        if not convo:
            return jsonify({'error': '会话不存在或无权限'}), 404
        cursor.execute(
            """
            SELECT message_id, sender, content, timestamp
            FROM messages
            WHERE conversation_id=%s
            ORDER BY timestamp ASC
        """,
            (conversation_id,)
        )
        return jsonify(cursor.fetchall())
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500
    finally:
        cursor.close()
        conn.close()
