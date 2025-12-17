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
                (telegram_id,),
            )
            row = cur.fetchone()
            if row:
                cur.execute(
                    "UPDATE users SET username = %s WHERE telegram_id = %s",
                    (username, telegram_id),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO users (telegram_id, username, role, is_premium, premium_until)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (telegram_id, username, "user", False, None),
                )
        else:
            cur.execute(
                "SELECT telegram_id FROM users WHERE telegram_id = ?",
                (telegram_id,),
            )
            row = cur.fetchone()
            if row:
                cur.execute(
                    "UPDATE users SET username = ? WHERE telegram_id = ?",
                    (username, telegram_id),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO users (telegram_id, username, role, is_premium, premium_until)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (telegram_id, username, "user", 0, None),
                )
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Создает таблицы если их нет"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if _is_postgres():
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id BIGINT PRIMARY KEY,
                    username TEXT,
                    role TEXT DEFAULT 'user',
                    is_premium BOOLEAN DEFAULT FALSE,
                    premium_until TIMESTAMP NULL
                )
                """
            )
        else:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    username TEXT,
                    role TEXT DEFAULT 'user',
                    is_premium INTEGER DEFAULT 0,
                    premium_until TEXT
                )
                """
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

        premium_until = row[4]
        if not _is_postgres():
            # sqlite хранит как строку
            if premium_until:
                try:
                    premium_until = datetime.fromisoformat(premium_until)
                except Exception:
                    premium_until = None

        return {
            "telegram_id": row[0],
            "username": row[1],
            "role": row[2],
            "is_premium": bool(row[3]) if _is_postgres() else bool(int(row[3])),
            "premium_until": premium_until,
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
                "FROM users WHERE username LIKE ?",
                (username,),
            )
        row = cur.fetchone()
        if not row:
            return None

        premium_until = row[4]
        if not _is_postgres():
            if premium_until:
                try:
                    premium_until = datetime.fromisoformat(premium_until)
                except Exception:
                    premium_until = None

        return {
            "telegram_id": row[0],
            "username": row[1],
            "role": row[2],
            "is_premium": bool(row[3]) if _is_postgres() else bool(int(row[3])),
            "premium_until": premium_until,
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


def set_user_role(telegram_id: int, role: str) -> None:
    """Совместимость: алиас для set_role_by_telegram_id (используется в handlers/role_actions.py)."""
    return set_role_by_telegram_id(telegram_id, role)


def is_user_premium(telegram_id: int) -> bool:
    user = get_user(telegram_id)
    if not user:
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
                (premium_until.isoformat(), telegram_id),
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
