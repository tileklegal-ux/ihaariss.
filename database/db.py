import os
import sqlite3
import psycopg2
from datetime import datetime

SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "database/artbazar.db")
DATABASE_URL = os.getenv("DATABASE_URL")


def _is_postgres() -> bool:
    return bool(DATABASE_URL)


def get_connection():
    if _is_postgres():
        return psycopg2.connect(DATABASE_URL)
    os.makedirs(os.path.dirname(SQLITE_DB_PATH) or ".", exist_ok=True)
    return sqlite3.connect(SQLITE_DB_PATH)


# =========================
# USERS
# =========================

def get_user(telegram_id: int):
    conn = get_connection()
    try:
        cur = conn.cursor()
        if _is_postgres():
            cur.execute(
                "SELECT telegram_id, username, role, is_premium, premium_until FROM users WHERE telegram_id = %s",
                (telegram_id,),
            )
        else:
            cur.execute(
                "SELECT telegram_id, username, role, is_premium, premium_until FROM users WHERE telegram_id = ?",
                (telegram_id,),
            )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "telegram_id": row[0],
            "username": row[1],
            "role": row[2],
            "is_premium": bool(row[3]),
            "premium_until": row[4],
        }
    finally:
        conn.close()


def get_user_role(telegram_id: int) -> str:
    user = get_user(telegram_id)
    return user["role"] if user else "user"


def update_premium_until(telegram_id: int, premium_until: datetime):
    conn = get_connection()
    try:
        cur = conn.cursor()
        if _is_postgres():
            cur.execute(
                """
                UPDATE users
                SET is_premium = TRUE,
                    premium_until = %s
                WHERE telegram_id = %s
                """,
                (premium_until, telegram_id),
            )
        else:
            cur.execute(
                """
                UPDATE users
                SET is_premium = 1,
                    premium_until = ?
                WHERE telegram_id = ?
                """,
                (premium_until, telegram_id),
            )
        conn.commit()
    finally:
        conn.close()


def remove_premium_from_db(telegram_id: int):
    conn = get_connection()
    try:
        cur = conn.cursor()
        if _is_postgres():
            cur.execute(
                """
                UPDATE users
                SET is_premium = FALSE,
                    premium_until = NULL
                WHERE telegram_id = %s
                """,
                (telegram_id,),
            )
        else:
            cur.execute(
                """
                UPDATE users
                SET is_premium = 0,
                    premium_until = NULL
                WHERE telegram_id = ?
                """,
                (telegram_id,),
            )
        conn.commit()
    finally:
        conn.close()


def get_all_premium_users():
    conn = get_connection()
    try:
        cur = conn.cursor()
        if _is_postgres():
            cur.execute(
                "SELECT telegram_id, premium_until FROM users WHERE is_premium = TRUE AND premium_until IS NOT NULL"
            )
        else:
            cur.execute(
                "SELECT telegram_id, premium_until FROM users WHERE is_premium = 1 AND premium_until IS NOT NULL"
            )
        rows = cur.fetchall() or []
        return [
            {"telegram_id": r[0], "premium_until": r[1]}
            for r in rows
        ]
    finally:
        conn.close()
