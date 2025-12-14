import logging
import warnings

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN
from handlers.user import cmd_start_user, register_handlers_user

warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def save_user_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ничего не перехватываем, просто не мешаем обработчикам
    if update.effective_user:
        pass


def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(
        MessageHandler(filters.ALL & ~filters.COMMAND, save_user_middleware),
        group=-1,
    )

    application.add_handler(
        CommandHandler("start", cmd_start_user),
        group=0,
    )

    register_handlers_user(application)

    application.run_polling()


if __name__ == "__main__":
    main()
