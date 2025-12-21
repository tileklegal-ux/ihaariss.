# handlers/manager.py

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from datetime import datetime, timedelta, timezone

from database.db import (
    get_user_role,
    set_premium_until,
    ensure_user_exists,
)

# =============================
# STATES
# =============================

MANAGER_MENU = 1
MANAGER_AWAIT_PREMIUM = 2

# =============================
# KEYBOARDS
# =============================

MANAGER_MENU_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["⭐ Активировать Premium"],
        ["⬅️ Выйти"],
    ],
    resize_keyboard=True,
)

BACK_KEYBOARD = ReplyKeyboardMarkup(
    [["⬅️ Выйти"]],
    resize_keyboard=True,
)

# =============================
# ENTRY
# =============================

async def manager_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return ConversationHandler.END

    ensure_user_exists(user.id)

    role = get_user_role(user.id)
    if role != "manager":
        return ConversationHandler.END

    context.user_data.clear()

    await update.message.reply_text(
        "🧑‍💼 Панель менеджера",
        reply_markup=MANAGER_MENU_KEYBOARD,
    )
    return MANAGER_MENU

# =============================
# MENU
# =============================

async def manager_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == "⬅️ Выйти":
        await update.message.reply_text("Выход из панели менеджера")
        return ConversationHandler.END

    if text == "⭐ Активировать Premium":
        await update.message.reply_text(
            "⭐ Активация Premium\n\n"
            "Отправь сообщение в формате:\n"
            "TELEGRAM_ID ДНИ\n\n"
            "Пример:\n"
            "123456789 30",
            reply_markup=BACK_KEYBOARD,
        )
        return MANAGER_AWAIT_PREMIUM

    return MANAGER_MENU

# =============================
# PREMIUM INPUT
# =============================

async def manager_activate_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == "⬅️ Выйти":
        await update.message.reply_text(
            "🧑‍💼 Панель менеджера",
            reply_markup=MANAGER_MENU_KEYBOARD,
        )
        return MANAGER_MENU

    parts = text.split()
    if len(parts) != 2:
        await update.message.reply_text(
            "❌ Формат неверный.\nИспользуй: TELEGRAM_ID ДНИ"
        )
        return MANAGER_AWAIT_PREMIUM

    tg_id, days = parts

    if not tg_id.isdigit() or not days.isdigit():
        await update.message.reply_text(
            "❌ Telegram ID и дни должны быть числами."
        )
        return MANAGER_AWAIT_PREMIUM

    tg_id = int(tg_id)
    days = int(days)

    if days <= 0:
        await update.message.reply_text(
            "❌ Количество дней должно быть больше 0."
        )
        return MANAGER_AWAIT_PREMIUM

    ensure_user_exists(tg_id)

    premium_until = datetime.now(timezone.utc) + timedelta(days=days)
    set_premium_until(tg_id, premium_until)

    await update.message.reply_text(
        "✅ Premium активирован\n\n"
        f"👤 Пользователь: {tg_id}\n"
        f"⏳ Срок: {days} дней",
        reply_markup=MANAGER_MENU_KEYBOARD,
    )

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

    return MANAGER_MENU

# =============================
# REGISTER
# =============================

def register_manager_handlers(app):
    manager_conv = ConversationHandler(
        entry_points=[CommandHandler("start", manager_entry)],
        states={
            MANAGER_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, manager_menu),
            ],
            MANAGER_AWAIT_PREMIUM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, manager_activate_premium),
            ],
        },
        fallbacks=[],
        allow_reentry=True,
    )

    app.add_handler(manager_conv, group=1)
