import logging
import warnings

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from config import BOT_TOKEN

from database.db import (
    get_user_role,
    create_or_update_user,
)

from handlers.user import (
    cmd_start_user,
    register_handlers_user,
)

from handlers.manager import (
    register_manager_handlers,
    manager_keyboard,
)

from handlers.owner import (
    owner_panel,
    register_owner_handlers,
)

warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def cmd_start_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or ""
    first_name = user.first_name or ""

    # 1) Всегда фиксируем пользователя в базе (не меняет UX, но чинит роли/поиск по @username)
    try:
        create_or_update_user(user_id, username, first_name)
    except Exception:
        logger.exception("create_or_update_user failed")

    # 2) Роутинг по ролям
    try:
        role = get_user_role(user_id)
    except Exception:
        logger.exception("get_user_role failed, fallback to user")
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

    await cmd_start_user(update, context)


def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # /start должен быть самым первым и стабильным
    application.add_handler(CommandHandler("start", cmd_start_router), group=0)

    # OWNER / MANAGER / USER
    register_owner_handlers(application)
    register_manager_handlers(application)
    register_handlers_user(application)

    application.run_polling()


if __name__ == "__main__":
    main()
