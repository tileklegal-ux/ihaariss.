# owner.py
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters

from database.db import get_user_role, ensure_user_exists, set_user_role
from handlers.owner_stats import show_owner_stats


OWNER_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["📊 Общая статистика"],
        ["➕ Добавить менеджера", "➖ Удалить менеджера"],
        ["⬅️ Выйти"],
    ],
    resize_keyboard=True,
)

ADD_MANAGER_TEXT = (
    "➕ Добавить менеджера\n\n"
    "Отправь Telegram ID пользователя, которого нужно сделать менеджером.\n\n"
    "Как узнать Telegram ID:\n"
    "1️⃣ Напиши боту @userinfobot\n"
    "2️⃣ Скопируй ID\n"
    "3️⃣ Пришли сюда числом"
)

REMOVE_MANAGER_TEXT = (
    "➖ Удалить менеджера\n\n"
    "Отправь Telegram ID менеджера, которого нужно убрать.\n\n"
    "Как узнать Telegram ID:\n"
    "1️⃣ Напиши боту @userinfobot\n"
    "2️⃣ Скопируй ID\n"
    "3️⃣ Пришли сюда числом"
)


def _clear_owner_flow(context: ContextTypes.DEFAULT_TYPE):
    # сбрасываем только то, что относится к панели владельца
    context.user_data.pop("await_manager_id", None)


async def owner_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _clear_owner_flow(context)
    await update.message.reply_text(
        "👑 Панель владельца",
        reply_markup=OWNER_KEYBOARD,
    )


async def owner_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if get_user_role(user_id) != "owner":
        return

    text = (update.message.text or "").strip()

    # ─────────────────────────────
    # КНОПКИ ПАНЕЛИ (всегда сбрасываем ожидания)
    # ─────────────────────────────
    if text == "📊 Общая статистика":
        _clear_owner_flow(context)
        await show_owner_stats(update, context)
        return

    if text == "➕ Добавить менеджера":
        _clear_owner_flow(context)
        context.user_data["await_manager_id"] = "add"
        await update.message.reply_text(ADD_MANAGER_TEXT)
        return

    if text == "➖ Удалить менеджера":
        _clear_owner_flow(context)
        context.user_data["await_manager_id"] = "remove"
        await update.message.reply_text(REMOVE_MANAGER_TEXT)
        return

    if text == "⬅️ Выйти":
        _clear_owner_flow(context)
        await update.message.reply_text("Выход из панели владельца")
        return

    # ─────────────────────────────
    # ОЖИДАНИЕ TELEGRAM ID (add/remove)
    # ─────────────────────────────
    action = context.user_data.get("await_manager_id")
    if action in ("add", "remove"):
        if not text.isdigit():
            await update.message.reply_text("❌ Пришли Telegram ID числом.")
            return

        target_id = int(text)

        # гарантируем запись пользователя
        ensure_user_exists(target_id)

        if action == "add":
            set_user_role(target_id, "manager")
            _clear_owner_flow(context)
            await update.message.reply_text(
                f"✅ Менеджер назначен.\nTelegram ID: {target_id}"
            )
            return

        if action == "remove":
            set_user_role(target_id, "user")
            _clear_owner_flow(context)
            await update.message.reply_text(
                f"✅ Менеджер удалён.\nTelegram ID: {target_id}"
            )
            return


def register_owner_handlers(app):
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, owner_text_router),
        group=1,
    )
