# manager.py
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters

from datetime import datetime, timedelta, timezone

from database.db import get_user_role, set_premium_until, ensure_user_exists


MANAGER_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["⭐ Активировать Premium"],
        ["⬅️ Выйти"],
    ],
    resize_keyboard=True,
)


async def manager_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧑‍💼 Панель менеджера",
        reply_markup=MANAGER_KEYBOARD,
    )


async def manager_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if get_user_role(user_id) != "manager":
        return

    text = (update.message.text or "").strip()

    if text == "⭐ Активировать Premium":
        context.user_data["await_premium"] = True
        await update.message.reply_text(
            "⭐ Активация Premium\n\n"
            "Отправь сообщение в формате:\n"
            "TELEGRAM_ID ДНИ\n\n"
            "Примеры:\n"
            "6444576072 30\n"
            "6444576072 180\n"
            "6444576072 365\n\n"
            "Как узнать Telegram ID:\n"
            "1️⃣ Напиши боту @userinfobot\n"
            "2️⃣ Скопируй ID\n"
            "3️⃣ Пришли сюда"
        )
        return

    if text == "⬅️ Выйти":
        context.user_data.pop("await_premium", None)
        await update.message.reply_text("Выход из панели менеджера")
        return

    if context.user_data.get("await_premium"):
        parts = text.split()

        if len(parts) != 2:
            await update.message.reply_text(
                "❌ Неверный формат.\nИспользуй: TELEGRAM_ID ДНИ"
            )
            return

        user_id_part, days_part = parts

        if not user_id_part.isdigit() or not days_part.isdigit():
            await update.message.reply_text(
                "❌ Telegram ID и срок должны быть числами."
            )
            return

        target_id = int(user_id_part)
        days = int(days_part)

        if days <= 0:
            await update.message.reply_text("❌ Срок должен быть больше 0.")
            return

        ensure_user_exists(target_id)

        premium_until = int(
            (datetime.now(timezone.utc) + timedelta(days=days)).timestamp()
        )

        set_premium_until(target_id, premium_until)

        context.user_data.pop("await_premium", None)

        await update.message.reply_text(
            f"✅ Premium активирован\n"
            f"Telegram ID: {target_id}\n"
            f"Срок: {days} дней"
        )
        return


def register_manager_handlers(app):
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, manager_text_router),
        group=1,
    )
