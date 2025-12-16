from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from database.db import (
    get_user_role,
    get_user_by_username,
    set_role_by_telegram_id,
    give_premium_days,
)
from services.audit_log import log_event

BTN_ADD_MANAGER = "➕ Добавить менеджера"
BTN_REMOVE_MANAGER = "➖ Удалить менеджера"
BTN_GIVE_PREMIUM = "⭐ Выдать Premium"


# -------------------------------------------------
# ADD MANAGER
# -------------------------------------------------
async def add_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = get_user_role(update.effective_user.id)
    if role != "owner":
        await update.message.reply_text("❌ Нет доступа.")
        return

    if not context.args:
        await update.message.reply_text("Укажи username менеджера.")
        return

    username = context.args[0]
    user = get_user_by_username(username)

    if not user:
        await update.message.reply_text("Пользователь не найден.")
        return

    set_role_by_telegram_id(user["telegram_id"], "manager")
    log_event(update.effective_user.id, f"add_manager:{user['telegram_id']}")

    await update.message.reply_text(
        f"✅ Пользователь @{user['username']} назначен менеджером."
    )


# -------------------------------------------------
# REMOVE MANAGER
# -------------------------------------------------
async def remove_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = get_user_role(update.effective_user.id)
    if role != "owner":
        await update.message.reply_text("❌ Нет доступа.")
        return

    if not context.args:
        await update.message.reply_text("Укажи username менеджера.")
        return

    username = context.args[0]
    user = get_user_by_username(username)

    if not user:
        await update.message.reply_text("Пользователь не найден.")
        return

    set_role_by_telegram_id(user["telegram_id"], "user")
    log_event(update.effective_user.id, f"remove_manager:{user['telegram_id']}")

    await update.message.reply_text(
        f"✅ Пользователь @{user['username']} больше не менеджер."
    )


# -------------------------------------------------
# GIVE PREMIUM (MANAGER)
# -------------------------------------------------
async def give_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = get_user_role(update.effective_user.id)
    if role not in ("manager", "owner"):
        await update.message.reply_text("❌ Нет доступа.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Формат: username дни")
        return

    username = context.args[0]
    days = context.args[1]

    user = get_user_by_username(username)
    if not user:
        await update.message.reply_text("Пользователь не найден.")
        return

    try:
        days = int(days)
    except ValueError:
        await update.message.reply_text("Дни должны быть числом.")
        return

    give_premium_days(user["telegram_id"], days)
    log_event(update.effective_user.id, f"premium_granted:{user['telegram_id']}:{days}")

    await update.message.reply_text(
        f"⭐ Premium для @{user['username']} выдан на {days} дней."
    )


# -------------------------------------------------
# REGISTRATION
# -------------------------------------------------
def register_role_actions(app):
    app.add_handler(
        MessageHandler(filters.Regex(f"^{BTN_ADD_MANAGER}$"), add_manager)
    )
    app.add_handler(
        MessageHandler(filters.Regex(f"^{BTN_REMOVE_MANAGER}$"), remove_manager)
    )
    app.add_handler(
        MessageHandler(filters.Regex(f"^{BTN_GIVE_PREMIUM}$"), give_premium)
    )
