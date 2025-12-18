# owner_stats.py
from telegram import Update
from telegram.ext import ContextTypes

from database.db import get_connection


async def show_owner_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:

                # Всего пользователей
                cur.execute("SELECT COUNT(*) FROM users")
                total_users = cur.fetchone()[0]

                # Premium пользователей (активных)
                cur.execute(
                    """
                    SELECT COUNT(*)
                    FROM users
                    WHERE premium_until IS NOT NULL
                      AND premium_until > NOW()
                    """
                )
                premium_users = cur.fetchone()[0]

                # Менеджеры
                cur.execute(
                    """
                    SELECT COUNT(*)
                    FROM users
                    WHERE role = 'manager'
                    """
                )
                managers = cur.fetchone()[0]

        await update.message.reply_text(
            "📊 Общая статистика\n\n"
            f"👥 Всего пользователей: {total_users}\n"
            f"⭐ Premium пользователей: {premium_users}\n"
            f"🧑‍💼 Менеджеров: {managers}"
        )

    except Exception as e:
        await update.message.reply_text("❌ Ошибка при получении статистики")
        raise e
