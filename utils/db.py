# utils/db.py
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'teaching_assistant'
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)