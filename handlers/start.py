from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from database.db import get_user_role, ensure_user_exists
from handlers.owner import owner_start
from handlers.manager import manager_start
from handlers.user import cmd_start_user


async def start_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    ensure_user_exists(u.id, u.username or "")

    role = get_user_role(u.id)

    if role == "owner":
        await owner_start(update, context)
        return

    if role == "manager":
        await manager_start(update, context)
        return

    await cmd_start_user(update, context)


def register_start_handlers(app):
    app.add_handler(CommandHandler("start", start_router), group=0)
