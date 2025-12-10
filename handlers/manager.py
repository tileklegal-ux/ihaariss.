from telegram import Update
from telegram.ext import ContextTypes
from datetime import timedelta, datetime

from config import MANAGER_ID
from database.models import get_user_by_username, set_premium, remove_premium


# Проверка роли менеджера
def is_manager(user_id: int) -> bool:
    return user_id == MANAGER_ID


# Нормализация username
def normalize_username(name: str) -> str:
    """
    Убирает @ и пробелы.
    """
    name = name.strip()
    if name.startswith("@"):
        name = name[1:]
    return name


# Выдача Premium по username
async def give_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_manager(update.effective_user.id):
        await update.message.reply_text("У вас нет прав менеджера.")
        return

    if len(context.args) != 2:
        await update.message.reply_text("Формат: /give_premium @username <days>")
        return

    username = normalize_username(context.args[0])
    days = int(context.args[1])

    user = get_user_by_username(username)

    if not user:
        await update.message.reply_text(
            f"Пользователь @{username} не найден. Он ещё не запускал бота."
        )
        return

    target_id = user[0]  # user_id из таблицы users

    set_premium(target_id, days)

    await update.message.reply_text(
        f"Premium выдан пользователю @{username} на {days} дней."
    )


# Продление Premium
async def extend_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_manager(update.effective_user.id):
        await update.message.reply_text("У вас нет прав менеджера.")
        return

    if len(context.args) != 2:
        await update.message.reply_text("Формат: /extend_premium @username <days>")
        return

    username = normalize_username(context.args[0])
    days = int(context.args[1])

    user = get_user_by_username(username)

    if not user:
        await update.message.reply_text(
            f"Пользователь @{username} не найден."
        )
        return

    target_id = user[0]

    set_premium(target_id, days)

    await update.message.reply_text(
        f"Premium продлён пользователю @{username} на {days} дней."
    )


# Отключение Premium
async def remove_premium_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_manager(update.effective_user.id):
        await update.message.reply_text("У вас нет прав менеджера.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Формат: /remove_premium @username")
        return

    username = normalize_username(context.args[0])
    user = get_user_by_username(username)

    if not user:
        await update.message.reply_text(
            f"Пользователь @{username} не найден."
        )
        return

    target_id = user[0]

    remove_premium(target_id)

    await update.message.reply_text(
        f"Premium отключён у пользователя @{username}."
    )

