from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters,
)

from database.db import (
    get_user_by_username,
    set_role_by_telegram_id,
    get_stats,
    get_user_role,
)

# ==================================================
# OWNER KEYBOARD
# ==================================================

OWNER_MENU = ReplyKeyboardMarkup(
    [
        ["➕ Добавить менеджера", "➖ Удалить менеджера"],
        ["📊 Статистика"],
    ],
    resize_keyboard=True,
)

OWNER_START_KB = ReplyKeyboardMarkup(
    [["👑 Панель владельца"]],
    resize_keyboard=True,
)

# ==================================================
# TEXTS
# ==================================================

OWNER_START_TEXT = (
    "Привет, босс 👋\n\n"
    "Смотрим на Artbazar AI спокойно и стратегически.\n\n"
    "Проект сейчас в рабочем MVP-состоянии.\n"
    "Ниже — фокус развития, чтобы держать направление.\n\n"
    "🎯 Фокус Artbazar AI:\n\n"
    "1️⃣ Монетизация\n"
    "— самостоятельная покупка Premium\n"
    "— подписки и автопродление\n"
    "— локальные платежи (Kaspi и др.)\n\n"
    "2️⃣ Масштабирование продукта\n"
    "— Artbazar AI как бренд\n"
    "— SaaS / B2B-версия\n"
    "— white-label для партнёров\n\n"
    "3️⃣ Умная аналитика\n"
    "— персональные AI-рекомендации\n"
    "— прогноз спроса и рисков\n\n"
    "Это не срочно.\n"
    "Это вектор движения."
)

# ==================================================
# OWNER ENTRY (вызывается из main.py)
# ==================================================

async def owner_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        OWNER_START_TEXT,
        reply_markup=OWNER_START_KB,
    )

# ==================================================
# OWNER MAIN PANEL
# ==================================================

async def open_owner_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if get_user_role(update.effective_user.id) != "owner":
        return

    context.user_data.clear()

    await update.message.reply_text(
        "👑 Панель владельца",
        reply_markup=OWNER_MENU,
    )

# ==================================================
# FSM STARTERS
# ==================================================

async def start_add_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if get_user_role(update.effective_user.id) != "owner":
        return

    context.user_data["owner_mode"] = "add_manager"
    await update.message.reply_text(
        "Отправь username или telegram_id пользователя"
    )


async def start_remove_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if get_user_role(update.effective_user.id) != "owner":
        return

    context.user_data["owner_mode"] = "remove_manager"
    await update.message.reply_text(
        "Отправь username или telegram_id пользователя"
    )

# ==================================================
# STATS
# ==================================================

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if get_user_role(update.effective_user.id) != "owner":
        return

    context.user_data.clear()

    stats = get_stats()
    text = (
        "📊 Статистика бота:\n\n"
        f"👤 Пользователи: {stats['user']}\n"
        f"🧑‍💼 Менеджеры: {stats['manager']}\n"
        f"👑 Владельцы: {stats['owner']}\n"
        f"⭐ Premium: {stats['premium']}"
    )
    await update.message.reply_text(text)

# ==================================================
# FSM HANDLER
# ==================================================

async def handle_owner_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if get_user_role(update.effective_user.id) != "owner":
        return

    mode = context.user_data.get("owner_mode")
    if not mode:
        return

    raw = update.message.text.strip().lstrip("@")

    telegram_id = None

    if raw.isdigit():
        telegram_id = int(raw)
    else:
        user = get_user_by_username(raw)
        if not user:
            await update.message.reply_text("❌ Пользователь не найден")
            return
        telegram_id = user["telegram_id"]

    if mode == "add_manager":
        ok = set_role_by_telegram_id(telegram_id, "manager")
        msg = "✅ Менеджер успешно добавлен" if ok else "❌ Не удалось назначить менеджера"
        await update.message.reply_text(msg)

    elif mode == "remove_manager":
        ok = set_role_by_telegram_id(telegram_id, "user")
        msg = "✅ Менеджер удалён" if ok else "❌ Не удалось удалить менеджера"
        await update.message.reply_text(msg)

    context.user_data.clear()
    await open_owner_menu(update, context)

# ==================================================
# REGISTER
# ==================================================

def register_owner_handlers(app):
    app.add_handler(
        MessageHandler(filters.Regex("^👑 Панель владельца$"), open_owner_menu),
        group=1,
    )

    app.add_handler(
        MessageHandler(filters.Regex("^➕ Добавить менеджера$"), start_add_manager),
        group=1,
    )

    app.add_handler(
        MessageHandler(filters.Regex("^➖ Удалить менеджера$"), start_remove_manager),
        group=1,
    )

    app.add_handler(
        MessageHandler(filters.Regex("^📊 Статистика$"), show_stats),
        group=1,
    )

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_owner_input),
        group=2,
    )
