import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from config import BOT_TOKEN
from database.db import get_user_role

# USER
from handlers.user import (
    cmd_start_user,
    register_handlers_user,
)

# MANAGER
from handlers.manager import (
    register_manager_handlers,
    manager_keyboard,
)

# OWNER
from handlers.owner import register_owner_handlers

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
        role = "user"

    # OWNER и MANAGER НЕ ОБРАБАТЫВАЮТСЯ ТУТ
    if role in ("owner", "manager"):
        return

    # USER
    await cmd_start_user(update, context)


# ==================================================
# MAIN
# ==================================================
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # /start router — ТОЛЬКО ДЛЯ USER
    application.add_handler(
        CommandHandler("start", cmd_start_router),
        group=2,
    )

    # OWNER — САМЫЙ ПЕРВЫЙ
    register_owner_handlers(application)

    # MANAGER
    register_manager_handlers(application)

    # USER
    register_handlers_user(application)

    application.run_polling()


if __name__ == "__main__":
    main()
