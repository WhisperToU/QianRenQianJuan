# routes/classes.py
from flask import Blueprint, jsonify
from utils.db import get_connection

classes_bp = Blueprint("classes", __name__)

@classes_bp.route("/list", methods=["GET"])
def list_classes():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT class_id, class_name FROM classes ORDER BY class_id")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)
