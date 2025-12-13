from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

from database.db import create_or_update_user, get_user_role
from services.menu import send_main_menu

# owner / manager / stats
from handlers.owner import register_owner_handlers, owner_panel
from handlers.manager import register_manager_handlers

# -------------------------------------------------
# КНОПКИ
# -------------------------------------------------
BTN_YES = "Да"
BTN_NO = "Нет"

BTN_OWNER_PANEL = "🧑‍💼 Панель владельца"
BTN_MANAGER_PANEL = "👨‍💼 Панель менеджера"

# -------------------------------------------------
# ТЕКСТЫ
# -------------------------------------------------
START_DISCLAIMER_TEXT = (
    "Привет! 👋\n"
    "Artbazar AI — помощник для предпринимателей.\n"
    "Мы используем вероятностные данные и не гарантируем 100% точность.\n"
    "Используйте выводы как подсказки, решения принимайте самостоятельно.\n\n"
    "Продолжим?"
)

NO_MENU_TEXT = "Хорошо, буду на связи. Обращайтесь, когда будете готовы."


# -------------------------------------------------
# КЛАВИАТУРЫ
# -------------------------------------------------
def yes_no_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton(BTN_YES), KeyboardButton(BTN_NO)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def owner_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton(BTN_OWNER_PANEL)]],
        resize_keyboard=True,
    )


def manager_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton(BTN_MANAGER_PANEL)]],
        resize_keyboard=True,
    )


# -------------------------------------------------
# INIT USER
# -------------------------------------------------
async def ensure_user(update: Update):
    u = update.effective_user
    if u:
        create_or_update_user(
            u.id,
            u.username or "",
            u.first_name or "",
        )


# -------------------------------------------------
# /start — ЕДИНАЯ ТОЧКА
# -------------------------------------------------
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ensure_user(update)
    role = get_user_role(update.effective_user.id)

    if role == "owner":
        # НЕ делаем Conversation. Просто даём кнопку входа.
        await update.message.reply_text(
            "Доступ владельца подтверждён ✅",
            reply_markup=owner_keyboard(),
        )
        return

    if role == "manager":
        await update.message.reply_text(
            "Доступ менеджера подтверждён ✅",
            reply_markup=manager_keyboard(),
        )
        return

    # user
    await update.message.reply_text(
        START_DISCLAIMER_TEXT,
        reply_markup=yes_no_keyboard(),
    )


# -------------------------------------------------
# START → YES / NO (ТОЛЬКО USER)
# -------------------------------------------------
async def on_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = get_user_role(update.effective_user.id)
    if role != "user":
        return
    await send_main_menu(update)


async def on_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = get_user_role(update.effective_user.id)
    if role != "user":
        return
    await update.message.reply_text(
        NO_MENU_TEXT,
        reply_markup=ReplyKeyboardRemove(),
    )


# -------------------------------------------------
# РЕГИСТРАЦИЯ
# -------------------------------------------------
def register_handlers_user(app):
    # /start
    app.add_handler(CommandHandler("start", cmd_start))

    # yes / no
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_YES}$"), on_yes))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NO}$"), on_no))

    # ВАЖНО:
    # НИКАКИХ заглушек на BTN_OWNER_PANEL / BTN_MANAGER_PANEL здесь.
    # Эти кнопки обрабатываются ТОЛЬКО в handlers/owner.py и handlers/manager.py.

    # owner / manager handlers
    register_owner_handlers(app)
    register_manager_handlers(app)
