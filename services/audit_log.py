import os
import sqlite3
from datetime import datetime

DB_PATH = "audit_log.db"


# -------------------------------------------------
# INIT
# -------------------------------------------------
def init_audit_log():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                event TEXT,
                created_at TEXT
            )
            """
        )
        conn.commit()
        conn.close()


# -------------------------------------------------
# WRITE EVENT
# -------------------------------------------------
def log_event(user_id: int, event: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO audit_log (user_id, event, created_at) VALUES (?, ?, ?)",
        (
            user_id,
            event,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    conn.commit()
    conn.close()


# -------------------------------------------------
# READ LAST EVENT (FOR OWNER STATS)
# -------------------------------------------------
def get_last_event() -> str | None:
    if not os.path.exists(DB_PATH):
        return None

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "SELECT event, created_at FROM audit_log ORDER BY id DESC LIMIT 1"
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    event, created_at = row
    return f"{event} ({created_at})"
