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
    manager_panel,
    register_manager_handlers,
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
        role = get_user_role(user_id) or "user"
    except Exception:
        logger.exception("get_user_role failed in /start router")
        role = "user"

    # Сбрасываем transient состояние на входе (чтобы не залипали FSM)
    try:
        context.user_data.clear()
    except Exception:
        pass

    if role == "owner":
        await owner_panel(update, context)
        return

    if role == "manager":
        await manager_panel(update, context)
        return

    await cmd_start_user(update, context)


def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # /start — всегда один, всегда первый, и блокирует остальные группы
    application.add_handler(
        CommandHandler("start", cmd_start_router),
        group=0,
    )

    # Важно: owner/manager/user регистрируют ТОЛЬКО текстовые/кнопочные хендлеры
    register_owner_handlers(application)     # group=1
    register_manager_handlers(application)   # group=2
    register_handlers_user(application)      # group=4

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
