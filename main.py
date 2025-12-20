# main.py
import os
import logging

from telegram.ext import Application

from database.db import init_db
from handlers.start import register_start_handlers
from handlers.owner import register_owner_handlers
from handlers.manager import register_manager_handlers
from handlers.user import register_handlers_user

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set")

    init_db()

    # Создаем приложение
    app = Application.builder().token(token).build()

    # ПОРЯДОК = ПРИОРИТЕТ
    register_start_handlers(app)     # /start - группа 0
    register_owner_handlers(app)     # OWNER - группа 1
    register_manager_handlers(app)   # MANAGER - группа 1
    register_handlers_user(app)      # USER - группа 1 (последний)

    logger.info("Бот запускается...")
    
    # Запускаем бота с обработкой pending updates
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()
