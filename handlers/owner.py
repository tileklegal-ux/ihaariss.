# handlers/owner.py

import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    Application,
)

from database.db import get_user_role

logger = logging.getLogger(__name__)

# =========================
# OWNER KEYBOARD
# =========================

BTN_OWNER_USERS = "👥 Пользователи"
BTN_OWNER_PREMIUM = "💳 Premium"
BTN_OWNER_MANAGERS = "🧑‍💼 Менеджеры"
BTN_OWNER_BACK = "⬅️ Выйти в главное меню"

def owner_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_OWNER_USERS), KeyboardButton(BTN_OWNER_PREMIUM)],
            [KeyboardButton(BTN_OWNER_MANAGERS)],
            [KeyboardButton(BTN_OWNER_BACK)],
        ],
        resize_keyboard=True,
    )

# =========================
# /start — OWNER ENTRY POINT
# =========================

async def owner_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        role = get_user_role(update.effective_user.id)
    except Exception:
        logger.exception("get_user_role failed in owner_start")
        return

    if role != "owner":
        return

    context.user_data.clear()

    await update.message.reply_text(
        "👑 Панель владельца\n\n"
        "Здесь ты управляешь системой:\n"
        "• пользователями\n"
        "• менеджерами\n"
        "• Premium-доступом\n\n"
        "Выбери действие 👇",
        reply_markup=owner_keyboard(),
    )

# =========================
# OWNER TEXT ROUTER
# =========================

async def owner_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        role = get_user_role(update.effective_user.id)
    except Exception:
        logger.exception("get_user_role failed in owner_text_router")
        return

    if role != "owner":
        return

    text = update.message.text or ""

    if text == BTN_OWNER_USERS:
        await update.message.reply_text(
            "👥 Пользователи\n\n"
            "Здесь будет управление пользователями.\n"
            "(просмотр, статусы, активность)",
            reply_markup=owner_keyboard(),
        )
        return

    if text == BTN_OWNER_PREMIUM:
        await update.message.reply_text(
            "💳 Premium\n\n"
            "Здесь будет управление Premium-доступом:\n"
            "• активация\n"
            "• продление\n"
            "• проверка статуса",
            reply_markup=owner_keyboard(),
        )
        return

    if text == BTN_OWNER_MANAGERS:
        await update.message.reply_text(
            "🧑‍💼 Менеджеры\n\n"
            "Здесь ты назначаешь и снимаешь менеджеров.\n"
            "Менеджер получает свою панель и доступы.",
            reply_markup=owner_keyboard(),
        )
        return

    if text == BTN_OWNER_BACK:
        await update.message.reply_text(
            "Выход из панели владельца.",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("/start")]],
                resize_keyboard=True,
            ),
        )
        return

# =========================
# REGISTER
# =========================

def register_handlers_owner(app: Application):
    """
    OWNER handlers.
    Должны регистрироваться РАНЬШЕ user.py
    """
    app.add_handler(CommandHandler("start", owner_start), group=1)
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, owner_text_router),
        group=1,
    )
