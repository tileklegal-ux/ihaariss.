from datetime import datetime, timedelta
from telegram import Bot

from config import BOT_TOKEN
from database.models import get_all_premium_users, disable_expired_premium


async def check_premium_expiration():
    """
    Проверяет Premium-статус:
    - кто теряет Premium через 3 дня → уведомить
    - кто теряет Premium через 1 день → уведомить
    - у кого Premium уже истёк → отключить
    """

    bot = Bot(BOT_TOKEN)
    users = get_all_premium_users()
    now = datetime.utcnow()

    for user_id, username, premium_until in users:

        try:
            expiry = datetime.fromisoformat(premium_until)
        except:
            continue

        delta = expiry - now

        # Уведомление за 3 дня
        if timedelta(days=3) >= delta > timedelta(days=2):
            await bot.send_message(
                chat_id=user_id,
                text=(
                    "⚠ *Ваш Premium истекает через 3 дня!* \n"
                    "Продлите доступ — сохраните историю, анализы и все функции Artbazar AI."
                ),
                parse_mode="Markdown"
            )

        # Уведомление за 1 день
        elif timedelta(days=1) >= delta > timedelta(hours=23):
            await bot.send_message(
                chat_id=user_id,
                text=(
                    "⏳ *Ваш Premium истекает завтра!* \n"
                    "Продлите, чтобы не потерять доступ к расширенному анализу."
                ),
                parse_mode="Markdown"
            )

    # Авто-отключение
    disable_expired_premium()
