# database/db.py
import os
import sqlite3
import psycopg2
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "database/artbazar.db")
DATABASE_URL = os.getenv("DATABASE_URL")


def _is_postgres() -> bool:
    return bool(DATABASE_URL)


def get_db_connection():
    if _is_postgres():
        return psycopg2.connect(DATABASE_URL)
    os.makedirs(os.path.dirname(SQLITE_DB_PATH) or ".", exist_ok=True)
    return sqlite3.connect(SQLITE_DB_PATH)


get_connection = get_db_connection


def ensure_user_exists(telegram_id: int, username: str = None):
    """Создает или обновляет пользователя в БД"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if _is_postgres():
            # Проверяем, существует ли пользователь
            cur.execute(
                "SELECT telegram_id FROM users WHERE telegram_id = %s",
                (telegram_id,)
            )
            if cur.fetchone():
                # Обновляем username, если он изменился
                if username:
                    cur.execute(
                        "UPDATE users SET username = %s WHERE telegram_id = %s",
                        (username, telegram_id)
                    )
            else:
                # Создаем нового пользователя
                cur.execute(
                    "INSERT INTO users (telegram_id, username, role, is_premium, premium_until) VALUES (%s, %s, 'user', FALSE, NULL)",
                    (telegram_id, username)
                )
        else:
            # SQLite
            cur.execute(
                "SELECT 1 FROM users WHERE telegram_id = ?",
                (telegram_id,)
            )
            if cur.fetchone():
                if username:
                    cur.execute(
                        "UPDATE users SET username = ? WHERE telegram_id = ?",
                        (username, telegram_id)
                    )
            else:
                cur.execute(
                    "INSERT INTO users (telegram_id, username, role, is_premium, premium_until) VALUES (?, ?, 'user', 0, NULL)",
                    (telegram_id, username)
                )
        conn.commit()
    finally:
        conn.close()


def get_user(telegram_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if _is_postgres():
            cur.execute(
                "SELECT telegram_id, username, role, is_premium, premium_until "
                "FROM users WHERE telegram_id = %s",
                (telegram_id,),
            )
        else:
            cur.execute(
                "SELECT telegram_id, username, role, is_premium, premium_until "
                "FROM users WHERE telegram_id = ?",
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


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if _is_postgres():
            cur.execute(
                "SELECT telegram_id, username, role, is_premium, premium_until "
                "FROM users WHERE username ILIKE %s",
                (username,),
            )
        else:
            cur.execute(
                "SELECT telegram_id, username, role, is_premium, premium_until "
                "FROM users WHERE username COLLATE NOCASE = ?",
                (username,),
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


def set_role_by_telegram_id(telegram_id: int, role: str) -> None:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if _is_postgres():
            cur.execute(
                "UPDATE users SET role = %s WHERE telegram_id = %s",
                (role, telegram_id),
            )
        else:
            cur.execute(
                "UPDATE users SET role = ? WHERE telegram_id = ?",
                (role, telegram_id),
            )
        conn.commit()
    finally:
        conn.close()


def is_user_premium(telegram_id: int) -> bool:
    user = get_user(telegram_id)
    if not user:
        return False
    if not user["is_premium"]:
        return False
    if not user["premium_until"]:
        return False
    try:
        return datetime.utcnow() <= user["premium_until"]
    except Exception:
        return False


def update_premium_until(telegram_id: int, premium_until: datetime) -> None:
    conn = get_db_connection()
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


def give_premium_days(telegram_id: int, days: int) -> None:
    new_until = datetime.utcnow() + timedelta(days=days)
    update_premium_until(telegram_id, new_until)


def remove_premium_from_db(telegram_id: int) -> None:
    conn = get_db_connection()
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
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if _is_postgres():
            cur.execute(
                "SELECT telegram_id, premium_until "
                "FROM users WHERE is_premium = TRUE AND premium_until IS NOT NULL"
            )
        else:
            cur.execute(
                "SELECT telegram_id, premium_until "
                "FROM users WHERE is_premium = 1 AND premium_until IS NOT NULL"
            )
        rows = cur.fetchall() or []
        return [{"telegram_id": r[0], "premium_until": r[1]} for r in rows]
    finally:
        conn.close()
