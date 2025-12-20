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

    # КРИТИЧЕСКИЙ ПОРЯДОК: manager ПЕРВЫЙ
    register_start_handlers(app)
    register_manager_handlers(app)    # <-- ПЕРВЫЙ в группе 1
    register_owner_handlers(app)      # <-- ВТОРОЙ
    register_handlers_user(app)       # <-- ТРЕТИЙ

    logger.info("Бот запускается...")
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
        close_loop=False,
    )

if __name__ == "__main__":
    main()
