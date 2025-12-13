import os
import sqlite3
from datetime import datetime, timedelta

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters,
)

from database.db import get_user_role

# ==================================================
# BUTTONS
# ==================================================

BTN_ACTIVATE_PREMIUM = "🟢 Активировать Premium"

# ==================================================
# FSM
# ==================================================

FSM_WAIT_PREMIUM_INPUT = "wait_premium_input"

# ==================================================
# KEYBOARD
# ==================================================

def manager_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton(BTN_ACTIVATE_PREMIUM)]],
        resize_keyboard=True,
    )

# ==================================================
# DB helpers (локально, без правки database/db.py)
# ==================================================

def _db_path() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "database", "artbazar.db")


def _get_columns(conn) -> set:
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(users)")
    rows = cur.fetchall()
    return {r[1] for r in rows}


def set_premium_by_username(username: str, days: int) -> bool:
    username = (username or "").replace("@", "").strip()
    if not username or days <= 0:
        return False

    conn = sqlite3.connect(_db_path())
    try:
        cols = _get_columns(conn)
        cur = conn.cursor()

        cur.execute("SELECT telegram_id FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        if not row:
            return False

        now = datetime.utcnow()
        premium_until = (now + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

        if "premium_until" in cols:
            cur.execute(
                "UPDATE users SET is_premium = 1, premium_until = ?, updated_at = ? WHERE username = ?",
                (premium_until, now.strftime("%Y-%m-%d %H:%M:%S"), username),
            )
        else:
            if "updated_at" in cols:
                cur.execute(
                    "UPDATE users SET is_premium = 1, updated_at = ? WHERE username = ?",
                    (now.strftime("%Y-%m-%d %H:%M:%S"), username),
                )
            else:
                cur.execute(
                    "UPDATE users SET is_premium = 1 WHERE username = ?",
                    (username,),
                )

        conn.commit()
        return True
    finally:
        conn.close()

# ==================================================
# ACTIONS
# ==================================================

async def on_activate_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if get_user_role(update.effective_user.id) != "manager":
        return

    context.user_data[FSM_WAIT_PREMIUM_INPUT] = True

    await update.message.reply_text(
        "🟢 *Активация Premium*\n\n"
        "Отправь одной строкой:\n"
        "`@username дни`\n\n"
        "Пример:\n"
        "`@test_user 30`",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )


async def on_premium_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if get_user_role(update.effective_user.id) != "manager":
        return

    if not context.user_data.get(FSM_WAIT_PREMIUM_INPUT):
        return  # ❗ КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ

    text = (update.message.text or "").strip()
    parts = text.split()

    if len(parts) != 2:
        await update.message.reply_text(
            "❌ Неверный формат.\nИспользуй:\n`@username дни`",
            parse_mode="Markdown",
        )
        return

    username = parts[0].replace("@", "").strip()
    try:
        days = int(parts[1])
    except ValueError:
        await update.message.reply_text("❌ Количество дней должно быть числом.")
        return

    ok = set_premium_by_username(username, days)
    if not ok:
        await update.message.reply_text("❌ Пользователь не найден.")
        return

    context.user_data.pop(FSM_WAIT_PREMIUM_INPUT, None)

    await update.message.reply_text(
        f"✅ Premium активирован\n\n"
        f"👤 @{username}\n"
        f"⏳ Дней: {days}",
        reply_markup=manager_keyboard(),
    )

# ==================================================
# REGISTER
# ==================================================

def register_manager_handlers(app):
    app.add_handler(
        MessageHandler(
            filters.Regex(f"^{BTN_ACTIVATE_PREMIUM}$"),
            on_activate_premium,
        ),
        group=1,
    )

    # FSM input — ТОЛЬКО при активном режиме
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, on_premium_input),
        group=3,
    )
