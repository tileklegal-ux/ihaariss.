import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

from database.db import get_analysis_history
from services.menu import send_main_menu

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# /history — премиум история
# ---------------------------------------------------------
async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Забираем историю из БД
    rows = get_analysis_history(user_id)

    if not rows:
        await update.message.reply_text(
            "История пуста.\nВы ещё не делали анализов.",
        )
        return await send_main_menu(update)

    # Формируем текст истории
    text_lines = ["📜 *История ваших анализов:*", ""]
    for row in rows:
        text_lines.append(f"• {row['created_at']} — {row['data'][:50]}...")

    await update.message.reply_text("\n".join(text_lines), parse_mode="Markdown")

    return await send_main_menu(update)


# ---------------------------------------------------------
# РЕГИСТРАЦИЯ
# ---------------------------------------------------------
def register_history_handlers(app):
    app.add_handler(CommandHandler("history", history_command))

    # Кнопка "📜 История" тоже ведёт сюда
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^📜 История$"),
            history_command
        )
    )
