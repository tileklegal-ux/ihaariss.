# handlers/manager.py
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

from database.db import get_user_role

BTN_MANAGER_INFO = "📋 Задачи"
BTN_EXIT = "⬅️ Выйти"

def manager_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_MANAGER_INFO)],
            [KeyboardButton(BTN_EXIT)],
        ],
        resize_keyboard=True,
    )

async def manager_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧑‍💼 Панель менеджера\n\n"
        "Доступ только к рабочим задачам.",
        reply_markup=manager_keyboard(),
    )

async def manager_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = get_user_role(update.effective_user.id)
    if role != "manager":
        return

    text = update.message.text

    if text == BTN_MANAGER_INFO:
        await update.message.reply_text("📋 Список задач менеджера.")
        return

    if text == BTN_EXIT:
        await update.message.reply_text("Выход из панели менеджера.")
        return

def register_handlers_manager(app):
    app.add_handler(CommandHandler("manager", manager_start), group=2)
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, manager_text_router),
        group=2,
    )
