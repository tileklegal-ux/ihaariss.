from telegram.ext import Application

from handlers.owner import register_handlers_owner
from database.db import init_db
from user import register_user_handlers  # твой user.py


def main():
    init_db()

    app = Application.builder().token("BOT_TOKEN").build()

    register_user_handlers(app)
    register_handlers_owner(app)

    app.run_polling()


if __name__ == "__main__":
    main()
