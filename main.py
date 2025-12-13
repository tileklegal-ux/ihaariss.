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
from database.db import init_db, create_or_update_user, get_user_role

# USER
from handlers.user import register_handlers_user, cmd_start_user

# OWNER
from handlers.owner import owner_panel, register_owner_handlers

# MANAGER
from handlers.manager import register_manager_handlers

# AUDIT LOG
from services.audit_log import init_audit_log

warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ==================================================
# MIDDLEWARE — сохраняем пользователя в БД
# НЕ перехватывает команды
# ==================================================
async def save_user_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user:
        u = update.effective_user
        create_or_update_user(
            u.id,
            u.username or "",
            u.first_name or "",
        )


# ==================================================
# /start — ЕДИНАЯ ТОЧКА ВХОДА ПО РОЛЯМ
# ==================================================
async def cmd_start_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = get_user_role(update.effective_user.id)

    if role == "owner":
        await owner_panel(update, context)
        return

    if role == "manager":
        await update.message.reply_text(
            "🧑‍💼 Режим менеджера\n\n"
            "Используй кнопку ниже для активации Premium пользователям."
        )
        return

    # user (по умолчанию)
    await cmd_start_user(update, context)


# ==================================================
# MAIN
# ==================================================
def main():
    # 1) DB
    init_db()

    # 2) AUDIT LOG
    init_audit_log()

    # 3) APP
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    # 4) MIDDLEWARE — САМЫЙ ПЕРВЫЙ
    application.add_handler(
        MessageHandler(filters.ALL & ~filters.COMMAND, save_user_middleware),
        group=-1,
    )

    # 5) /start router — ПЕРВЫМ
    application.add_handler(
        CommandHandler("start", cmd_start_router),
        group=0,
    )

    # 6) OWNER
    register_owner_handlers(application)

    # 7) MANAGER
    register_manager_handlers(application)

    # 8) USER
    register_handlers_user(application)

    # 9) RUN
    application.run_polling()


if __name__ == "__main__":
    main()
