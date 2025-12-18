from telegram import Update
from telegram.ext import ContextTypes
import psycopg2
import os


DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


async def show_owner_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Всего пользователей
        cur.execute("SELECT COUNT(*) FROM users")
        total_users = cur.fetchone()[0]

        # Premium пользователи
        cur.execute(
            "SELECT COUNT(*) FROM users WHERE premium_until > EXTRACT(EPOCH FROM NOW())"
        )
        premium_users = cur.fetchone()[0]

        # Менеджеры
        cur.execute("SELECT COUNT(*) FROM users WHERE role = 'manager'")
        managers = cur.fetchone()[0]

        cur.close()
        conn.close()

        text = (
            "📊 *Общая статистика*\n\n"
            f"👥 Всего пользователей: {total_users}\n"
            f"⭐ Premium пользователей: {premium_users}\n"
            f"🧑‍💼 Менеджеров: {managers}"
        )

        await update.message.reply_text(text, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text("❌ Ошибка при получении статистики")
        raise e
