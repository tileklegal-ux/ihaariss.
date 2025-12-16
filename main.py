import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from config import BOT_TOKEN
from database.db import get_user_role

from handlers.user import cmd_start_user, register_handlers_user
from handlers.owner import owner_panel, register_owner_handlers
from handlers.manager import manager_panel, register_manager_handlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def cmd_start_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    try:
        role = get_user_role(user_id)
    except Exception:
        role = "user"

    if role == "owner":
        await owner_panel(update, context)
        return

    if role == "manager":
        await manager_panel(update, context)
        return

    await cmd_start_user(update, context)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start_router), group=0)

    register_owner_handlers(app)
    register_manager_handlers(app)
    register_handlers_user(app)

    app.run_polling()


if __name__ == "__main__":
    main()
