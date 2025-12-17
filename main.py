import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import TELEGRAM_TOKEN
from database.db import get_user_role

from handlers.user import cmd_start_user, register_handlers_user
from handlers.owner import owner_start, register_handlers_owner
from handlers.manager import manager_start, register_handlers_manager
from handlers.role_actions import register_role_actions  # ДОБАВИТЬ


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def start_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    role = get_user_role(user_id)

    if role == "owner":
        await owner_start(update, context)
        return

    if role == "manager":
        await manager_start(update, context)
        return

    await cmd_start_user(update, context)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # ЕДИНСТВЕННЫЙ /start ВО ВСЁМ ПРОЕКТЕ
    app.add_handler(CommandHandler("start", start_router), group=0)

    # РОЛЕВЫЕ HANDLERS БЕЗ /start
    register_handlers_owner(app)      # group 1
    register_handlers_manager(app)    # group 2
    register_role_actions(app)        # ДОБАВИТЬ: group 2 (FSM для ролей)
    register_handlers_user(app)       # group 4

    app.run_polling()


if __name__ == "__main__":
    main()
