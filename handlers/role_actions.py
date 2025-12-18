# handlers/role_actions.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, Application

from database.db import set_user_role, get_user_by_username, ensure_user_exists

# Если у тебя owner задаётся иначе — поменяешь тут или завяжешь на config.py
OWNER_ID = 1974482384


def _parse_target(arg: str):
    """
    Возвращает либо int(user_id), либо None.
    Поддержка: "123456", "@username", "username"
    """
    arg = (arg or "").strip()
    if not arg:
        return None

    if arg.isdigit():
        return int(arg)

    row = get_user_by_username(arg)
    if row:
        return int(row[0])

    return None


async def add_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Нет доступа.")
        return

    if not context.args:
        await update.message.reply_text("Формат: /add_manager <telegram_id или @username>")
        return

    target = _parse_target(context.args[0])
    if not target:
        await update.message.reply_text("Не нашёл пользователя. Дай telegram_id или корректный @username.")
        return

    ensure_user_exists(target, None)
    set_user_role(target, "manager")
    await update.message.reply_text(f"✅ Назначил менеджера: {target}")


async def remove_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Нет доступа.")
        return

    if not context.args:
        await update.message.reply_text("Формат: /remove_manager <telegram_id или @username>")
        return

    target = _parse_target(context.args[0])
    if not target:
        await update.message.reply_text("Не нашёл пользователя. Дай telegram_id или корректный @username.")
        return

    ensure_user_exists(target, None)
    set_user_role(target, "user")
    await update.message.reply_text(f"✅ Снял менеджера: {target}")


def register_role_actions(app: Application):
    app.add_handler(CommandHandler("add_manager", add_manager))
    app.add_handler(CommandHandler("remove_manager", remove_manager))
