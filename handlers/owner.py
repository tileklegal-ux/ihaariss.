
from telegram import Update
from telegram.ext import ContextTypes

from config import OWNER_ID
from database.models import get_stats, get_user_by_username, set_role


def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


def normalize_username(name: str) -> str:
    name = name.strip()
    if name.startswith("@"):
        name = name[1:]
    return name


async def owner_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Главное меню владельца.
    """
    user_id = update.effective_user.id

    if not is_owner(user_id):
        await update.message.reply_text("У вас нет прав владельца.")
        return

    text = (
        "👑 Панель владельца Artbazar AI\n\n"
        "/owner_stats — статистика пользователей\n"
        "/add_manager @username — назначить менеджера\n"
        "/remove_manager @username — убрать менеджера\n"
    )
    await update.message.reply_text(text)


async def owner_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Статистика по базе.
    """
    user_id = update.effective_user.id

    if not is_owner(user_id):
        await update.message.reply_text("У вас нет прав владельца.")
        return

    stats = get_stats()

    text = (
        "📊 Статистика Artbazar AI\n\n"
        f"Всего пользователей: {stats['total_users']}\n"
        f"Premium пользователей: {stats['premium_users']}\n"
        f"Менеджеров: {stats['managers']}\n"
    )

    await update.message.reply_text(text)


async def add_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Назначение менеджера по username.
    Формат: /add_manager @username
    """
    user_id = update.effective_user.id

    if not is_owner(user_id):
        await update.message.reply_text("У вас нет прав владельца.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Формат: /add_manager @username")
        return

    username = normalize_username(context.args[0])
    user = get_user_by_username(username)

    if not user:
        await update.message.reply_text(f"Пользователь @{username} не найден в базе.")
        return

    target_id = user[0]
    set_role(target_id, "manager")

    await update.message.reply_text(f"Пользователь @{username} назначен менеджером.")


async def remove_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Удаление менеджера (возврат к роли user).
    Формат: /remove_manager @username
    """
    user_id = update.effective_user.id

    if not is_owner(user_id):
        await update.message.reply_text("У вас нет прав владельца.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Формат: /remove_manager @username")
        return

    username = normalize_username(context.args[0])
    user = get_user_by_username(username)

    if not user:
        await update.message.reply_text(f"Пользователь @{username} не найден.")
        return

    target_id = user[0]
    set_role(target_id, "user")

    await update.message.reply_text(f"Пользователь @{username} больше не менеджер.")
