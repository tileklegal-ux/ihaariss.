# handlers/manager.py - нужно создать или обновить

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters

from database.db import get_user_role
from handlers.role_actions import give_premium_start, BTN_GIVE_PREMIUM, BTN_EXIT


def manager_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_GIVE_PREMIUM)],
            [KeyboardButton(BTN_EXIT)],
        ],
        resize_keyboard=True,
    )


async def manager_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = get_user_role(update.effective_user.id)
    if role != "manager":
        return

    await update.message.reply_text(
        "👨‍💼 Панель менеджера\n\n"
        "Доступ:\n"
        "• Выдача Premium пользователям",
        reply_markup=manager_keyboard(),
    )


async def manager_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = get_user_role(update.effective_user.id)
    if role != "manager":
        return

    text = update.message.text or ""

    if text == BTN_GIVE_PREMIUM:
        await give_premium_start(update, context)
        return

    if text == BTN_EXIT:
        # Сбрасываем все состояния
        context.user_data.clear()
        await update.message.reply_text("Выход из панели менеджера.")
        return


def register_handlers_manager(app):
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, manager_text_router),
        group=2,
    )
