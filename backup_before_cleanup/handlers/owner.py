from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ContextTypes, MessageHandler, ConversationHandler, filters

from database.db import get_user_role, get_user_by_username, set_role
from services.audit_log import log_event

BTN_OWNER_PANEL = "🧑‍💼 Панель владельца"

BTN_ADD_MANAGER = "➕ Добавить менеджера"
BTN_DEL_MANAGER = "➖ Удалить менеджера"
BTN_STATS = "📊 Статистика"
BTN_BACK = "⬅️ Назад"

ASK_ADD_USERNAME = 101
ASK_DEL_USERNAME = 102

OWNER_MENU = ReplyKeyboardMarkup(
    [
        [KeyboardButton(BTN_ADD_MANAGER)],
        [KeyboardButton(BTN_DEL_MANAGER)],
        [KeyboardButton(BTN_STATS)],
        [KeyboardButton(BTN_BACK)],
    ],
    resize_keyboard=True,
)


def _is_owner(update: Update) -> bool:
    u = update.effective_user
    if not u:
        return False
    return get_user_role(u.id) == "owner"


async def owner_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_owner(update):
        return

    log_event(update.effective_user.id, "owner_open_panel")

    await update.message.reply_text(
        "🧑‍💼 Панель владельца",
        reply_markup=OWNER_MENU,
    )


async def owner_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_owner(update):
        return ConversationHandler.END

    await update.message.reply_text(
        "🧑‍💼 Панель владельца",
        reply_markup=OWNER_MENU,
    )
    return ConversationHandler.END


# -------------------------------
# ADD MANAGER FLOW
# -------------------------------
async def add_manager_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_owner(update):
        return ConversationHandler.END

    await update.message.reply_text(
        "Отправь @username для назначения менеджером",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ASK_ADD_USERNAME


async def add_manager_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_owner(update):
        return ConversationHandler.END

    username = (update.message.text or "").strip().replace("@", "").strip()
    user = get_user_by_username(username)

    if not user:
        await update.message.reply_text("❌ Пользователь не найден. Отправь корректный @username.")
        return ASK_ADD_USERNAME

    set_role(user["id"], "manager")
    log_event(update.effective_user.id, f"owner_set_manager @{username}")

    await update.message.reply_text(
        f"✅ @{username} назначен менеджером",
        reply_markup=OWNER_MENU,
    )
    return ConversationHandler.END


# -------------------------------
# DELETE MANAGER FLOW
# -------------------------------
async def del_manager_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_owner(update):
        return ConversationHandler.END

    await update.message.reply_text(
        "Отправь @username для удаления из менеджеров",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ASK_DEL_USERNAME


async def del_manager_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_owner(update):
        return ConversationHandler.END

    username = (update.message.text or "").strip().replace("@", "").strip()
    user = get_user_by_username(username)

    if not user:
        await update.message.reply_text("❌ Пользователь не найден. Отправь корректный @username.")
        return ASK_DEL_USERNAME

    set_role(user["id"], "user")
    log_event(update.effective_user.id, f"owner_del_manager @{username}")

    await update.message.reply_text(
        f"✅ @{username} снят с роли менеджера",
        reply_markup=OWNER_MENU,
    )
    return ConversationHandler.END


# -------------------------------
# STATS (зависит от твоей БД; если есть отдельные методы — подключишь позже)
# -------------------------------
async def owner_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_owner(update):
        return

    # Безопасный placeholder: чтобы не падать из-за отсутствующих функций.
    # Если у тебя есть функции stats в db.py — подставишь их сюда.
    await update.message.reply_text(
        "📊 Статистика\n\n"
        "— всего пользователей: (подключим)\n"
        "— premium пользователей: (подключим)\n"
        "— менеджеров: (подключим)\n\n"
        "Статистика будет считаться из БД.",
        reply_markup=OWNER_MENU,
    )


def register_owner_handlers(app):
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_OWNER_PANEL}$"), owner_panel))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_BACK}$"), owner_back))

    app.add_handler(
        ConversationHandler(
            entry_points=[MessageHandler(filters.Regex(f"^{BTN_ADD_MANAGER}$"), add_manager_start)],
            states={ASK_ADD_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_manager_finish)]},
            fallbacks=[MessageHandler(filters.Regex(f"^{BTN_BACK}$"), owner_back)],
            allow_reentry=True,
        )
    )

    app.add_handler(
        ConversationHandler(
            entry_points=[MessageHandler(filters.Regex(f"^{BTN_DEL_MANAGER}$"), del_manager_start)],
            states={ASK_DEL_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, del_manager_finish)]},
            fallbacks=[MessageHandler(filters.Regex(f"^{BTN_BACK}$"), owner_back)],
            allow_reentry=True,
        )
    )

    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_STATS}$"), owner_stats))
