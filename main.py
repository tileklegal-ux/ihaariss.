# main.py

import os
import logging
from telegram import Update
from telegram.ext import Application

from database.db import init_db
from handlers.start import register_start_handlers
from handlers.owner import register_owner_handlers
from handlers.manager import register_manager_handlers
from handlers.user import register_handlers_user

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set")

    init_db()

    app = Application.builder().token(token).build()

    # START / role routing
    register_start_handlers(app)

    # ⚠️ КРИТИЧЕСКОЕ РАЗВЕДЕНИЕ ПО ГРУППАМ
    # owner -> group 0
    # manager -> group 1
    # user -> group 2
    register_owner_handlers(app)      # group=0
    register_manager_handlers(app)    # group=1
    register_handlers_user(app)       # group=2

    logger.info("Бот запускается...")

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
        close_loop=False,
    )


if __name__ == "__main__":
    main()
