import sqlite3
from contextlib import closing

DB_PATH = "database.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    with closing(get_connection()) as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            role TEXT DEFAULT 'user',
            premium_until INTEGER DEFAULT 0
        )
        """)
        conn.commit()


def get_user_by_username(username: str):
    with closing(get_connection()) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id, username, role, premium_until FROM users WHERE username = ?",
            (username,),
        )
        return cur.fetchone()


def get_user_role(user_id: int):
    with closing(get_connection()) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT role FROM users WHERE user_id = ?",
            (user_id,),
        )
        row = cur.fetchone()
        return row[0] if row else "user"


def set_user_role(user_id: int, role: str):
    with closing(get_connection()) as conn:
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO users (user_id, role)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET role = excluded.role
        """, (user_id, role))
        conn.commit()
