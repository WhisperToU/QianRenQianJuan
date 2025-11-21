# routes/auth.py
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from utils.db import get_connection
from utils.auth import generate_token

auth_bp = Blueprint('auth', __name__)


def _fetch_user_by_username(username):
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, username, password_hash, role, is_new_user, created_at, school_id, group_id FROM users WHERE username=%s",
            (username,)
        )
        return cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = (data.get('identifier') or '').strip()
    password = data.get('password') or ''
    if not username or not password:
        return jsonify({'error': '用户名和密码均为必填'}), 400

    user = _fetch_user_by_username(username)
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': '账号或密码不正确'}), 401

    user_payload = {
        'id': user['id'],
        'username': user['username'],
        'role': user.get('role'),
        'is_new_user': bool(user.get('is_new_user')),
        'created_at': user.get('created_at').isoformat() if user.get('created_at') else None,
        'school_id': user.get('school_id'),
        'group_id': user.get('group_id'),
    }
    token = generate_token(user_payload)
    return jsonify({'user': user_payload, 'token': token})


def _get_or_create_school(conn, school_name):
    cursor = conn.cursor()
    cursor.execute("SELECT school_id FROM schools WHERE school_name=%s", (school_name,))
    row = cursor.fetchone()
    if row:
        cursor.close()
        return row[0]
    cursor.execute("INSERT INTO schools (school_name) VALUES (%s)", (school_name,))
    new_id = cursor.lastrowid
    cursor.close()
    return new_id


def _get_or_create_group(conn, group_name, school_id):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT group_id FROM subject_groups WHERE group_name=%s AND school_id=%s",
        (group_name, school_id)
    )
    row = cursor.fetchone()
    if row:
        cursor.close()
        return row[0]
    cursor.execute(
        "INSERT INTO subject_groups (group_name, school_id) VALUES (%s, %s)",
        (group_name, school_id)
    )
    new_id = cursor.lastrowid
    cursor.close()
    return new_id


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = (data.get('identifier') or '').strip()
    password = data.get('password') or ''
    school_name = (data.get('school_name') or '').strip()
    group_name = (data.get('group_name') or '').strip()
    if not username or not password:
        return jsonify({'error': '用户名和密码均为必填'}), 400
    if not school_name or not group_name:
        return jsonify({'error': '学校名称和教学组名称均为必填'}), 400

    existing = _fetch_user_by_username(username)
    if existing:
        return jsonify({'error': '用户名已存在'}), 409

    password_hash = generate_password_hash(password)

    conn = cursor = None
    try:
        conn = get_connection()
        school_id = _get_or_create_school(conn, school_name)
        group_id = _get_or_create_group(conn, group_name, school_id)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, is_new_user, school_id, group_id) VALUES (%s, %s, %s, %s, %s, %s)",
            (username, password_hash, 'teacher', 0, school_id, group_id)
        )
        conn.commit()
        new_id = cursor.lastrowid
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    user_payload = {
        'id': new_id,
        'username': username,
        'role': 'teacher',
        'is_new_user': False,
        'school_id': school_id,
        'group_id': group_id
    }
    token = generate_token(user_payload)
    return jsonify({'user': user_payload, 'token': token}), 201
