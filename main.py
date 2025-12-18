# main.py  (DEPLOY)

import logging

from telegram.ext import Application

from config import TELEGRAM_TOKEN
from database.db import init_db
from handlers.user import (
    register_handlers_user,
    cmd_start_user,
)
from telegram.ext import CommandHandler


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def main():
    init_db()

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # /start — ТОЛЬКО user.py (канон)
    app.add_handler(CommandHandler("start", cmd_start_user), group=0)

    # пользовательский роутер (FSM, кнопки, AI, premium)
    register_handlers_user(app)

    app.run_polling()


if __name__ == "__main__":
    main()
