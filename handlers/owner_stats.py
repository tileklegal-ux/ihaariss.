from telegram import Update
from telegram.ext import ContextTypes

from database.db import get_user_role, get_connection


async def show_owner_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = get_user_role(update.effective_user.id)

    if role != "owner":
        await update.message.reply_text("Нет доступа.")
        return

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        total_users = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM users WHERE role = 'manager'")
        managers = cur.fetchone()[0]

    text = (
        f"📊 Статистика:\n"
        f"Всего пользователей: {total_users}\n"
        f"Менеджеров: {managers}"
    )

    await update.message.reply_text(text)
