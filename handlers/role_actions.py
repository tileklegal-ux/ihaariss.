from telegram import Update
from telegram.ext import ContextTypes

from database.db import (
    ensure_user_exists,
    set_user_role,
    get_user_role,
)


async def add_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Ожидает Telegram ID менеджера обычным числом.
    """
    text = update.message.text.strip()

    if not text.isdigit():
        await update.message.reply_text(
            "❌ Telegram ID должен быть числом."
        )
        return

    manager_id = int(text)

    # создаём пользователя, если его ещё нет
    ensure_user_exists(manager_id)

    # назначаем роль
    set_user_role(manager_id, "manager")

    await update.message.reply_text(
        f"✅ Пользователь с ID {manager_id} назначен менеджером."
    )

    # сбрасываем ожидание
    context.user_data.pop("await_username", None)


async def remove_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Удаление менеджера по Telegram ID
    """
    text = update.message.text.strip()

    if not text.isdigit():
        await update.message.reply_text(
            "❌ Telegram ID должен быть числом."
        )
        return

    manager_id = int(text)

    role = get_user_role(manager_id)
    if role != "manager":
        await update.message.reply_text(
            "❌ У этого пользователя нет роли менеджера."
        )
        return

    set_user_role(manager_id, "user")

    await update.message.reply_text(
        f"🗑 Менеджер с ID {manager_id} удалён."
    )

    context.user_data.pop("await_username", None)
