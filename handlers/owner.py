# handlers/owner.py

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters,
    StopPropagation,  # <--- ДОБАВЛЕН ИМПОРТ
)

from database.db import (
    get_user_by_username,
    set_role_by_telegram_id,
    get_stats,
    get_user_role,
)

from handlers.user_keyboards import main_menu_keyboard

# ==================================================
# OWNER KEYBOARDS
# ==================================================

OWNER_MENU = ReplyKeyboardMarkup(
    [
        ["➕ Добавить менеджера", "➖ Удалить менеджера"],
        ["📊 Статистика"],
        ["⬅️ Выйти в главное меню"],
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
    "Ниже — вектор движения, не план задач.\n\n"
    "🎯 Фокус Artbazar AI:\n\n"
    "1️⃣ Монетизация\n"
    "— самостоятельная покупка Premium\n"
    "— подписки и автопродление\n"
    "— локальные платежи (Kaspi и др.)\n\n"
    "2️⃣ Масштабирование\n"
    "— Artbazar AI как бренд\n"
    "— SaaS / B2B-версия\n"
    "— white-label для партнёров\n\n"
    "3️⃣ Аналитика\n"
    "— персональные AI-разборы\n"
    "— оценка рисков\n\n"
    "Это не срочно.\n"
    "Это направление."
)

# ==================================================
# OWNER ENTRY
# ==================================================

async def owner_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("ai_chat_mode", None)
    context.user_data.pop("pm_state", None)
    context.user_data.pop("ta_state", None)
    context.user_data.pop("ns_step", None)
    context.user_data.pop("growth", None)
    context.user_data.pop("owner_mode", None)

    await update.message.reply_text(
        OWNER_START_TEXT,
        reply_markup=OWNER_START_KB,
    )

# ==================================================
# OWNER MAIN MENU
# ==================================================

async def open_owner_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if get_user_role(update.effective_user.id) != "owner":
        return

    context.user_data.pop("ai_chat_mode", None)
    context.user_data.pop("pm_state", None)
    context.user_data.pop("ta_state", None)
    context.user_data.pop("ns_step", None)
    context.user_data.pop("growth", None)
    context.user_data.pop("owner_mode", None)

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

    stats = get_stats()
    total = stats.get("user", 0) + stats.get("manager", 0) + stats.get("owner", 0)

    text = (
        "📊 Статистика проекта\n\n"
        f"👥 Всего пользователей: {total}\n"
        f"👤 Пользователи: {stats.get('user', 0)}\n"
        f"🧑‍💼 Менеджеры: {stats.get('manager', 0)}\n"
        f"👑 Владельцы: {stats.get('owner', 0)}\n"
        f"⭐ Premium: {stats.get('premium', 0)}\n\n"
        "Цифры отражают текущее состояние.\n"
        "Это не оценка и не прогноз."
    )

    await update.message.reply_text(
        text,
        reply_markup=OWNER_MENU,
    )

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

    context.user_data.pop("owner_mode", None)
    await open_owner_menu(update, context)

# ==================================================
# EXIT OWNER MODE (FIXED)
# ==================================================

async def exit_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("owner_mode", None)
    context.user_data.pop("ai_chat_mode", None)
    context.user_data.pop("pm_state", None)
    context.user_data.pop("ta_state", None)
    context.user_data.pop("ns_step", None)
    context.user_data.pop("growth", None)

    await update.message.reply_text(
        "Выход из панели владельца",
        reply_markup=main_menu_keyboard(),
    )
    
    # 📌 ФИКС: Остановка Propagation, чтобы апдейт не попал в group=4 (text_router)
    raise StopPropagation  

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
        MessageHandler(filters.Regex("^⬅️ Выйти в главное меню$"), exit_owner),
        group=1,
    )

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_owner_input),
        group=2,
    )
