from telegram import Update
from telegram.ext import ContextTypes

from database.db import (
    get_user_role,
    set_user_role,
    get_user_by_username
)
from services.audit_log import log_event


async def add_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if get_user_role(user.id) != "owner":
        await update.callback_query.message.reply_text("❌ Только владелец.")
        return

    await update.callback_query.message.reply_text(
        "Введите username пользователя (без @), которого нужно сделать менеджером:"
    )
    context.user_data["awaiting_manager_add"] = True


async def remove_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if get_user_role(user.id) != "owner":
        await update.callback_query.message.reply_text("❌ Только владелец.")
        return

    await update.callback_query.message.reply_text(
        "Введите username менеджера (без @), которого нужно удалить:"
    )
    context.user_data["awaiting_manager_remove"] = True


async def role_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "awaiting_manager_add" in context.user_data:
        username = update.message.text.strip()
        target = get_user_by_username(username)

        if not target:
            await update.message.reply_text("❌ Пользователь не найден.")
        else:
            set_user_role(target["telegram_id"], "manager")
            await update.message.reply_text("✅ Менеджер добавлен.")
            log_event(user_id=target["telegram_id"], action="role_changed", details="Promoted to manager")

        context.user_data.pop("awaiting_manager_add")
        return

    if "awaiting_manager_remove" in context.user_data:
        username = update.message.text.strip()
        target = get_user_by_username(username)

        if not target:
            await update.message.reply_text("❌ Пользователь не найден.")
        else:
            set_user_role(target["telegram_id"], "user")
            await update.message.reply_text("✅ Менеджер удалён.")
            log_event(user_id=target["telegram_id"], action="role_changed", details="Demoted to user")

        context.user_data.pop("awaiting_manager_remove")
