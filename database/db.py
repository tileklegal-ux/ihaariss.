import psycopg2
import os
from datetime import datetime, timedelta

DATABASE_URL = os.getenv("DATABASE_URL")


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def ensure_user_exists(telegram_id: int, username: str | None):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO users (telegram_id, username, role, is_premium)
        VALUES (%s, %s, 'user', false)
        ON CONFLICT (telegram_id) DO NOTHING
        """,
        (telegram_id, username),
    )

    conn.commit()
    cur.close()
    conn.close()


def get_user_role(telegram_id: int) -> str | None:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT role FROM users WHERE telegram_id = %s",
        (telegram_id,),
    )
    row = cur.fetchone()

    cur.close()
    conn.close()

    return row[0] if row else None


def set_user_role(telegram_id: int, role: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET role = %s WHERE telegram_id = %s",
        (role, telegram_id),
    )

    conn.commit()
    cur.close()
    conn.close()


def is_user_premium(telegram_id: int) -> bool:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT is_premium FROM users WHERE telegram_id = %s",
        (telegram_id,),
    )
    row = cur.fetchone()

    cur.close()
    conn.close()

    return bool(row and row[0])
