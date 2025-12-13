import sqlite3
from datetime import datetime, timedelta

DB_PATH = "database/artbazar.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        role TEXT DEFAULT 'user',
        premium_until TEXT
    )
    """)

    # Таблица истории анализов (только для PREMIUM)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        table_json TEXT,
        ai_json TEXT,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    """)

    conn.commit()
    conn.close()


# --------- USERS ---------

def get_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def get_user_by_username(username: str):
    """
    Возвращает пользователя по username (без '@').
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user


def create_or_update_user(user_id, username, first_name, last_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    exists = cursor.fetchone()

    if exists:
        cursor.execute("""
            UPDATE users SET username=?, first_name=?, last_name=?
            WHERE user_id=?
        """, (username, first_name, last_name, user_id))

    else:
        cursor.execute("""
            INSERT INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        """, (user_id, username, first_name, last_name))

    conn.commit()
    conn.close()


# --------- PREMIUM ---------

def set_premium(user_id: int, days: int):
    """
    Выдаёт Premium на X дней или продлевает, если Premium уже есть.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT premium_until FROM users WHERE user_id=?", (user_id,))
    current = cursor.fetchone()

    now = datetime.utcnow()

    if current and current[0]:
        try:
            current_until = datetime.fromisoformat(current[0])
        except:
            current_until = now
    else:
        current_until = now

    new_until = (max(now, current_until) + timedelta(days=days)).isoformat()

    cursor.execute("""
        UPDATE users SET premium_until=?
        WHERE user_id=?
    """, (new_until, user_id))

    conn.commit()
    conn.close()


def remove_premium(user_id: int):
    """
    Полностью отключает Premium.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users SET premium_until=NULL
        WHERE user_id=?
    """, (user_id,))

    conn.commit()
    conn.close()


def get_all_premium_users():
    """
    Возвращает всех пользователей, у которых есть премиум.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, username, premium_until
        FROM users
        WHERE premium_until IS NOT NULL
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def disable_expired_premium():
    """
    Автоматически отключает премиум у всех, чей срок истёк.
    """
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.utcnow().isoformat()

    cursor.execute("""
        UPDATE users
        SET premium_until = NULL
        WHERE premium_until <= ?
    """, (now,))

    conn.commit()
    conn.close()


# --------- ROLES & STATS (для OWNER) ---------

def set_role(user_id: int, role: str):
    """
    Устанавливает роль пользователю: 'user' / 'manager' / 'owner' (если понадобится).
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users SET role=?
        WHERE user_id=?
    """, (role, user_id))

    conn.commit()
    conn.close()


def get_stats():
    """
    Возвращает базовую статистику:
    - total_users
    - premium_users
    - managers
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE role='manager'")
    managers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE premium_until IS NOT NULL")
    premium_users = cursor.fetchone()[0]

    conn.close()

    return {
        "total_users": total_users,
        "premium_users": premium_users,
        "managers": managers,
    }
