from telegram.ext import Application
from config import BOT_TOKEN
from database.db import init_db

from handlers.start import register_start_handlers
from handlers.user import register_user_handlers
from handlers.owner import register_handlers_owner
from handlers.manager import register_handlers_manager


def main():
    init_db()

    application = Application.builder().token(BOT_TOKEN).build()

    # /start — всегда первый
    register_start_handlers(application)

    # дальше по ролям
    register_handlers_owner(application)
    register_handlers_manager(application)
    register_user_handlers(application)

    application.run_polling()


if __name__ == "__main__":
    main()
