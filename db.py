import sqlite3
import os
from utils.auth import hash_password
import sqlite3
from database.engine import engine


# database/db.py

from .models import User, Story  # Relative import of User and Story

def get_connection():
    return sqlite3.connect("storytelling.db", check_same_thread=False)


# Ensure data directory exists
os.makedirs("data", exist_ok=True)

DB_PATH = "data/storyfusion.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            user_type TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            title TEXT,
            description TEXT,
            image_path TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, password, user_type):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)', 
              (username, hash_password(password), user_type))
    conn.commit()
    conn.close()

def get_user(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    return result

def get_user_type(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT user_type FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# database/db.py

from sqlalchemy.orm import sessionmaker
from .models import Story
from . import engine

Session = sessionmaker(bind=engine)
session = Session()

def add_story(username, title, content, image_url=None):
    """Adds a new story to the database."""
    try:
        # Assuming you have a User model with a relationship to stories
        user = session.query(User).filter_by(username=username).first()
        if user:
            new_story = Story(
                title=title,
                content=content,
                user_id=user.id,
                image_url=image_url  # Store the image URL
            )
            session.add(new_story)
            session.commit()
            return new_story
        else:
            return None
    except Exception as e:
        session.rollback()
        print(f"Error saving story: {e}")
        return None
    finally:
        session.close()


def get_user_stories(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM stories WHERE username = ?', (username,))
    results = c.fetchall()
    conn.close()
    return results

def get_all_stories():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM stories')
    results = c.fetchall()
    conn.close()
    return results

def delete_story(story_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM stories WHERE id = ?', (story_id,))
    conn.commit()
    conn.close()
