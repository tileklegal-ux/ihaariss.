# database/db.py

import os
import sqlite3
import psycopg2
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

DATABASE_URL = os.getenv("DATABASE_URL")
SQLITE_DB_PATH = "database/artbazar.db"


# =========================
# CONNECTION
# =========================

def is_postgres() -> bool:
    return bool(DATABASE_URL)


def get_db_connection():
    if is_postgres():
        return psycopg2.connect(DATABASE_URL)
    os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)
    return sqlite3.connect(SQLITE_DB_PATH)


get_connection = get_db_connection


# =========================
# USERS
# =========================

def get_user(telegram_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if is_postgres():
            cur.execute(
                """
                SELECT telegram_id, username, role, is_premium, premium_until
                FROM users WHERE telegram_id = %s
                """,
                (telegram_id,),
            )
            row = cur.fetchone()
        else:
            cur.execute(
                """
                SELECT telegram_id, username, role, is_premium, premium_until
                FROM users WHERE telegram_id = ?
                """,
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
        uname = username.lstrip("@")

        if is_postgres():
            cur.execute(
                """
                SELECT telegram_id, username, role
                FROM users WHERE username = %s
                """,
                (uname,),
            )
            row = cur.fetchone()
        else:
            cur.execute(
                """
                SELECT telegram_id, username, role
                FROM users WHERE username = ?
                """,
                (uname,),
            )
            row = cur.fetchone()

        if not row:
            return None

        return {
            "telegram_id": row[0],
            "username": row[1],
            "role": row[2],
        }
    finally:
        conn.close()


def ensure_user_exists(
    telegram_id: int,
    username: str = None,
    first_name: str = None,
    last_name: str = None,
    language: str = "ru",
):
    conn = get_db_connection()
    try:
        cur = conn.cursor()

        if is_postgres():
            cur.execute(
                "SELECT telegram_id FROM users WHERE telegram_id = %s",
                (telegram_id,),
            )
            exists = cur.fetchone()

            if not exists:
                cur.execute(
                    """
                    INSERT INTO users
                    (telegram_id, username, role, is_premium)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (telegram_id, username, "user", False),
                )
        else:
            cur.execute(
                "SELECT telegram_id FROM users WHERE telegram_id = ?",
                (telegram_id,),
            )
            if not cur.fetchone():
                cur.execute(
                    """
                    INSERT INTO users
                    (telegram_id, username, role, is_premium)
                    VALUES (?, ?, ?, ?)
                    """,
                    (telegram_id, username, "user", 0),
                )

        conn.commit()
    finally:
        conn.close()


# =========================
# ROLES
# =========================

def get_user_role(telegram_id: int) -> str:
    user = get_user(telegram_id)
    return user["role"] if user else "user"


def set_role_by_telegram_id(telegram_id: int, role: str):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if is_postgres():
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


set_user_role = set_role_by_telegram_id


# =========================
# PREMIUM
# =========================

def is_user_premium(telegram_id: int) -> bool:
    user = get_user(telegram_id)
    return bool(user and user["is_premium"])


def give_premium_days(telegram_id: int, days: int):
    """Используется OWNER / MANAGER"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        until = datetime.utcnow() + timedelta(days=days)

        if is_postgres():
            cur.execute(
                """
                UPDATE users
                SET is_premium = %s,
                    premium_until = %s
                WHERE telegram_id = %s
                """,
                (True, until, telegram_id),
            )
        else:
            cur.execute(
                """
                UPDATE users
                SET is_premium = 1,
                    premium_until = ?
                WHERE telegram_id = ?
                """,
                (until.isoformat(), telegram_id),
            )

        conn.commit()
    finally:
        conn.close()
