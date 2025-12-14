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

# USER HANDLERS
from handlers.user import (
    cmd_start_user,
    register_handlers_user,
)

warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ==================================================
# MIDDLEWARE — сохраняем пользователя (НЕ ломает FSM)
# ==================================================
async def save_user_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ничего не перехватываем, просто фиксируем факт пользователя
    if update.effective_user:
        pass


# ==================================================
# MAIN
# ==================================================
def main():
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    # 1️⃣ Middleware — САМЫЙ ПЕРВЫЙ
    application.add_handler(
        MessageHandler(filters.ALL & ~filters.COMMAND, save_user_middleware),
        group=-1,
    )

    # 2️⃣ /start — КАНОНИЧЕСКАЯ ТОЧКА ВХОДА
    application.add_handler(
        CommandHandler("start", cmd_start_user),
        group=0,
    )

    # 3️⃣ USER FSM И МЕНЮ
    register_handlers_user(application)

    # 4️⃣ RUN
    application.run_polling()


if __name__ == "__main__":
    main()
