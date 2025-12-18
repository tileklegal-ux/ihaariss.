from telegram import Update
from telegram.ext import ContextTypes

from database.db import ensure_user_exists, set_user_role


async def add_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not text.isdigit():
        await update.message.reply_text(
            "❌ Нужно отправить Telegram ID числом."
        )
        return

    manager_id = int(text)

    # гарантируем, что пользователь есть в БД
    ensure_user_exists(user_id=manager_id)

    # назначаем роль
    set_user_role(manager_id, "manager")

    await update.message.reply_text(
        f"✅ Пользователь с ID {manager_id} назначен менеджером."
    )


async def remove_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not text.isdigit():
        await update.message.reply_text(
            "❌ Нужно отправить Telegram ID числом."
        )
        return

    manager_id = int(text)

    ensure_user_exists(user_id=manager_id)
    set_user_role(manager_id, "user")

    await update.message.reply_text(
        f"➖ Роль менеджера у пользователя {manager_id} удалена."
    )
