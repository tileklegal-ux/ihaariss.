from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from handlers.owner_stats import show_owner_stats
from handlers.role_actions import add_manager, remove_manager
from database.db import get_user_role


async def owner_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if get_user_role(user.id) != "owner":
        await update.message.reply_text("❌ Доступ только для владельца.")
        return

    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data="owner_stats")],
        [InlineKeyboardButton("➕ Добавить менеджера", callback_data="add_manager")],
        [InlineKeyboardButton("➖ Удалить менеджера", callback_data="remove_manager")],
    ]

    await update.message.reply_text(
        "👑 Панель владельца",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def owner_callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "owner_stats":
        await show_owner_stats(update, context)

    elif query.data == "add_manager":
        await add_manager(update, context)

    elif query.data == "remove_manager":
        await remove_manager(update, context)


def register_handlers_owner(application):
    application.add_handler(CommandHandler("owner", owner_start))
    application.add_handler(CallbackQueryHandler(owner_callback_router, pattern="^owner_|^add_manager|^remove_manager"))
