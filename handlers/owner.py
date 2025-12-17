# handlers/owner.py

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters

from database.db import get_user_role
from handlers.owner_stats import show_owner_stats
from handlers.role_actions import add_manager, remove_manager


BTN_OWNER_STATS = "📊 Общая статистика"
BTN_ADD_MANAGER = "➕ Добавить менеджера"
BTN_REMOVE_MANAGER = "➖ Удалить менеджера"
BTN_EXIT = "⬅️ Выйти"


def owner_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_OWNER_STATS)],
            [KeyboardButton(BTN_ADD_MANAGER), KeyboardButton(BTN_REMOVE_MANAGER)],
            [KeyboardButton(BTN_EXIT)],
        ],
        resize_keyboard=True,
    )


async def owner_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = get_user_role(update.effective_user.id)
    if role != "owner":
        return

    await update.message.reply_text(
        "👑 Панель владельца\n\n"
        "Доступ:\n"
        "• Общая статистика\n"
        "• Управление менеджерами",
        reply_markup=owner_keyboard(),
    )


async def owner_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = get_user_role(update.effective_user.id)
    if role != "owner":
        return

    text = update.message.text or ""

    if text == BTN_OWNER_STATS:
        await show_owner_stats(update, context)
        return

    if text == BTN_ADD_MANAGER:
        await add_manager(update, context)
        return

    if text == BTN_REMOVE_MANAGER:
        await remove_manager(update, context)
        return

    if text == BTN_EXIT:
        # Сбрасываем все состояния
        context.user_data.clear()
        await update.message.reply_text("Выход из панели владельца.")
        return


def register_handlers_owner(app):
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, owner_text_router),
        group=2,  # ВТОРАЯ группа - после FSM
    )
