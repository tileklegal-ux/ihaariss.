import logging
import warnings

from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN
from database.db import init_db, create_or_update_user
from handlers.user import register_handlers_user

# AUDIT LOG
from services.audit_log import init_audit_log

warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# middleware — записывать пользователя в БД
# ВАЖНО: НЕ перехватывает команды (/start и т.п.)
# ---------------------------------------------------------
async def save_user_middleware(update, context):
    if update.effective_user:
        u = update.effective_user
        create_or_update_user(
            u.id,
            u.username or "",
            u.first_name or "",
        )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main():
    # 1) Инициализация базы пользователей
    init_db()

    # 2) Инициализация AUDIT LOG
    init_audit_log()

    # 3) Создаём приложение
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    # 4) middleware — ТОЛЬКО не-командные апдейты
    application.add_handler(
        MessageHandler(filters.ALL & ~filters.COMMAND, save_user_middleware),
        group=-1
    )

    # 5) handlers (user + owner + manager)
    register_handlers_user(application)

    # 6) Запуск
    application.run_polling()


if __name__ == "__main__":
    main()
