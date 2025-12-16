# handlers/owner.py

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

BTN_OWNER_STATS = "📊 Общая статистика"
BTN_OWNER_ADD_MANAGER = "➕ Добавить менеджера"
BTN_OWNER_REMOVE_MANAGER = "➖ Удалить менеджера"

def owner_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_OWNER_STATS)],
            [KeyboardButton(BTN_OWNER_ADD_MANAGER)],
            [KeyboardButton(BTN_OWNER_REMOVE_MANAGER)],
        ],
        resize_keyboard=True,
    )

async def owner_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == "/start":
        await update.message.reply_text(
            "👑 Панель владельца\n\n"
            "Доступ:\n"
            "— общая статистика\n"
            "— управление менеджерами\n\n"
            "Пользовательские функции недоступны.",
            reply_markup=owner_keyboard(),
        )
        return

    if text == BTN_OWNER_STATS:
        await update.message.reply_text("📊 Здесь будет общая статистика")
        return

    if text == BTN_OWNER_ADD_MANAGER:
        await update.message.reply_text("➕ Логика добавления менеджера")
        return

    if text == BTN_OWNER_REMOVE_MANAGER:
        await update.message.reply_text("➖ Логика удаления менеджера")
        return

    await update.message.reply_text("Команда недоступна в панели владельца.")
