# database/db.py

import os
import sqlite3
import psycopg2
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

DATABASE_URL = os.getenv("DATABASE_URL")
SQLITE_DB_PATH = "database/artbazar.db"


def is_postgres() -> bool:
    return bool(DATABASE_URL)


def get_connection():
    if is_postgres():
        return psycopg2.connect(DATABASE_URL)
    os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)
    return sqlite3.connect(SQLITE_DB_PATH)


# -------------------------
# USER CORE
# -------------------------

def ensure_user_exists(
    telegram_id: int,
    username: str = None,
    first_name: str = None,
    last_name: str = None,
    language: str = "ru",
):
    """
    Гарантирует, что пользователь существует.
    Работает С ТЕКУЩЕЙ СХЕМОЙ users в PostgreSQL.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()

        if is_postgres():
            cur.execute(
                "SELECT user_id FROM users WHERE telegram_id = %s",
                (telegram_id,),
            )
            row = cur.fetchone()

            if row:
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
            else:
                cur.execute(
                    """
                    INSERT INTO users (
                        user_id,
                        telegram_id,
                        username,
                        first_name,
                        last_name,
                        role,
                        language,
                        is_premium
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        telegram_id,        # user_id = telegram_id (канонично)
                        telegram_id,
                        username,
                        first_name,
                        last_name,
                        "user",
                        language,
                        False,
                    ),
                )
        else:
            # SQLite (fallback)
            cur.execute(
                "SELECT telegram_id FROM users WHERE telegram_id = ?",
                (telegram_id,),
            )
            row = cur.fetchone()

            if not row:
                cur.execute(
                    """
                    INSERT INTO users (
                        telegram_id,
                        username,
                        role,
                        is_premium
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (telegram_id, username, "user", 0),
                )

        conn.commit()
    finally:
        conn.close()


def get_user_role(telegram_id: int) -> str:
    conn = get_connection()
    try:
        cur = conn.cursor()
        if is_postgres():
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


def set_role_by_telegram_id(telegram_id: int, role: str):
    conn = get_connection()
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


def set_user_role(telegram_id: int, role: str):
    # алиас для совместимости
    set_role_by_telegram_id(telegram_id, role)


# -------------------------
# PREMIUM
# -------------------------

def is_user_premium(telegram_id: int) -> bool:
    conn = get_connection()
    try:
        cur = conn.cursor()
        if is_postgres():
            cur.execute(
                "SELECT is_premium FROM users WHERE telegram_id = %s",
                (telegram_id,),
            )
        else:
            cur.execute(
                "SELECT is_premium FROM users WHERE telegram_id = ?",
                (telegram_id,),
            )
        row = cur.fetchone()
        return bool(row[0]) if row else False
    finally:
        conn.close()


def give_premium_days(telegram_id: int, days: int):
    conn = get_connection()
    try:
        cur = conn.cursor()
        if is_postgres():
            cur.execute(
                "UPDATE users SET is_premium = TRUE WHERE telegram_id = %s",
                (telegram_id,),
            )
        else:
            cur.execute(
                "UPDATE users SET is_premium = 1 WHERE telegram_id = ?",
                (telegram_id,),
            )
        conn.commit()
    finally:
        conn.close()
