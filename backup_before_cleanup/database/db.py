import sqlite3
from datetime import datetime, timedelta

DB_PATH = "database/artbazar.db"


# =========================
# CONNECTION
# =========================

def get_connection():
    return sqlite3.connect(DB_PATH)


def get_db_connection():
    return get_connection()


# =========================
# INIT
# =========================

def init_db():
    with get_connection() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            username TEXT UNIQUE,
            first_name TEXT,
            role TEXT DEFAULT 'user',
            premium_until TEXT
        )
        """)
        conn.commit()


# =========================
# USER
# =========================

def create_or_update_user(telegram_id: int, username: str, first_name: str):
    username = username.lstrip("@") if username else None
    with get_connection() as conn:
        conn.execute("""
        INSERT INTO users (telegram_id, username, first_name)
        VALUES (?, ?, ?)
        ON CONFLICT(telegram_id)
        DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name
        """, (telegram_id, username, first_name))
        conn.commit()


def get_user_by_username(username: str):
    if not username:
        return None

    username = username.lstrip("@")
    cur = get_connection().cursor()
    cur.execute(
        "SELECT telegram_id, username, role, premium_until FROM users WHERE username = ?",
        (username,)
    )
    row = cur.fetchone()
    if not row:
        return None

    return {
        "telegram_id": row[0],
        "username": row[1],
        "role": row[2],
        "premium_until": row[3],
    }


# =========================
# ROLES
# =========================

def set_role(username: str, role: str):
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET role = ? WHERE username = ?",
            (role, username.lstrip("@"))
        )
        conn.commit()


def get_user_role(telegram_id: int) -> str:
    cur = get_connection().cursor()
    cur.execute(
        "SELECT role FROM users WHERE telegram_id = ?",
        (telegram_id,)
    )
    row = cur.fetchone()
    return row[0] if row else "user"


# =========================
# PREMIUM
# =========================

def give_premium_days(telegram_id: int, days: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT premium_until FROM users WHERE telegram_id = ?",
        (telegram_id,)
    )
    row = cur.fetchone()

    now = datetime.utcnow()

    if row and row[0]:
        try:
            current_until = datetime.fromisoformat(row[0])
            if current_until > now:
                new_until = current_until + timedelta(days=days)
            else:
                new_until = now + timedelta(days=days)
        except Exception:
            new_until = now + timedelta(days=days)
    else:
        new_until = now + timedelta(days=days)

    cur.execute(
        "UPDATE users SET premium_until = ? WHERE telegram_id = ?",
        (new_until.isoformat(), telegram_id)
    )

    conn.commit()


def revoke_premium(username: str):
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET premium_until = NULL WHERE username = ?",
            (username.lstrip("@"),)
        )
        conn.commit()


def is_premium(username: str) -> bool:
    cur = get_connection().cursor()
    cur.execute(
        "SELECT premium_until FROM users WHERE username = ?",
        (username.lstrip("@"),)
    )
    row = cur.fetchone()
    if not row or not row[0]:
        return False
    return datetime.fromisoformat(row[0]) > datetime.utcnow()


# =========================
# STATS (OWNER)
# =========================

def get_stats():
    cur = get_connection().cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE premium_until IS NOT NULL")
    premium = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'manager'")
    managers = cur.fetchone()[0]

    return {
        "total": total,
        "premium": premium,
        "managers": managers
    }
