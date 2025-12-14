from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from handlers.user import main_menu_keyboard
from handlers.user import clear_fsm

async def on_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    await update.message.reply_text(
        "👤 Личный кабинет\n\nИстория появится позже.",
        reply_markup=main_menu_keyboard(),
    )
