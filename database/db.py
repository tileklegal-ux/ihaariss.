# database/db.py
import os
import psycopg2
from contextlib import contextmanager
from datetime import datetime, timezone

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
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    role TEXT NOT NULL DEFAULT 'user',
                    premium_until TIMESTAMPTZ
                )
                """
            )
        conn.commit()


def ensure_user_exists(user_id: int, username: str | None = None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT user_id FROM users WHERE user_id = %s",
                (user_id,),
            )
            exists = cur.fetchone()

            if not exists:
                cur.execute(
                    """
                    INSERT INTO users (user_id, username, role, premium_until)
                    VALUES (%s, %s, 'user', NULL)
                    """,
                    (user_id, username or ""),
                )
            else:
                if username:
                    cur.execute(
                        """
                        UPDATE users
                        SET username = %s
                        WHERE user_id = %s
                        """,
                        (username, user_id),
                    )
        conn.commit()


def get_user_role(user_id: int) -> str:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT role FROM users WHERE user_id = %s",
                (user_id,),
            )
            row = cur.fetchone()
            return row[0] if row else "user"


def set_user_role(user_id: int, role: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (user_id, role)
                VALUES (%s, %s)
                ON CONFLICT (user_id)
                DO UPDATE SET role = EXCLUDED.role
                """,
                (user_id, role),
            )
        conn.commit()


def get_premium_until(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT premium_until FROM users WHERE user_id = %s",
                (user_id,),
            )
            row = cur.fetchone()
            return row[0] if row else None


def set_premium_until(user_id: int, premium_until: datetime | None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (user_id, premium_until)
                VALUES (%s, %s)
                ON CONFLICT (user_id)
                DO UPDATE SET premium_until = EXCLUDED.premium_until
                """,
                (user_id, premium_until),
            )
        conn.commit()


def is_user_premium(user_id: int) -> bool:
    premium_until = get_premium_until(user_id)

    if not premium_until:
        return False

    if premium_until <= datetime.now(timezone.utc):
        return False

    return True
