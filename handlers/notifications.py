from telegram import Update
from telegram.ext import ContextTypes

# -----------------------------------------
# УВЕДОМЛЕНИЯ ПОЛЬЗОВАТЕЛЯМ
# -----------------------------------------
async def notify_premium_activated(context: ContextTypes.DEFAULT_TYPE, user_id: int, days: int):
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "⭐ Premium активирован!\n\n"
                f"Срок: {days} дней.\n"
                "Теперь вам доступна расширенная аналитика и рекомендации.\n\n"
                "Удачи в бизнесе 🚀"
            ),
        )
    except Exception:
        pass


async def notify_premium_revoked(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "❌ Premium отключён.\n\n"
                "Доступ к расширенным функциям завершён.\n"
                "Если это ошибка — обратитесь к менеджеру."
            ),
        )
    except Exception:
        pass
