import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import BOT_TOKEN
from handlers.owner import owner_start, register_handlers_owner
from handlers.user import handle_user_message
from handlers.role_actions import role_text_router
from database.db import ensure_user_exists


logging.basicConfig(level=logging.INFO)


async def start(update, context):
    user = update.effective_user
    ensure_user_exists(user.id, user.username)
    await update.message.reply_text("👋 Добро пожаловать в ArtBazar AI!")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    register_handlers_owner(app)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, role_text_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))

    app.run_polling()


if __name__ == "__main__":
    main()
