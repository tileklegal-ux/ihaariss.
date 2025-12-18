from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from database.db import get_user_role
from handlers.owner import owner_start
from handlers.manager import manager_start
from handlers.user import user_start


async def start_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    role = get_user_role(user_id)

    # OWNER — самый высокий приоритет
    if role == "owner":
        await owner_start(update, context)
        return

    # MANAGER
    if role == "manager":
        await manager_start(update, context)
        return

    # USER (по умолчанию)
    await user_start(update, context)


def register_start_handlers(application):
    application.add_handler(CommandHandler("start", start_router), group=0)
