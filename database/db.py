import sqlite3
from datetime import datetime

DB_PATH = "database/artbazar.db"


# ==================================================
# CONNECTION
# ==================================================

def get_db_connection():
    return sqlite3.connect(DB_PATH)


def get_connection():
    return get_db_connection()


# ==================================================
# SCHEMA HELPERS
# ==================================================

def _get_existing_columns(cur, table_name: str) -> set:
    cur.execute(f"PRAGMA table_info({table_name})")
    rows = cur.fetchall()
    # PRAGMA table_info: (cid, name, type, notnull, dflt_value, pk)
    return {r[1] for r in rows}


def _ensure_users_schema(cur):
    """
    ВАЖНО:
    - если база уже существует и таблица users создана по старой схеме,
      CREATE TABLE IF NOT EXISTS не добавит новые колонки.
    - поэтому делаем безопасное добавление недостающих колонок через ALTER TABLE.
    """
    # таблица (на случай если её вообще нет)
    cur.execute("""
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
    """)

    cols = _get_existing_columns(cur, "users")

    # добавляем недостающие колонки безопасно
    if "username" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN username TEXT")
        cols.add("username")

    if "first_name" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN first_name TEXT")
        cols.add("first_name")

    if "role" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
        cols.add("role")

    if "is_premium" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN is_premium INTEGER DEFAULT 0")
        cols.add("is_premium")

    if "premium_until" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN premium_until TEXT")
        cols.add("premium_until")

    if "created_at" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN created_at TEXT")
        cols.add("created_at")

    if "updated_at" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN updated_at TEXT")
        cols.add("updated_at")


# ==================================================
# INIT
# ==================================================

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    _ensure_users_schema(cur)

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # безопасное заполнение времени
    cur.execute("UPDATE users SET created_at = COALESCE(created_at, ?)", (now,))
    cur.execute("UPDATE users SET updated_at = COALESCE(updated_at, ?)", (now,))

    conn.commit()
    conn.close()


# ==================================================
# USERS
# ==================================================

def create_or_update_user(telegram_id: int, username: str, first_name: str):
    conn = get_db_connection()
    cur = conn.cursor()

    _ensure_users_schema(cur)

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    username = (username or "").lstrip("@")
    first_name = first_name or ""

    cur.execute(
        "SELECT telegram_id FROM users WHERE telegram_id = ?",
        (telegram_id,),
    )

    if cur.fetchone():
        cur.execute(
            """
            UPDATE users
            SET username = ?, first_name = ?, updated_at = ?
            WHERE telegram_id = ?
            """,
            (username, first_name, now, telegram_id),
        )
    else:
        cur.execute(
            """
            INSERT INTO users
            (telegram_id, username, first_name, role, is_premium, created_at, updated_at)
            VALUES (?, ?, ?, 'user', 0, ?, ?)
            """,
            (telegram_id, username, first_name, now, now),
        )

    conn.commit()
    conn.close()


def get_user_role(telegram_id: int) -> str:
    conn = get_db_connection()
    cur = conn.cursor()

    _ensure_users_schema(cur)

    cur.execute(
        "SELECT role FROM users WHERE telegram_id = ?",
        (telegram_id,),
    )
    row = cur.fetchone()
    conn.close()

    return row[0] if row else "user"


def set_role_by_telegram_id(telegram_id: int, role: str) -> bool:
    conn = get_db_connection()
    cur = conn.cursor()

    _ensure_users_schema(cur)

    cur.execute(
        "UPDATE users SET role = ?, updated_at = ? WHERE telegram_id = ?",
        (role, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), telegram_id),
    )

    ok = cur.rowcount > 0
    conn.commit()
    conn.close()
    return ok


def get_user_by_username(username: str):
    conn = get_db_connection()
    cur = conn.cursor()

    _ensure_users_schema(cur)

    username = (username or "").lstrip("@")

    cur.execute(
        "SELECT telegram_id, username, role FROM users WHERE username = ?",
        (username,),
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "telegram_id": row[0],
        "username": row[1],
        "role": row[2],
    }


# ==================================================
# PREMIUM
# ==================================================

def is_user_premium(telegram_id: int) -> bool:
    conn = get_db_connection()
    cur = conn.cursor()

    _ensure_users_schema(cur)

    cur.execute(
        "SELECT is_premium, premium_until FROM users WHERE telegram_id = ?",
        (telegram_id,),
    )
    row = cur.fetchone()
    conn.close()

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


# ==================================================
# STATS
# ==================================================

def get_stats():
    conn = get_db_connection()
    cur = conn.cursor()

    _ensure_users_schema(cur)

    stats = {}
    for role in ["user", "manager", "owner"]:
        cur.execute("SELECT COUNT(*) FROM users WHERE role = ?", (role,))
        stats[role] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE is_premium = 1")
    stats["premium"] = cur.fetchone()[0]

    conn.close()
    return stats
