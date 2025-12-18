from telegram import Update
from telegram.ext import ContextTypes

from database.db import get_user_role
from services.audit_log import log_event


async def show_owner_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # защита: только owner
    role = get_user_role(user.id)
    if role != "owner":
        await update.message.reply_text("❌ Доступ только для владельца.")
        return

    # тут пока заглушка, ты дальше сам расширишь статистику
    text = (
        "📊 Статистика владельца\n\n"
        "— Пользователи: в разработке\n"
        "— Премиум: в разработке\n"
        "— Запросы: в разработке"
    )

    await update.message.reply_text(text)

    log_event(
        user_id=user.id,
        action="owner_stats_opened",
        details="Owner opened statistics panel"
    )
