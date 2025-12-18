from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from database.db import ensure_user_exists, get_user_role
from handlers.owner import owner_start
from handlers.manager import manager_start

# ВАЖНО: user.py канон, мы не переписываем его логику.
# В твоей иерархии старт у USER — это cmd_start_user()
from handlers.user import cmd_start_user


def register_start_handlers(app):
    app.add_handler(CommandHandler("start", start_router))


async def start_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user

    # Создаём/обновляем пользователя в БД
    # (username может быть None)
    ensure_user_exists(
        telegram_id=u.id,
        username=u.username,
        first_name=u.first_name,
        last_name=u.last_name,
    )

    role = get_user_role(u.id)

    if role == "owner":
        await owner_start(update, context)
        return

    if role == "manager":
        await manager_start(update, context)
        return

    # USER
    await cmd_start_user(update, context)
