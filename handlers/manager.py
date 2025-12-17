# handlers/manager.py

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
        "👨‍💼 **Панель менеджера**\n\n"
        "Доступные действия:\n"
        "• Выдача Premium пользователям\n\n"
        "**Инструкция:**\n"
        "1. Нажмите '⭐ Выдать Premium'\n"
        "2. Введите username пользователя (без @)\n"
        "3. Укажите количество дней\n"
        "4. Подтвердите выдачу\n\n"
        "Примечание: пользователь должен сначала запустить бота (/start)",
        reply_markup=manager_keyboard(),
        parse_mode="Markdown",
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
        context.user_data.clear()
        await update.message.reply_text("Выход из панели менеджера.")
        return


def register_handlers_manager(app):
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, manager_text_router),
        group=3,
    )
