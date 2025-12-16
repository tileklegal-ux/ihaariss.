import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from config import BOT_TOKEN

from database.db import get_user_role, init_db

from handlers.user import (
    cmd_start_user,
    register_handlers_user,
)

from handlers.manager import (
    register_manager_handlers,
    manager_keyboard,
)

from handlers.owner import (
    owner_start,
    register_handlers_owner,
)

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ==================================================
# /start — ЕДИНАЯ ТОЧКА ВХОДА
# ==================================================
async def cmd_start_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    try:
        role = get_user_role(user_id)
    except Exception:
        logger.exception("get_user_role failed in cmd_start_router")
        role = "user"

    if role == "owner":
        await owner_start(update, context)
        return

    if role == "manager":
        await update.message.reply_text(
            "🧑‍💼 Панель менеджера",
            reply_markup=manager_keyboard(),
        )
        return

    await cmd_start_user(update, context)


# ==================================================
# MAIN
# ==================================================
def main():
    init_db()

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", cmd_start_router), group=0)

    register_handlers_owner(application)
    register_manager_handlers(application)
    register_handlers_user(application)

    application.run_polling()


if __name__ == "__main__":
    main()
