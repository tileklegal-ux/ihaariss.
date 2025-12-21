# handlers/owner.py

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters

from database.db import (
    get_user_role,
    ensure_user_exists,
    get_total_users,
    get_premium_users,
    get_managers_count,
)

from handlers.role_actions import add_manager, remove_manager

OWNER_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["📊 Общая статистика"],
        ["➕ Добавить менеджера"],
        ["➖ Удалить менеджера"],
        ["⬅️ Выйти"],
    ],
    resize_keyboard=True,
)

async def owner_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message:
        return

    ensure_user_exists(update.effective_user.id)
    context.user_data.clear()

    await update.message.reply_text(
        "👑 Панель владельца",
        reply_markup=OWNER_KEYBOARD,
    )

async def owner_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message

    if not user or not message or not message.text:
        return

    if get_user_role(user.id) != "owner":
        return

    text = message.text.strip()

    if text == "⬅️ Выйти":
        context.user_data.clear()
        await owner_start(update, context)
        return

    if text == "📊 Общая статистика":
        total = get_total_users()
        premium = get_premium_users()
        managers = get_managers_count()

        await message.reply_text(
            "📊 Общая статистика\n\n"
            f"👥 Всего пользователей: {total}\n"
            f"⭐ Premium пользователей: {premium}\n"
            f"🧑‍💼 Менеджеров: {managers}"
        )
        return

    if text == "➕ Добавить менеджера":
        context.user_data["await_add_manager"] = True
        await message.reply_text("Отправь Telegram ID менеджера числом.")
        return

    if text == "➖ Удалить менеджера":
        context.user_data["await_remove_manager"] = True
        await message.reply_text("Отправь Telegram ID менеджера для удаления.")
        return

    if context.user_data.get("await_add_manager"):
        context.user_data.pop("await_add_manager", None)
        await add_manager(update, context)
        return

    if context.user_data.get("await_remove_manager"):
        context.user_data.pop("await_remove_manager", None)
        await remove_manager(update, context)
        return

def register_owner_handlers(app):
    app.add_handler(
        MessageHandler(
            filters.Regex(
                r"^(📊 Общая статистика|➕ Добавить менеджера|➖ Удалить менеджера|⬅️ Выйти)$"
            ),
            owner_text_router,
        ),
        group=1,
    )
