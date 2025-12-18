# handlers/start.py

from telegram.ext import CommandHandler
from telegram import Update
from telegram.ext import ContextTypes

from database.db import ensure_user_exists, get_user_role

from handlers.owner import owner_start
from handlers.manager import manager_start
from handlers.user import cmd_start_user


async def start_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # гарантируем, что пользователь есть в БД
    ensure_user_exists(
        user_id=user.id,
        username=user.username,
    )

    role = get_user_role(user.id)

    if role == "owner":
        await owner_start(update, context)
        return

    if role == "manager":
        await manager_start(update, context)
        return

    # КАНОН: user.py — мозг
    await cmd_start_user(update, context)


def register_start_handlers(app):
    app.add_handler(CommandHandler("start", start_router))
