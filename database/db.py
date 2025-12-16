import os
import sqlite3
from datetime import datetime, timedelta

import psycopg2


# ==================================================
# DB CONFIG
# ==================================================
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "database/artbazar.db")
DATABASE_URL = os.getenv("DATABASE_URL")  # Railway Postgres


def _utcnow_str() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def _is_postgres() -> bool:
    return bool(DATABASE_URL)


# ==================================================
# CONNECTIONS
# ==================================================
def get_connection():
    """
    Возвращает подключение:
    - Postgres на Railway, если задан DATABASE_URL
    - иначе SQLite (локально)
    """
    if _is_postgres():
        return psycopg2.connect(
            DATABASE_URL,
            sslmode=os.getenv("PGSSLMODE", "require"),
        )

    os.makedirs(os.path.dirname(SQLITE_DB_PATH) or ".", exist_ok=True)
    return sqlite3.connect(SQLITE_DB_PATH)


# legacy alias (used in old code)
def get_db_connection():
    return get_connection()


def _placeholders() -> str:
    return "%s" if _is_postgres() else "?"


def _execute(conn, query: str, params=()):
    cur = conn.cursor()
    cur.execute(query, params)
    return cur


# ==================================================
# SCHEMA
# ==================================================
def init_db():
    conn = get_connection()
    try:
        if _is_postgres():
            _execute(
                conn,
                """
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id BIGINT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    role TEXT DEFAULT 'user',
                    is_premium BOOLEAN DEFAULT FALSE,
                    premium_until TIMESTAMP NULL,
                    created_at TIMESTAMP NULL,
                    updated_at TIMESTAMP NULL
                )
                """,
            )
        else:
            _execute(
                conn,
                """
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    role TEXT DEFAULT 'user',
                    is_premium INTEGER DEFAULT 0,
                    premium_until TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
                """,
            )
        conn.commit()
    finally:
        conn.close()


# ==================================================
# USERS
# ==================================================
def create_or_update_user(telegram_id: int, username: str | None, first_name: str | None):
    init_db()
    now = _utcnow_str()
    conn = get_connection()
    try:
        if _is_postgres():
            _execute(
                conn,
                """
                INSERT INTO users (telegram_id, username, first_name, created_at, updated_at)
                VALUES (%s, %s, %s, NOW(), NOW())
                ON CONFLICT (telegram_id) DO UPDATE SET
                    username = EXCLUDED.username,
                    first_name = EXCLUDED.first_name,
                    updated_at = NOW()
                """,
                (telegram_id, username, first_name),
            )
        else:
            _execute(
                conn,
                """
                INSERT INTO users (telegram_id, username, first_name, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(telegram_id) DO UPDATE SET
                    username=excluded.username,
                    first_name=excluded.first_name,
                    updated_at=excluded.updated_at
                """,
                (telegram_id, username, first_name, now, now),
            )
        conn.commit()
    finally:
        conn.close()


def get_user_role(telegram_id: int) -> str:
    init_db()
    conn = get_connection()
    try:
        ph = _placeholders()
        cur = _execute(conn, f"SELECT role FROM users WHERE telegram_id = {ph}", (telegram_id,))
        row = cur.fetchone()
        if not row:
            return "user"
        return row[0] or "user"
    finally:
        conn.close()


def set_role_by_telegram_id(telegram_id: int, role: str):
    init_db()
    conn = get_connection()
    try:
        ph = _placeholders()
        if _is_postgres():
            _execute(
                conn,
                f"""
                INSERT INTO users (telegram_id, role, created_at, updated_at)
                VALUES ({ph}, {ph}, NOW(), NOW())
                ON CONFLICT (telegram_id) DO UPDATE SET
                    role = EXCLUDED.role,
                    updated_at = NOW()
                """,
                (telegram_id, role),
            )
        else:
            now = _utcnow_str()
            _execute(
                conn,
                """
                INSERT INTO users (telegram_id, role, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(telegram_id) DO UPDATE SET
                    role=excluded.role,
                    updated_at=excluded.updated_at
                """,
                (telegram_id, role, now, now),
            )
        conn.commit()
    finally:
        conn.close()


def get_user_by_username(username: str):
    init_db()
    if not username:
        return None

    username = username.lstrip("@")
    conn = get_connection()
    try:
        ph = _placeholders()
        cur = _execute(
            conn,
            f"""
            SELECT telegram_id, username, first_name, role, is_premium, premium_until
            FROM users
            WHERE username = {ph}
            """,
            (username,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "telegram_id": row[0],
            "username": row[1],
            "first_name": row[2],
            "role": row[3],
            "is_premium": bool(row[4]),
            "premium_until": row[5],
        }
    finally:
        conn.close()


def is_user_premium(telegram_id: int) -> bool:
    init_db()
    conn = get_connection()
    try:
        ph = _placeholders()
        cur = _execute(
            conn,
            f"SELECT is_premium, premium_until FROM users WHERE telegram_id = {ph}",
            (telegram_id,),
        )
        row = cur.fetchone()
        if not row:
            return False

        is_premium = bool(row[0])
        premium_until = row[1]

        if not is_premium:
            return False

        if premium_until is None:
            return True

        if _is_postgres():
            return premium_until > datetime.utcnow()

        try:
            dt = datetime.strptime(str(premium_until), "%Y-%m-%d %H:%M:%S")
            return dt > datetime.utcnow()
        except Exception:
            return True
    finally:
        conn.close()


def set_premium_by_telegram_id(telegram_id: int, days: int):
    init_db()
    conn = get_connection()
    try:
        days = int(days)

        if _is_postgres():
            _execute(
                conn,
                """
                INSERT INTO users (telegram_id, is_premium, premium_until, created_at, updated_at)
                VALUES (%s, TRUE, NOW() + (%s || ' days')::interval, NOW(), NOW())
                ON CONFLICT (telegram_id) DO UPDATE SET
                    is_premium = TRUE,
                    premium_until = CASE
                        WHEN users.premium_until IS NULL THEN NOW() + (%s || ' days')::interval
                        WHEN users.premium_until > NOW() THEN users.premium_until + (%s || ' days')::interval
                        ELSE NOW() + (%s || ' days')::interval
                    END,
                    updated_at = NOW()
                """,
                (telegram_id, days, days, days, days),
            )
        else:
            cur = _execute(conn, "SELECT premium_until FROM users WHERE telegram_id = ?", (telegram_id,))
            row = cur.fetchone()

            base = datetime.utcnow()
            if row and row[0]:
                try:
                    existing = datetime.strptime(str(row[0]), "%Y-%m-%d %H:%M:%S")
                    if existing > base:
                        base = existing
                except Exception:
                    pass

            new_until = (base + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
            now = _utcnow_str()

            _execute(
                conn,
                """
                INSERT INTO users (telegram_id, is_premium, premium_until, created_at, updated_at)
                VALUES (?, 1, ?, ?, ?)
                ON CONFLICT(telegram_id) DO UPDATE SET
                    is_premium=1,
                    premium_until=excluded.premium_until,
                    updated_at=excluded.updated_at
                """,
                (telegram_id, new_until, now, now),
            )

        conn.commit()
    finally:
        conn.close()


# legacy alias (used by role_actions / owner code)
def give_premium_days(telegram_id: int, days: int):
    return set_premium_by_telegram_id(telegram_id, days)


def get_stats():
    init_db()
    conn = get_connection()
    try:
        cur = _execute(conn, "SELECT COUNT(*) FROM users", ())
        total = int(cur.fetchone()[0] or 0)

        if _is_postgres():
            cur = _execute(conn, "SELECT COUNT(*) FROM users WHERE is_premium = TRUE", ())
        else:
            cur = _execute(conn, "SELECT COUNT(*) FROM users WHERE is_premium = 1", ())
        premium = int(cur.fetchone()[0] or 0)

        return {"total_users": total, "premium_users": premium}
    finally:
        conn.close()
