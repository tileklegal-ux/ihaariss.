from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    filters,
)

from database.db import (
    get_user_role,
    get_user_by_username,
    give_premium_days,
)
from services.audit_log import log_event
from services.premium_notifications import (
    notify_premium_activated,
    notify_premium_revoked,
)

# -------------------------------------------------
# BUTTONS
# -------------------------------------------------
BTN_MANAGER_PANEL = "👨‍💼 Панель менеджера"
BTN_GRANT = "✅ Активировать Premium"
BTN_REVOKE = "❌ Отменить Premium"
BTN_BACK = "⬅️ Назад"

ASK_USERNAME = 1
ASK_DAYS = 2
ASK_REVOKE = 3

MANAGER_MENU = ReplyKeyboardMarkup(
    [
        [KeyboardButton(BTN_GRANT)],
        [KeyboardButton(BTN_REVOKE)],
        [KeyboardButton(BTN_BACK)],
    ],
    resize_keyboard=True,
)

# -------------------------------------------------
# PANEL — ❗️НЕ ConversationHandler
# -------------------------------------------------
async def manager_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if get_user_role(update.effective_user.id) != "manager":
        return

    log_event(update.effective_user.id, "manager_open_panel")

    await update.message.reply_text(
        "👨‍💼 Панель менеджера",
        reply_markup=MANAGER_MENU,
    )

# -------------------------------------------------
# GRANT PREMIUM
# -------------------------------------------------
async def grant_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Отправь @username пользователя",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ASK_USERNAME

async def grant_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.replace("@", "").strip()
    user = get_user_by_username(username)

    if not user:
        await update.message.reply_text("❌ Пользователь не найден.")
        return ConversationHandler.END

    context.user_data["uid"] = user["id"]
    context.user_data["username"] = username

    await update.message.reply_text(
        "Выбери срок:",
        reply_markup=ReplyKeyboardMarkup(
            [
                [KeyboardButton("30")],
                [KeyboardButton("180")],
                [KeyboardButton("365")],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )
    return ASK_DAYS

async def grant_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    days = int(update.message.text.strip())
    uid = context.user_data["uid"]
    username = context.user_data["username"]

    give_premium_days(uid, days)

    await notify_premium_activated(
        bot=context.bot,
        user_id=uid,
    )

    log_event(
        update.effective_user.id,
        f"premium_granted @{username} {days}d",
    )

    await update.message.reply_text(
        f"⭐ Premium активирован для @{username} на {days} дней",
        reply_markup=MANAGER_MENU,
    )

    context.user_data.clear()
    return ConversationHandler.END

# -------------------------------------------------
# REVOKE PREMIUM
# -------------------------------------------------
async def revoke_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Отправь @username для отключения Premium",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ASK_REVOKE

async def revoke_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.replace("@", "").strip()
    user = get_user_by_username(username)

    if not user:
        await update.message.reply_text("❌ Пользователь не найден.")
        return ConversationHandler.END

    give_premium_days(user["id"], -36500)

    await notify_premium_revoked(
        bot=context.bot,
        user_id=user["id"],
    )

    log_event(
        update.effective_user.id,
        f"premium_revoked @{username}",
    )

    await update.message.reply_text(
        f"❌ Premium отключён для @{username}",
        reply_markup=MANAGER_MENU,
    )

    return ConversationHandler.END

# -------------------------------------------------
# REGISTRATION
# -------------------------------------------------
def register_manager_handlers(app):
    # Панель менеджера — ОТДЕЛЬНО
    app.add_handler(
        MessageHandler(filters.Regex(f"^{BTN_MANAGER_PANEL}$"), manager_panel)
    )

    # Grant Premium
    app.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex(f"^{BTN_GRANT}$"), grant_start)
            ],
            states={
                ASK_USERNAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, grant_days)
                ],
                ASK_DAYS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, grant_finish)
                ],
            },
            fallbacks=[],
        )
    )

    # Revoke Premium
    app.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex(f"^{BTN_REVOKE}$"), revoke_start)
            ],
            states={
                ASK_REVOKE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, revoke_finish)
                ],
            },
            fallbacks=[],
        )
    )
