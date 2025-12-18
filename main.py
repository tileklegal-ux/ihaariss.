# main.py
import os
import logging

from telegram.ext import Application

from database.db import init_db
from handlers.start import register_start_handlers

# твой user.py НЕ трогаем — просто импортируем то, что реально существует
from handlers.user import register_handlers_user

# эти модули у тебя есть в проекте (по скринам)
from handlers.owner import register_handlers_owner
from handlers.role_actions import register_role_actions

# manager.py существует у тебя по списку файлов
from handlers.manager import register_handlers_manager


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def build_app() -> Application:
    token = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Не найден BOT_TOKEN (или TELEGRAM_BOT_TOKEN) в переменных окружения Railway.")

    app = Application.builder().token(token).build()

    # база
    init_db()

    # handlers
    register_start_handlers(app)
    register_handlers_user(app)
    register_handlers_owner(app)
    register_role_actions(app)
    register_handlers_manager(app)

    return app


def main():
    app = build_app()
    # Polling (без вебхука)
    app.run_polling(allowed_updates=None)


if __name__ == "__main__":
    main()
