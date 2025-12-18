from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from handlers.role_actions import add_manager, remove_manager
from handlers.owner_stats import show_owner_stats
from database.db import get_user_role


async def owner_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = get_user_role(update.effective_user.id)

    if role != "owner":
        await update.message.reply_text("Доступ только для владельца.")
        return

    await update.message.reply_text(
        "👑 Панель владельца\n\n"
        "/add_manager @username\n"
        "/remove_manager @username\n"
        "/owner_stats"
    )


def register_handlers_owner(app):
    app.add_handler(CommandHandler("owner", owner_start))
    app.add_handler(CommandHandler("add_manager", add_manager))
    app.add_handler(CommandHandler("remove_manager", remove_manager))
    app.add_handler(CommandHandler("owner_stats", show_owner_stats))
