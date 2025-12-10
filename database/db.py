import os
from datetime import datetime, timedelta

import psycopg2
from psycopg2.extras import RealDictCursor

# Берём строку подключения из переменной окружения
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    """
    Создаёт подключение к PostgreSQL.
    """
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL не задан. Проверь .env и Variables в Railway.")
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def init_db():
    """
    Создаёт таблицы в PostgreSQL, если их ещё нет.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            role TEXT DEFAULT 'user',
            premium_until TIMESTAMPTZ
        );
        """
    )

    # Таблица истории анализов
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS analysis_history (
            id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(user_id),
            table_json TEXT,
            ai_json TEXT,
            created_at TIMESTAMPTZ
        );
        """
    )

    conn.commit()
    conn.close()


# -------- USERS --------


def get_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def get_user_by_username(username: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    conn.close()
    return user


def create_or_update_user(user_id, username, first_name, last_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
    exists = cursor.fetchone()

    if exists:
        cursor.execute(
            """
            UPDATE users
            SET username = %s,
                first_name = %s,
                last_name = %s
            WHERE user_id = %s
            """,
            (username, first_name, last_name, user_id),
        )
    else:
        cursor.execute(
            """
            INSERT INTO users (user_id, username, first_name, last_name)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, username, first_name, last_name),
        )

    conn.commit()
    conn.close()


# -------- PREMIUM --------


def set_premium(user_id: int, days: int):
    """
    Выдаёт Premium на X дней или продлевает, если Premium уже есть.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT premium_until FROM users WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()

    now = datetime.utcnow()

    if row and row["premium_until"]:
        try:
            current_until = row["premium_until"]
        except Exception:
            current_until = now
    else:
        current_until = now

    new_until = max(now, current_until) + timedelta(days=days)

    cursor.execute(
        """
        UPDATE users
        SET premium_until = %s
        WHERE user_id = %s
        """,
        (new_until, user_id),
    )

    conn.commit()
    conn.close()


def remove_premium(user_id: int):
    """
    Полностью отключает Premium.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET premium_until = NULL
        WHERE user_id = %s
        """,
        (user_id,),
    )

    conn.commit()
    conn.close()


def get_all_premium_users():
    """
    Возвращает всех пользователей, у которых есть премиум.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT user_id, username, premium_until
        FROM users
        WHERE premium_until IS NOT NULL
        """
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def disable_expired_premium():
    """
    Автоматически отключает премиум у всех, чей срок истёк.
    """
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.utcnow()

    cursor.execute(
        """
        UPDATE users
        SET premium_until = NULL
        WHERE premium_until <= %s
        """,
        (now,),
    )

    conn.commit()
    conn.close()


# -------- ROLES & STATS --------


def set_role(user_id: int, role: str):
    """
    Устанавливает роль пользователю: 'user' / 'manager' / 'owner'.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET role = %s
        WHERE user_id = %s
        """,
        (role, user_id),
    )

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

    cursor.execute("SELECT COUNT(*) AS cnt FROM users")
    total_users = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) AS cnt FROM users WHERE role = 'manager'")
    managers = cursor.fetchone()["cnt"]

    cursor.execute(
        "SELECT COUNT(*) AS cnt FROM users WHERE premium_until IS NOT NULL"
    )
    premium_users = cursor.fetchone()["cnt"]

    conn.close()

    return {
        "total_users": total_users,
        "premium_users": premium_users,
        "managers": managers,
    }
