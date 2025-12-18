from telegram import Update
from telegram.ext import ContextTypes
from database.db import set_user_role, get_user_role


OWNER_ID = 1974482384


async def add_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Нет доступа")
        return

    if not context.args:
        await update.message.reply_text("Передай telegram_id менеджера")
        return

    manager_id = int(context.args[0])
    set_user_role(manager_id, "manager")
    await update.message.reply_text("Менеджер добавлен")


async def remove_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Нет доступа")
        return

    if not context.args:
        await update.message.reply_text("Передай telegram_id менеджера")
        return

    manager_id = int(context.args[0])
    set_user_role(manager_id, "user")
    await update.message.reply_text("Менеджер удалён")
