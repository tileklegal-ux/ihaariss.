# -*- coding: utf-8 -*-
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
BTN_EXPORT_PDF = "📄 Скачать PDF"
BTN_EXPORT_EXCEL = "📊 Скачать Excel"

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

def premium_profile_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_EXPORT_PDF), KeyboardButton(BTN_EXPORT_EXCEL)],
            [KeyboardButton("⬅️ Главное меню")],
        ],
        resize_keyboard=True,
    )

# ==================================================
# DB helpers
# ==================================================

def _db_path() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "database", "artbazar.db")


def _get_user_by_username(username: str):
    conn = sqlite3.connect(_db_path())
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT telegram_id FROM users WHERE username = ?",
            (username,),
        )
        return cur.fetchone()
    finally:
        conn.close()


def set_premium_by_telegram_id(telegram_id: int, days: int):
    conn = sqlite3.connect(_db_path())
    try:
        cur = conn.cursor()
        now = datetime.utcnow()
        premium_until = (now + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

        cur.execute(
            """
            UPDATE users
            SET is_premium = 1,
                premium_until = ?,
                updated_at = ?
            WHERE telegram_id = ?
            """,
            (premium_until, now.strftime("%Y-%m-%d %H:%M:%S"), telegram_id),
        )
        conn.commit()
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
        "`@test_user 7`",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )


async def on_premium_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if get_user_role(update.effective_user.id) != "manager":
        return

    if not context.user_data.get(FSM_WAIT_PREMIUM_INPUT):
        return

    text = (update.message.text or "").strip()
    parts = text.split()

    if len(parts) != 2 or not parts[0].startswith("@") or not parts[1].isdigit():
        await update.message.reply_text(
            "❌ Неверный формат.\nИспользуй:\n`@username дни`",
            parse_mode="Markdown",
        )
        return

    username = parts[0].replace("@", "").strip()
    days = int(parts[1])

    row = _get_user_by_username(username)
    if not row:
        await update.message.reply_text("❌ Пользователь не найден в базе.")
        return

    telegram_id = row[0]
    set_premium_by_telegram_id(telegram_id, days)

    context.user_data.pop(FSM_WAIT_PREMIUM_INPUT, None)

    # ===============================
    # 🔔 УВЕДОМЛЕНИЕ ПОЛЬЗОВАТЕЛЮ
    # + АВТО-ВХОД В КАБИНЕТ
    # ===============================

    try:
        await context.bot.send_message(
            chat_id=telegram_id,
            text=(
                "🎉 *Premium активирован!*\n\n"
                f"⏳ Срок: *{days} дней*\n\n"
                "Теперь доступны:\n"
                "• история анализов\n"
                "• экспорт в PDF и Excel\n\n"
                "Я сразу открыл твой личный кабинет 👇"
            ),
            parse_mode="Markdown",
        )

        await context.bot.send_message(
            chat_id=telegram_id,
            text=(
                "👤 *Личный кабинет*\n\n"
                "Статус: ⭐ *Premium активен*\n\n"
                "Здесь собраны твои результаты.\n"
                "Ты можешь скачать отчёты в PDF или Excel."
            ),
            parse_mode="Markdown",
            reply_markup=premium_profile_keyboard(),
        )
    except Exception:
        pass

    # Ответ менеджеру
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

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, on_premium_input),
        group=3,
    )
