# -*- coding: utf-8 -*-
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters,
)

from database.db import get_user_role, get_user_by_username, set_premium_by_telegram_id

# ==================================================
# BUTTONS
# ==================================================

BTN_ACTIVATE_PREMIUM = "🟢 Активировать Premium"

# ==================================================
# FSM
# ==================================================

FSM_WAIT_PREMIUM_INPUT = "wait_premium_input"

# ==================================================
# KEYBOARD
# ==================================================

def manager_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton(BTN_ACTIVATE_PREMIUM)]],
        resize_keyboard=True,
    )

def premium_profile_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("📄 Скачать PDF"), KeyboardButton("📊 Скачать Excel")],
            [KeyboardButton("⬅️ Назад")],
        ],
        resize_keyboard=True,
    )

# ==================================================
# ACTIONS
# ==================================================

async def on_activate_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if get_user_role(update.effective_user.id) != "manager":
        return

    context.user_data[FSM_WAIT_PREMIUM_INPUT] = True

    await update.message.reply_text(
        "🟢 *Активация Premium*\n\n"
        "Отправь одной строкой:\n"
        "`@username дни`\n\n"
        "Пример:\n"
        "`@test_user 7`",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )


async def on_premium_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if get_user_role(update.effective_user.id) != "manager":
        return

    if not context.user_data.get(FSM_WAIT_PREMIUM_INPUT):
        return

    text = (update.message.text or "").strip()
    parts = text.split()

    if len(parts) != 2 or not parts[0].startswith("@") or not parts[1].isdigit():
        context.user_data.pop(FSM_WAIT_PREMIUM_INPUT, None)

        await update.message.reply_text(
            "❌ Неверный формат.\n\n"
            "Используй:\n"
            "`@username дни`\n\n"
            "Пример:\n"
            "`@test_user 7`",
            parse_mode="Markdown",
            reply_markup=manager_keyboard(),
        )
        return

    username = parts[0].replace("@", "").strip()
    days = int(parts[1])

    user_data = get_user_by_username(username)

    if not user_data:
        context.user_data.pop(FSM_WAIT_PREMIUM_INPUT, None)

        await update.message.reply_text(
            "❌ Пользователь не найден в базе.\n\n"
            "Убедись, что пользователь:\n"
            "• уже заходил в бот\n"
            "• имеет @username\n\n"
            "Попроси его написать /start и попробуй снова.",
            reply_markup=manager_keyboard(),
        )
        return

    telegram_id = user_data["telegram_id"]
    set_premium_by_telegram_id(telegram_id, days)

    context.user_data.pop(FSM_WAIT_PREMIUM_INPUT, None)

    try:
        await context.bot.send_message(
            chat_id=telegram_id,
            text=(
                "🎉 *Premium активирован!*\n\n"
                f"⏳ Срок: *{days} дней*\n\n"
                "Теперь доступны:\n"
                "• история анализов\n"
                "• экспорт в PDF и Excel\n\n"
                "Я сразу открыл твой личный кабинет 👇"
            ),
            parse_mode="Markdown",
        )

        await context.bot.send_message(
            chat_id=telegram_id,
            text=(
                "👤 *Личный кабинет*\n\n"
                "Статус: ⭐ *Premium активен*\n\n"
                "Здесь собраны твои результаты.\n"
                "Ты можешь скачать отчёты в PDF или Excel."
            ),
            parse_mode="Markdown",
            reply_markup=premium_profile_keyboard(),
        )
    except Exception:
        pass

    await update.message.reply_text(
        f"✅ Premium активирован\n\n"
        f"👤 @{username}\n"
        f"⏳ Дней: {days}",
        reply_markup=manager_keyboard(),
    )

# ==================================================
# REGISTER
# ==================================================

def register_manager_handlers(app):
    app.add_handler(
        MessageHandler(
            filters.Regex(f"^{BTN_ACTIVATE_PREMIUM}$"),
            on_activate_premium,
        ),
        group=1,
    )

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, on_premium_input),
        group=3,
    )
