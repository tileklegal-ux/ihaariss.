import os
import sqlite3
import psycopg2

SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "database/artbazar.db")
DATABASE_URL = os.getenv("DATABASE_URL")


def _is_postgres() -> bool:
    return bool(DATABASE_URL)


def get_connection():
    if _is_postgres():
        return psycopg2.connect(DATABASE_URL)
    os.makedirs(os.path.dirname(SQLITE_DB_PATH) or ".", exist_ok=True)
    return sqlite3.connect(SQLITE_DB_PATH)


def get_user_role(telegram_id: int) -> str:
    conn = get_connection()
    try:
        cur = conn.cursor()
        if _is_postgres():
            cur.execute(
                "SELECT role FROM users WHERE telegram_id = %s",
                (telegram_id,),
            )
        else:
            cur.execute(
                "SELECT role FROM users WHERE telegram_id = ?",
                (telegram_id,),
            )
        row = cur.fetchone()
        return row[0] if row else "user"
    finally:
        conn.close()
