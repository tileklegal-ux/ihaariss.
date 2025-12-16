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

# EXPORT (PDF / EXCEL)
from handlers.export import (
    export_pdf,
    export_excel,
)

warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ==================================================
# /start — КАНОНИЧЕСКИЙ РОУТЕР ПО РОЛЯМ
# ==================================================
async def cmd_start_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    role = get_user_role(user_id)

    if role == "owner":
        await owner_panel(update, context)
        return

    if role == "manager":
        await update.message.reply_text(
            "🧑‍💼 Панель менеджера",
            reply_markup=manager_keyboard(),
        )
        return

    # user по умолчанию
    await cmd_start_user(update, context)

# ==================================================
# MAIN
# ==================================================
def main():
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    # /start — ВСЕГДА ПЕРВЫМ
    application.add_handler(
        CommandHandler("start", cmd_start_router),
        group=0,
    )

    # OWNER
    register_owner_handlers(application)

    # MANAGER
    register_manager_handlers(application)

    # USER
    register_handlers_user(application)

    # EXPORT
    application.add_handler(
        MessageHandler(filters.Regex("^📄 Скачать PDF$"), export_pdf),
        group=3,
    )

    application.add_handler(
        MessageHandler(filters.Regex("^📊 Скачать Excel$"), export_excel),
        group=3,
    )

    application.run_polling()

if __name__ == "__main__":
    main()
