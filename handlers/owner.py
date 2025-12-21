# handlers/owner.py
from __future__ import annotations

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters

from database.db import ensure_user_exists, get_user_role
from handlers.owner_stats import show_owner_stats
from handlers.role_actions import add_manager, remove_manager

# =============================
# FSM KEYS (только для owner)
# =============================
OWNER_AWAIT_ADD_MANAGER = "owner_await_add_manager"
OWNER_AWAIT_REMOVE_MANAGER = "owner_await_remove_manager"

# =============================
# KEYBOARD
# =============================
OWNER_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["📊 Общая статистика"],
        ["➕ Добавить менеджера", "➖ Удалить менеджера"],
        ["⬅️ Выйти"],
    ],
    resize_keyboard=True,
)

# =============================
# START (вызывается из start_router.py)
# =============================
async def owner_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or not update.message:
        return

    ensure_user_exists(user.id, user.username or "")
    context.user_data.clear()

    await update.message.reply_text(
        "👑 Панель владельца",
        reply_markup=OWNER_KEYBOARD,
    )


# =============================
# TEXT ROUTER (ТОЛЬКО owner)
# =============================
async def owner_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message
    if not user or not message or not message.text:
        return

    ensure_user_exists(user.id, user.username or "")

    # Жёсткая проверка роли
    if get_user_role(user.id) != "owner":
        return

    text = message.text.strip()

    # Выход
    if text == "⬅️ Выйти":
        context.user_data.clear()
        await owner_start(update, context)
        return

    # Статистика
    if text == "📊 Общая статистика":
        await show_owner_stats(update, context)
        return

    # Начать добавление менеджера
    if text == "➕ Добавить менеджера":
        context.user_data.clear()
        context.user_data[OWNER_AWAIT_ADD_MANAGER] = True
        await message.reply_text("Отправь Telegram ID менеджера числом.")
        return

    # Начать удаление менеджера
    if text == "➖ Удалить менеджера":
        context.user_data.clear()
        context.user_data[OWNER_AWAIT_REMOVE_MANAGER] = True
        await message.reply_text("Отправь Telegram ID менеджера для удаления.")
        return

    # Обработка ввода ID (после кнопок выше)
    if context.user_data.get(OWNER_AWAIT_ADD_MANAGER) or context.user_data.get(OWNER_AWAIT_REMOVE_MANAGER):
        raw = text
        if not raw.isdigit():
            await message.reply_text("Пришли Telegram ID числом.")
            return

        target_id = int(raw)

        if context.user_data.get(OWNER_AWAIT_ADD_MANAGER):
            await add_manager(update, context, target_id)
        else:
            await remove_manager(update, context, target_id)

        context.user_data.clear()
        return


# =============================
# REGISTER
# ВАЖНО: фильтр узкий, чтобы owner не перехватывал manager/user
# =============================
def register_owner_handlers(app):
    app.add_handler(
        MessageHandler(
            filters.Regex(r"^(📊 Общая статистика|➕ Добавить менеджера|➖ Удалить менеджера|⬅️ Выйти|\d+)$"),
            owner_text_router,
        ),
        group=1,
    )
