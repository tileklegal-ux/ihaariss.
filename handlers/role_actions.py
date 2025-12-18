from telegram import Update
from telegram.ext import ContextTypes

from database.db import (
    ensure_user_exists,
    set_user_role,
)


async def add_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Ожидает Telegram ID менеджера числом
    """
    text = update.message.text.strip()

    try:
        manager_id = int(text)
    except ValueError:
        await update.message.reply_text("❌ Telegram ID должен быть числом")
        return

    # гарантируем пользователя в БД
    ensure_user_exists(manager_id)

    # назначаем роль
    set_user_role(manager_id, "manager")

    context.user_data.pop("await_username", None)

    await update.message.reply_text(
        f"✅ Менеджер добавлен\n\n"
        f"Telegram ID: {manager_id}"
    )


async def remove_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Ожидает Telegram ID менеджера числом
    """
    text = update.message.text.strip()

    try:
        manager_id = int(text)
    except ValueError:
        await update.message.reply_text("❌ Telegram ID должен быть числом")
        return

    # возвращаем роль user
    set_user_role(manager_id, "user")

    context.user_data.pop("await_username", None)

    await update.message.reply_text(
        f"✅ Менеджер удалён\n\n"
        f"Telegram ID: {manager_id}"
    )
