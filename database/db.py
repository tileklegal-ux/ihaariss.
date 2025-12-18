# database/db.py
import os
import time
from contextlib import closing

# Optional Postgres (Railway). Falls back to SQLite if psycopg2 is not installed or DATABASE_URL not set.
try:
    import psycopg2  # type: ignore
    import psycopg2.extras  # type: ignore
except Exception:
    psycopg2 = None  # type: ignore

import sqlite3

DB_PATH = "database.db"
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

_IS_PG = bool(DATABASE_URL) and psycopg2 is not None
_PARAM = "%s" if _IS_PG else "?"


def get_connection():
    if _IS_PG:
        return psycopg2.connect(DATABASE_URL, sslmode="require")
    return sqlite3.connect(DB_PATH)


def _execute(cur, query: str, params: tuple = ()):
    # Keep one codebase for sqlite/pg
    if _IS_PG:
        cur.execute(query.replace("?", "%s"), params)
    else:
        cur.execute(query, params)


def init_db():
    with closing(get_connection()) as conn:
        cur = conn.cursor()
        if _IS_PG:
            _execute(
                cur,
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    role TEXT DEFAULT 'user',
                    premium_until BIGINT DEFAULT 0
                )
                """,
            )
        else:
            _execute(
                cur,
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    role TEXT DEFAULT 'user',
                    premium_until INTEGER DEFAULT 0
                )
                """,
            )
        conn.commit()


def ensure_user_exists(user_id: int, username: str | None = None):
    with closing(get_connection()) as conn:
        cur = conn.cursor()

        _execute(cur, f"SELECT user_id FROM users WHERE user_id = {_PARAM}", (user_id,))
        row = cur.fetchone()

        if row is None:
            _execute(
                cur,
                f"INSERT INTO users (user_id, username, role, premium_until) VALUES ({_PARAM}, {_PARAM}, 'user', 0)",
                (user_id, (username or "")),
            )
        else:
            if username:
                _execute(
                    cur,
                    f"UPDATE users SET username = {_PARAM} WHERE user_id = {_PARAM}",
                    (username, user_id),
                )
        conn.commit()


def get_user_by_username(username: str):
    if not username:
        return None
    username = username.lstrip("@").strip()

    with closing(get_connection()) as conn:
        cur = conn.cursor()
        _execute(
            cur,
            f"SELECT user_id, username, role, premium_until FROM users WHERE username = {_PARAM}",
            (username,),
        )
        return cur.fetchone()


def get_user_role(user_id: int):
    with closing(get_connection()) as conn:
        cur = conn.cursor()
        _execute(cur, f"SELECT role FROM users WHERE user_id = {_PARAM}", (user_id,))
        row = cur.fetchone()
        return row[0] if row else "user"


def set_user_role(user_id: int, role: str):
    with closing(get_connection()) as conn:
        cur = conn.cursor()

        if _IS_PG:
            _execute(
                cur,
                """
                INSERT INTO users (user_id, role, username, premium_until)
                VALUES (?, ?, '', 0)
                ON CONFLICT(user_id) DO UPDATE SET role = EXCLUDED.role
                """,
                (user_id, role),
            )
        else:
            _execute(
                cur,
                """
                INSERT INTO users (user_id, role)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET role = excluded.role
                """,
                (user_id, role),
            )
        conn.commit()


def get_premium_until(user_id: int) -> int:
    with closing(get_connection()) as conn:
        cur = conn.cursor()
        _execute(cur, f"SELECT premium_until FROM users WHERE user_id = {_PARAM}", (user_id,))
        row = cur.fetchone()
        return int(row[0]) if row and row[0] is not None else 0


def set_premium_until(user_id: int, premium_until: int):
    with closing(get_connection()) as conn:
        cur = conn.cursor()

        if _IS_PG:
            _execute(
                cur,
                """
                INSERT INTO users (user_id, premium_until, username, role)
                VALUES (?, ?, '', 'user')
                ON CONFLICT(user_id) DO UPDATE SET premium_until = EXCLUDED.premium_until
                """,
                (user_id, int(premium_until)),
            )
        else:
            _execute(
                cur,
                """
                INSERT INTO users (user_id, premium_until)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET premium_until = excluded.premium_until
                """,
                (user_id, int(premium_until)),
            )
        conn.commit()


def is_user_premium(user_id: int) -> bool:
    now = int(time.time())
    return get_premium_until(user_id) > now
