# handlers/manager.py

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters
from datetime import datetime, timedelta, timezone

from database.db import (
    get_user_role,
    set_premium_until,
    ensure_user_exists,
)

# =============================
# FSM KEY (ТОЛЬКО ДЛЯ МЕНЕДЖЕРА)
# =============================

MANAGER_AWAIT_PREMIUM = "manager_await_premium"

# =============================
# KEYBOARD
# =============================

MANAGER_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["⭐ Активировать Premium"],
        ["⬅️ Выйти"],
    ],
    resize_keyboard=True,
)

# =============================
# START
# =============================

async def manager_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user_exists(update.effective_user.id)
    context.user_data.pop(MANAGER_AWAIT_PREMIUM, None)

    await update.message.reply_text(
        "🧑‍💼 Панель менеджера",
        reply_markup=MANAGER_KEYBOARD,
    )

# =============================
# TEXT ROUTER
# =============================

async def manager_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return

    user_id = user.id

    # 🔑 КРИТИЧЕСКИ ВАЖНО
    ensure_user_exists(user_id)

    role = get_user_role(user_id)
    if role != "manager":
        return

    text = (update.message.text or "").strip()
    if not text:
        return

    # -------------------------
    # EXIT
    # -------------------------
    if text == "⬅️ Выйти":
        context.user_data.pop(MANAGER_AWAIT_PREMIUM, None)
        await update.message.reply_text("Выход из панели менеджера")
        return

    # -------------------------
    # START PREMIUM FLOW
    # -------------------------
    if text == "⭐ Активировать Premium":
        context.user_data[MANAGER_AWAIT_PREMIUM] = True

        await update.message.reply_text(
            "⭐ Активация Premium\n\n"
            "Отправь сообщение в формате:\n"
            "TELEGRAM_ID ДНИ\n\n"
            "Пример:\n"
            "123456789 30"
        )
        return

    # -------------------------
    # HANDLE PREMIUM INPUT
    # -------------------------
    if context.user_data.get(MANAGER_AWAIT_PREMIUM):
        parts = text.split()
        if len(parts) != 2:
            await update.message.reply_text(
                "❌ Формат неверный.\nИспользуй: TELEGRAM_ID ДНИ"
            )
            return

        tg_id, days = parts

        if not tg_id.isdigit() or not days.isdigit():
            await update.message.reply_text(
                "❌ Telegram ID и дни должны быть числами."
            )
            return

        tg_id = int(tg_id)
        days = int(days)

        if days <= 0:
            await update.message.reply_text(
                "❌ Количество дней должно быть больше 0."
            )
            return

        ensure_user_exists(tg_id)

        premium_until = datetime.now(timezone.utc) + timedelta(days=days)
        set_premium_until(tg_id, premium_until)

        context.user_data.pop(MANAGER_AWAIT_PREMIUM, None)

        await update.message.reply_text(
            "✅ Premium активирован\n\n"
            f"👤 Пользователь: {tg_id}\n"
            f"⏳ Срок: {days} дней"
        )

        await manager_start(update, context)

        try:
            await context.bot.send_message(
                chat_id=tg_id,
                text=(
                    "🎉 Premium активирован!\n\n"
                    f"⏳ Срок действия: {days} дней\n\n"
                    "Теперь вам доступны расширенные функции 🚀"
                ),
            )
        except Exception:
            pass

        return

# =============================
# REGISTER
# =============================

def register_manager_handlers(app):
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, manager_text_router),
        group=1,
    )
