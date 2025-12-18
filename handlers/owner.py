# handlers/owner.py

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, Application

from handlers.owner_stats import show_owner_stats
from handlers.role_actions import add_manager, remove_manager


OWNER_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["📊 Общая статистика"],
        ["➕ Добавить менеджера", "➖ Удалить менеджера"],
        ["⬅️ Выйти"],
    ],
    resize_keyboard=True,
)


async def owner_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👑 Панель владельца",
        reply_markup=OWNER_KEYBOARD,
    )


async def owner_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📊 Общая статистика":
        await show_owner_stats(update, context)
        return

    if text == "➕ Добавить менеджера":
        await add_manager(update, context)
        return

    if text == "➖ Удалить менеджера":
        await remove_manager(update, context)
        return

    if text == "⬅️ Выйти":
        await owner_start(update, context)
        return


def register_owner_handlers(app: Application):
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, owner_text_router),
        group=1,
    )
