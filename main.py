from dotenv import load_dotenv
load_dotenv()

import logging
from telegram.ext import Application, CommandHandler

from config import BOT_TOKEN
from handlers.owner import owner_command, owner_stats, add_manager, remove_manager
from handlers.manager import give_premium, extend_premium, remove_premium_cmd
from handlers.user import register_user_handlers
from services.premium_checker import check_premium_expiration

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


async def start(update, context):
    await update.message.reply_text("Artbazar AI бот запущен")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Базовая команда
    app.add_handler(CommandHandler("start", start))

    # OWNER
    app.add_handler(CommandHandler("owner", owner_command))
    app.add_handler(CommandHandler("owner_stats", owner_stats))
    app.add_handler(CommandHandler("add_manager", add_manager))
    app.add_handler(CommandHandler("remove_manager", remove_manager))

    # MANAGER (работа по username)
    app.add_handler(CommandHandler("give_premium", give_premium))
    app.add_handler(CommandHandler("extend_premium", extend_premium))
    app.add_handler(CommandHandler("remove_premium", remove_premium_cmd))

    # Premium уведомления — ручной запуск (для теста cron-логики)
    app.add_handler(CommandHandler("check_premium", check_premium_expiration))

    # USER-флоу (таблица, анализ, экспорт)
    register_user_handlers(app)

    app.run_polling()


if __name__ == "__main__":
    main()
