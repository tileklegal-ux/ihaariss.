from telegram import Update
from telegram.ext import ContextTypes

from database.db import (
    get_user_by_username,
    set_role_by_telegram_id,
    give_premium_days,
)

# ==================================================
# ADD MANAGER (2-step via button → username)
# ==================================================

async def add_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Шаг 1.
    Вызывается по кнопке владельца.
    Просим ввести username менеджера.
    """
    context.user_data["awaiting_manager_username"] = True

    await update.message.reply_text(
        "Укажите юзернейм пользователя (без @), которого нужно сделать менеджером:"
    )


async def handle_add_manager_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Шаг 2.
    Обрабатывает введённый username.
    """
    if not context.user_data.get("awaiting_manager_username"):
        return

    context.user_data.pop("awaiting_manager_username", None)

    username = (update.message.text or "").strip().lstrip("@")
    if not username:
        await update.message.reply_text("Юзернейм не может быть пустым.")
        return

    user = get_user_by_username(username)
    if not user:
        await update.message.reply_text("Пользователь с таким юзернеймом не найден.")
        return

    set_role_by_telegram_id(user["telegram_id"], "manager")

    await update.message.reply_text(
        f"Пользователь @{username} успешно назначен менеджером."
    )


# ==================================================
# REMOVE MANAGER (1-step, legacy behaviour)
# ==================================================

async def remove_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Удаляет роль менеджера.
    Ожидает username следующим сообщением.
    """
    context.user_data["awaiting_remove_manager"] = True

    await update.message.reply_text(
        "Укажите юзернейм менеджера (без @), которого нужно удалить:"
    )


async def handle_remove_manager_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_remove_manager"):
        return

    context.user_data.pop("awaiting_remove_manager", None)

    username = (update.message.text or "").strip().lstrip("@")
    if not username:
        await update.message.reply_text("Юзернейм не может быть пустым.")
        return

    user = get_user_by_username(username)
    if not user:
        await update.message.reply_text("Пользователь не найден.")
        return

    set_role_by_telegram_id(user["telegram_id"], "user")

    await update.message.reply_text(
        f"Роль менеджера у @{username} успешно удалена."
    )
