from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters

from database.db import get_user_role
from handlers.role_actions import add_manager, remove_manager
from handlers.owner_stats import show_owner_stats


OWNER_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["📊 Общая статистика"],
        ["➕ Добавить менеджера", "➖ Удалить менеджера"],
        ["⬅️ Выйти"],
    ],
    resize_keyboard=True,
)


async def owner_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👑 Панель владельца",
        reply_markup=OWNER_KEYBOARD,
    )


async def owner_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if get_user_role(user_id) != "owner":
        return

    text = update.message.text

    if text == "📊 Общая статистика":
        await show_owner_stats(update, context)
        return

    if text == "➕ Добавить менеджера":
        context.user_data["await_action"] = "add_manager"
        await update.message.reply_text(
            "➕ Добавление менеджера\n\n"
            "Отправь Telegram ID пользователя, которого нужно сделать менеджером.\n\n"
            "Как узнать Telegram ID:\n"
            "1️⃣ Напиши боту @userinfobot\n"
            "2️⃣ Скопируй ID\n"
            "3️⃣ Пришли сюда числом"
        )
        return

    if text == "➖ Удалить менеджера":
        context.user_data["await_action"] = "remove_manager"
        await update.message.reply_text(
            "➖ Удаление менеджера\n\n"
            "Отправь Telegram ID менеджера, которого нужно удалить.\n\n"
            "Telegram ID — это число."
        )
        return

    if text == "⬅️ Выйти":
        context.user_data.clear()
        await update.message.reply_text("Выход из панели владельца")
        return


def register_owner_handlers(app):
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, owner_text_router),
        group=1,
    )
