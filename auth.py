# utils/auth.py

from utils.password import hash_password, verify_password
import sqlite3
from database.db import get_user
from database.db import get_connection


def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password, user_type FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result and verify_password(password, result[1]):
        return True, result[2], result[0]  # user_type, user_id
    return False, None, None


def signup_user(username, password, user_type):
    conn = sqlite3.connect("data/storyfusion.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)",
              (username, hash_password(password), user_type))  # Hashing password before storing
    conn.commit()
