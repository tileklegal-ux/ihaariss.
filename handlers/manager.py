# handlers/manager.py - ОБНОВЛЕННАЯ ВЕРСИЯ

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters

from database.db import get_user_role

# УБРАН ИМПОРТ из role_actions
# from handlers.role_actions import give_premium_start, BTN_GIVE_PREMIUM, BTN_EXIT

# КОНСТАНТЫ КНОПОК (ДОБАВЛЕНЫ ВРУЧНУЮ)
BTN_GIVE_PREMIUM = "📋 Выдать Premium"
BTN_EXIT = "⬅️ Выйти"


def manager_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_GIVE_PREMIUM)],
            [KeyboardButton(BTN_EXIT)],
        ],
        resize_keyboard=True,
    )


async def manager_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = get_user_role(update.effective_user.id)
    if role != "manager":
        return

    await update.message.reply_text(
        "👨‍💼 Панель менеджера\n\n"
        "Доступ:\n"
        "• Выдача Premium пользователям",
        reply_markup=manager_keyboard(),
    )


async def manager_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = get_user_role(update.effective_user.id)
    if role != "manager":
        return

    text = update.message.text or ""

    if text == BTN_GIVE_PREMIUM:
        # ВРЕМЕННАЯ ЗАГЛУШКА вместо give_premium_start
        await update.message.reply_text(
            "⚠️ Функция выдачи Premium временно недоступна.\n\n"
            "Для выдачи Premium пользователям:\n"
            "1. Получите подтверждение от владельца\n"
            "2. Напишите в поддержку @Artbazar_support\n\n"
            "Функция будет доступна в ближайшем обновлении.",
            reply_markup=manager_keyboard()
        )
        return

    if text == BTN_EXIT:
        # Сбрасываем все состояния
        context.user_data.clear()
        await update.message.reply_text("Выход из панели менеджера.")
        return


def register_handlers_manager(app):
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, manager_text_router),
        group=3,  # group=3 для менеджера
    )
