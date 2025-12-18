import logging

from telegram.ext import Application

from config import TELEGRAM_TOKEN
from database.db import init_db

from handlers.start import register_start_handlers
from handlers.user import register_handlers_user
from handlers.owner import register_owner_handlers
from handlers.manager import register_manager_handlers


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def main():
    init_db()

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # /start — единый вход
    register_start_handlers(app)

    # handlers по ролям
    register_owner_handlers(app)
    register_manager_handlers(app)
    register_handlers_user(app)

    app.run_polling()


if __name__ == "__main__":
    main()
