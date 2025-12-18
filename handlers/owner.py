# handlers/owner.py
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

ADD_MANAGER_TEXT = (
    "➕ Добавление менеджера\n\n"
    "Отправь Telegram ID пользователя, которого нужно сделать менеджером.\n\n"
    "Как узнать Telegram ID:\n"
    "1️⃣ Напиши боту @userinfobot\n"
    "2️⃣ Скопируй ID\n"
    "3️⃣ Пришли сюда числом"
)

REMOVE_MANAGER_TEXT = (
    "➖ Удаление менеджера\n\n"
    "Отправь Telegram ID пользователя, которого нужно снять с роли менеджера.\n\n"
    "Как узнать Telegram ID:\n"
    "1️⃣ Напиши боту @userinfobot\n"
    "2️⃣ Скопируй ID\n"
    "3️⃣ Пришли сюда числом"
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

    text = (update.message.text or "").strip()

    # Awaiting Telegram ID flow
    await_mode = context.user_data.get("await_manager_id")
    if await_mode in ("add", "remove"):
        if text.isdigit():
            if await_mode == "add":
                await add_manager(update, context, int(text))
            else:
                await remove_manager(update, context, int(text))
            context.user_data.pop("await_manager_id", None)
        else:
            await update.message.reply_text("Пришли Telegram ID числом.")
        return

    if text == "📊 Общая статистика":
        await show_owner_stats(update, context)
        return

    if text == "➕ Добавить менеджера":
        context.user_data["await_manager_id"] = "add"
        await update.message.reply_text(ADD_MANAGER_TEXT)
        return

    if text == "➖ Удалить менеджера":
        context.user_data["await_manager_id"] = "remove"
        await update.message.reply_text(REMOVE_MANAGER_TEXT)
        return

    if text == "⬅️ Выйти":
        await update.message.reply_text("Выход из панели владельца")
        return


def register_owner_handlers(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, owner_text_router), group=1)
