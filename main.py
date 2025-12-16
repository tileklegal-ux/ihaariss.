# main.py

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
from handlers.owner import (
    owner_panel,
    register_owner_handlers,
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
        # Если БД временно недоступна — считаем user
        role = "user"

    if role == "owner":
        await owner_panel(update, context)
        return

    if role == "manager":
        await update.message.reply_text(
            "🧑‍💼 Панель менеджера",
            reply_markup=manager_keyboard(),
        )
        return

    # default: user
    await cmd_start_user(update, context)


# ==================================================
# MAIN
# ==================================================
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # /start — ВСЕГДА ПЕРВЫМ
    application.add_handler(
        CommandHandler("start", cmd_start_router),
        group=0,
    )

    # OWNER (group 1–2)
    register_owner_handlers(application)

    # MANAGER (group 1–3)
    register_manager_handlers(application)

    # USER (group 4)
    register_handlers_user(application)

    application.run_polling()


if __name__ == "__main__":
    main()
