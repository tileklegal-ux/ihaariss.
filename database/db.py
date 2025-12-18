# database/db.py

import sqlite3
import time
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


def ensure_user_exists(user_id: int, username: str | None = None):
    with closing(get_connection()) as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()

        if row is None:
            cur.execute(
                "INSERT INTO users (user_id, username, role, premium_until) VALUES (?, ?, 'user', 0)",
                (user_id, username or ""),
            )
        else:
            if username:
                cur.execute(
                    "UPDATE users SET username = ? WHERE user_id = ?",
                    (username, user_id),
                )
        conn.commit()


def get_user_by_username(username: str):
    if not username:
        return None
    username = username.lstrip("@").strip()

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
        cur.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
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


def get_premium_until(user_id: int) -> int:
    with closing(get_connection()) as conn:
        cur = conn.cursor()
        cur.execute("SELECT premium_until FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return int(row[0]) if row and row[0] is not None else 0


def set_premium_until(user_id: int, premium_until: int):
    with closing(get_connection()) as conn:
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO users (user_id, premium_until)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET premium_until = excluded.premium_until
        """, (user_id, int(premium_until)))
        conn.commit()


def is_user_premium(user_id: int) -> bool:
    now = int(time.time())
    return get_premium_until(user_id) > now
