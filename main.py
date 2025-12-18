import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from database.db import ensure_user_exists, get_user_role
from handlers.owner import owner_start, register_handlers_owner
from handlers.user import handle_user_message  # <-- ВАЖНО


TOKEN = "ТВОЙ_TOKEN"

OWNER_ID = 1974482384

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    telegram_id = user.id
    username = user.username

    ensure_user_exists(telegram_id, username)

    role = get_user_role(telegram_id)

    if telegram_id == OWNER_ID or role == "owner":
        await owner_start(update, context)
        return

    await update.message.reply_text(
        "Привет! Напиши сообщение, и я помогу 👇"
    )


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_router), group=0)

    # ВСЕ пользовательские сообщения → существующий handler
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message),
        group=1,
    )

    register_handlers_owner(app)

    app.run_polling()


if __name__ == "__main__":
    main()
