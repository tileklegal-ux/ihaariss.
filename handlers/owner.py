from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.role_actions import add_manager, remove_manager

OWNER_ID = 1974482384


async def owner_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    keyboard = ReplyKeyboardMarkup(
        [
            ["➕ Добавить менеджера", "➖ Удалить менеджера"],
            ["⬅️ Выйти"],
        ],
        resize_keyboard=True,
    )

    await update.message.reply_text("Панель владельца", reply_markup=keyboard)


def register_handlers_owner(app):
    app.add_handler(
        app.command_handler("add_manager", add_manager),
        group=1,
    )
    app.add_handler(
        app.command_handler("remove_manager", remove_manager),
        group=1,
    )
