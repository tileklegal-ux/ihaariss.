import time
from datetime import datetime
from telegram import Bot

from database.db import get_db_connection
from services.audit_log import log_event


# -------------------------------------------------
# HELPERS
# -------------------------------------------------

def _now_ts() -> int:
    return int(time.time())


def _fmt_ts(ts: int) -> str:
    return datetime.fromtimestamp(ts).strftime("%d.%m.%Y %H:%M")


# -------------------------------------------------
# NOTIFICATIONS
# -------------------------------------------------

async def notify_premium_activated(bot: Bot, user_id: int, premium_until: int):
    text = (
        "✅ Premium активирован!\n\n"
        f"Срок действия до: {_fmt_ts(premium_until)}\n"
        "Спасибо за доверие к Artbazar AI."
    )
    try:
        await bot.send_message(chat_id=user_id, text=text)
        log_event(user_id, "premium_activated_notification_sent")
    except Exception:
        log_event(user_id, "premium_activated_notification_failed")


async def notify_premium_revoked(bot: Bot, user_id: int):
    text = (
        "ℹ️ Premium отключён.\n\n"
        "Если это ошибка — обратись к менеджеру."
    )
    try:
        await bot.send_message(chat_id=user_id, text=text)
        log_event(user_id, "premium_revoked_notification_sent")
    except Exception:
        log_event(user_id, "premium_revoked_notification_failed")


async def notify_premium_expiring(bot: Bot, user_id: int, days_left: int, premium_until: int):
    text = (
        "⏳ Premium скоро закончится.\n\n"
        f"Осталось дней: {days_left}\n"
        f"Дата окончания: {_fmt_ts(premium_until)}\n\n"
        "Чтобы продлить — напиши менеджеру."
    )
    try:
        await bot.send_message(chat_id=user_id, text=text)
        log_event(user_id, f"premium_expiring_{days_left}_days_notification_sent")
    except Exception:
        log_event(user_id, f"premium_expiring_{days_left}_days_notification_failed")


# -------------------------------------------------
# CHECKER (cron / manual call)
# -------------------------------------------------

async def check_premium_expiry(bot: Bot):
    """
    Проверка:
    - за 7 / 3 / 1 день до окончания
    - без дублей
    """
    conn = get_db_connection()
    cur = conn.cursor()

    now = _now_ts()
    notify_days = [7, 3, 1]

    cur.execute(
        "SELECT id, premium_until FROM users WHERE premium_until > ?",
        (now,),
    )
    users = cur.fetchall()

    for user in users:
        user_id = user["id"]
        premium_until = user["premium_until"]

        days_left = (premium_until - now) // 86400

        if days_left in notify_days:
            await notify_premium_expiring(
                bot=bot,
                user_id=user_id,
                days_left=days_left,
                premium_until=premium_until,
            )

    conn.close()
    log_event(0, "premium_expiry_check_completed")
