import os
import sqlite3
from datetime import datetime, timedelta
from urllib.parse import urlparse

DB_PATH = "database/artbazar.db"


def _is_postgres() -> bool:
    url = os.getenv("DATABASE_URL", "").strip()
    return url.startswith("postgres://") or url.startswith("postgresql://")


def _pg_connect():
    # Import inside to avoid breaking local runs without psycopg2 installed
    import psycopg2

    url = os.getenv("DATABASE_URL", "").strip()
    if url.startswith("postgres://"):
        # psycopg2 expects postgresql:// sometimes; accept both
        url = "postgresql://" + url[len("postgres://") :]

    return psycopg2.connect(url)


def get_db_connection():
    if _is_postgres():
        return _pg_connect()
    return sqlite3.connect(DB_PATH)


def get_connection():
    return get_db_connection()


def _utc_now_str() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def init_db():
    conn = get_db_connection()
    try:
        cur = conn.cursor()

        if _is_postgres():
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id BIGINT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    role TEXT DEFAULT 'user',
                    is_premium BOOLEAN DEFAULT FALSE,
                    premium_until TIMESTAMP NULL,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
                """
            )

            now = datetime.utcnow()
            cur.execute("UPDATE users SET created_at = COALESCE(created_at, %s)", (now,))
            cur.execute("UPDATE users SET updated_at = COALESCE(updated_at, %s)", (now,))
        else:
            cur.execute(
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
                """
            )

            now = _utc_now_str()
            cur.execute("UPDATE users SET created_at = COALESCE(created_at, ?)", (now,))
            cur.execute("UPDATE users SET updated_at = COALESCE(updated_at, ?)", (now,))

        conn.commit()
    finally:
        conn.close()


def create_or_update_user(telegram_id: int, username: str, first_name: str):
    init_db()

    username = (username or "").lstrip("@")
    first_name = first_name or ""

    conn = get_db_connection()
    try:
        cur = conn.cursor()

        if _is_postgres():
            now = datetime.utcnow()

            cur.execute("SELECT telegram_id FROM users WHERE telegram_id = %s", (telegram_id,))
            exists = cur.fetchone() is not None

            if exists:
                cur.execute(
                    """
                    UPDATE users
                    SET username = %s, first_name = %s, updated_at = %s
                    WHERE telegram_id = %s
                    """,
                    (username, first_name, now, telegram_id),
                )
            else:
                # РОЛЬ ПО УМОЛЧАНИЮ: user (никаких костылей manager)
                cur.execute(
                    """
                    INSERT INTO users
                    (telegram_id, username, first_name, role, is_premium, created_at, updated_at)
                    VALUES (%s, %s, %s, 'user', FALSE, %s, %s)
                    """,
                    (telegram_id, username, first_name, now, now),
                )
        else:
            now = _utc_now_str()

            cur.execute("SELECT telegram_id FROM users WHERE telegram_id = ?", (telegram_id,))
            exists = cur.fetchone() is not None

            if exists:
                cur.execute(
                    """
                    UPDATE users
                    SET username = ?, first_name = ?, updated_at = ?
                    WHERE telegram_id = ?
                    """,
                    (username, first_name, now, telegram_id),
                )
            else:
                # РОЛЬ ПО УМОЛЧАНИЮ: user (никаких костылей manager)
                cur.execute(
                    """
                    INSERT INTO users
                    (telegram_id, username, first_name, role, is_premium, created_at, updated_at)
                    VALUES (?, ?, ?, 'user', 0, ?, ?)
                    """,
                    (telegram_id, username, first_name, now, now),
                )

        conn.commit()
    finally:
        conn.close()


def get_user_role(telegram_id: int) -> str:
    init_db()

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if _is_postgres():
            cur.execute("SELECT role FROM users WHERE telegram_id = %s", (telegram_id,))
        else:
            cur.execute("SELECT role FROM users WHERE telegram_id = ?", (telegram_id,))
        row = cur.fetchone()
        return row[0] if row else "user"
    finally:
        conn.close()


def set_role_by_telegram_id(telegram_id: int, role: str) -> bool:
    init_db()

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if _is_postgres():
            cur.execute(
                "UPDATE users SET role = %s, updated_at = %s WHERE telegram_id = %s",
                (role, datetime.utcnow(), telegram_id),
            )
            ok = cur.rowcount > 0
        else:
            cur.execute(
                "UPDATE users SET role = ?, updated_at = ? WHERE telegram_id = ?",
                (role, _utc_now_str(), telegram_id),
            )
            ok = cur.rowcount > 0

        conn.commit()
        return ok
    finally:
        conn.close()


def get_user_by_username(username: str):
    init_db()

    username_lower = (username or "").lstrip("@").lower()

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if _is_postgres():
            cur.execute(
                "SELECT telegram_id, username, role FROM users WHERE LOWER(username) = %s",
                (username_lower,),
            )
        else:
            cur.execute(
                "SELECT telegram_id, username, role FROM users WHERE LOWER(username) = ?",
                (username_lower,),
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


def set_premium_by_telegram_id(telegram_id: int, days: int) -> bool:
    init_db()

    conn = get_db_connection()
    try:
        cur = conn.cursor()

        if _is_postgres():
            now = datetime.utcnow()
            premium_until = now + timedelta(days=days)

            cur.execute(
                """
                UPDATE users
                SET is_premium = TRUE,
                    premium_until = %s,
                    updated_at = %s
                WHERE telegram_id = %s
                """,
                (premium_until, now, telegram_id),
            )
            ok = cur.rowcount > 0
        else:
            now = _utc_now_str()
            premium_until = (datetime.utcnow() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
            cur.execute(
                """
                UPDATE users
                SET is_premium = 1,
                    premium_until = ?,
                    updated_at = ?
                WHERE telegram_id = ?
                """,
                (premium_until, now, telegram_id),
            )
            ok = cur.rowcount > 0

        conn.commit()
        return ok
    finally:
        conn.close()


def is_user_premium(telegram_id: int) -> bool:
    init_db()

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if _is_postgres():
            cur.execute(
                "SELECT is_premium, premium_until FROM users WHERE telegram_id = %s",
                (telegram_id,),
            )
            row = cur.fetchone()
            if not row:
                return False

            is_premium, premium_until = row
            if not is_premium:
                return False

            if premium_until:
                return premium_until > datetime.utcnow()
            return True
        else:
            cur.execute(
                "SELECT is_premium, premium_until FROM users WHERE telegram_id = ?",
                (telegram_id,),
            )
            row = cur.fetchone()
            if not row:
                return False

            is_premium, premium_until = row
            if not is_premium:
                return False

            if premium_until:
                try:
                    until = datetime.strptime(premium_until, "%Y-%m-%d %H:%M:%S")
                    return until > datetime.utcnow()
                except Exception:
                    return False

            return True
    finally:
        conn.close()


def get_stats():
    init_db()

    conn = get_db_connection()
    try:
        cur = conn.cursor()

        stats = {}
        if _is_postgres():
            for role in ["user", "manager", "owner"]:
                cur.execute("SELECT COUNT(*) FROM users WHERE role = %s", (role,))
                stats[role] = int(cur.fetchone()[0])

            cur.execute("SELECT COUNT(*) FROM users WHERE is_premium = TRUE")
            stats["premium"] = int(cur.fetchone()[0])
        else:
            for role in ["user", "manager", "owner"]:
                cur.execute("SELECT COUNT(*) FROM users WHERE role = ?", (role,))
                stats[role] = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM users WHERE is_premium = 1")
            stats["premium"] = cur.fetchone()[0]

        return stats
    finally:
        conn.close()
