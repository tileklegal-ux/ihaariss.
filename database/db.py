import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


# =========================
# USERS
# =========================

def ensure_user_exists(telegram_id: int, username: str = None,
                       first_name: str = None, last_name: str = None):
    """
    Гарантирует, что пользователь есть в БД.
    НИКАКОГО ON CONFLICT — только честный SELECT → INSERT
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT user_id FROM users WHERE telegram_id = %s",
        (telegram_id,)
    )
    user = cur.fetchone()

    if user is None:
        cur.execute(
            """
            INSERT INTO users (
                user_id,
                telegram_id,
                username,
                first_name,
                last_name,
                role,
                is_premium,
                premium_until
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                telegram_id,          # user_id = telegram_id (как у тебя в таблице)
                telegram_id,
                username,
                first_name,
                last_name,
                "user",
                False,
                None
            )
        )
        conn.commit()

    cur.close()
    conn.close()


def get_user(telegram_id: int):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE telegram_id = %s",
        (telegram_id,)
    )
    user = cur.fetchone()

    cur.close()
    conn.close()
    return user


def get_user_role(telegram_id: int) -> str:
    user = get_user(telegram_id)
    return user["role"] if user else "user"


# =========================
# ROLES
# =========================

def set_user_role(telegram_id: int, role: str):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET role = %s WHERE telegram_id = %s",
        (role, telegram_id)
    )
    conn.commit()

    cur.close()
    conn.close()


# =========================
# PREMIUM
# =========================

def give_premium_days(telegram_id: int, days: int):
    conn = get_db_connection()
    cur = conn.cursor()

    premium_until = datetime.utcnow() + timedelta(days=days)

    cur.execute(
        """
        UPDATE users
        SET is_premium = TRUE,
            premium_until = %s
        WHERE telegram_id = %s
        """,
        (premium_until, telegram_id)
    )

    conn.commit()
    cur.close()
    conn.close()


def remove_premium(telegram_id: int):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE users
        SET is_premium = FALSE,
            premium_until = NULL
        WHERE telegram_id = %s
        """,
        (telegram_id,)
    )

    conn.commit()
    cur.close()
    conn.close()


def is_user_premium(telegram_id: int) -> bool:
    user = get_user(telegram_id)
    if not user:
        return False

    if not user["is_premium"]:
        return False

    if user["premium_until"] is None:
        return False

    return user["premium_until"] > datetime.utcnow()


# =========================
# MANAGERS
# =========================

def add_manager(telegram_id: int):
    set_user_role(telegram_id, "manager")


def remove_manager(telegram_id: int):
    set_user_role(telegram_id, "user")
