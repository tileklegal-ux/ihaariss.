# database/db.py
import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


@contextmanager
def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                telegram_id BIGINT,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                role TEXT DEFAULT 'user',
                premium_until BIGINT DEFAULT 0,
                is_premium BOOLEAN DEFAULT FALSE
            )
            """)
            conn.commit()


def ensure_user_exists(
    telegram_id: int,
    username: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT user_id FROM users WHERE telegram_id = %s",
                (telegram_id,),
            )
            row = cur.fetchone()

            if row is None:
                cur.execute(
                    """
                    INSERT INTO users (user_id, telegram_id, username, first_name, last_name)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (telegram_id, telegram_id, username, first_name, last_name),
                )
            else:
                cur.execute(
                    """
                    UPDATE users
                    SET username = %s,
                        first_name = %s,
                        last_name = %s
                    WHERE telegram_id = %s
                    """,
                    (username, first_name, last_name, telegram_id),
                )

            conn.commit()


def get_user_role(user_id: int) -> str:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT role FROM users WHERE telegram_id = %s",
                (user_id,),
            )
            row = cur.fetchone()
            return row[0] if row else "user"


def set_user_role(user_id: int, role: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE users
                SET role = %s
                WHERE telegram_id = %s
                """,
                (role, user_id),
            )
            conn.commit()


def get_user_by_username(username: str):
    if not username:
        return None

    username = username.lstrip("@").strip()

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT user_id, telegram_id, username, role, premium_until
                FROM users
                WHERE username = %s
                """,
                (username,),
            )
            return cur.fetchone()


def get_premium_until(user_id: int) -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT premium_until FROM users WHERE telegram_id = %s",
                (user_id,),
            )
            row = cur.fetchone()
            return int(row[0]) if row and row[0] else 0


def set_premium_until(user_id: int, premium_until: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE users
                SET premium_until = %s,
                    is_premium = %s
                WHERE telegram_id = %s
                """,
                (int(premium_until), premium_until > int(time.time()), user_id),
            )
            conn.commit()


def is_user_premium(user_id: int) -> bool:
    now = int(time.time())
    return get_premium_until(user_id) > now
