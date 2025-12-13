import logging
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from config import OWNER_ID
from database.db import get_user_role, is_user_premium
from services.ai_analysis import finalize_analysis

logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# СТАДИИ 12-ШАГОВОГО АНАЛИЗА
# ---------------------------------------------------------
(
    STEP_NICHE,
    STEP_PRODUCT,
    STEP_PRICE_BUY,
    STEP_PRICE_SELL,
    STEP_COMMISSION,
    STEP_LOGISTICS,
    STEP_DELIVERY,
    STEP_MARKETING,
    STEP_OTHER,
    STEP_COMPETITION,
    STEP_SEASONALITY,
    STEP_RISKS,
) = range(12)


# ---------------------------------------------------------
# /analyze /analysis — старт анализа товара
# ---------------------------------------------------------
async def analysis_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id == OWNER_ID:
        await update.message.reply_text(
            "Владельцу недоступен AI-анализ с этого аккаунта.\n"
            "Используйте пользовательский профиль для тестов."
        )
        return ConversationHandler.END

    role = get_user_role(user.id)
    if role == "owner":
        await update.message.reply_text(
            "Владельцу недоступен AI-анализ. Используйте отдельный пользовательский аккаунт."
        )
        return ConversationHandler.END

    context.user_data["is_premium"] = is_user_premium(user.id)
    context.user_data["analysis"] = {}

    await update.message.reply_text(
        "📌 Шаг 1/12\n"
        "Ниша\n\n"
        "Напишите нишу, в которой хотите проверить товар."
    )
    return STEP_NICHE


# ---------------------------------------------------------
# ШАГИ
# ---------------------------------------------------------
async def step_niche(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["niche"] = update.message.text.strip()
    await update.message.reply_text("📦 Шаг 2/12\nТовар")
    return STEP_PRODUCT


async def step_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["product"] = update.message.text.strip()
    await update.message.reply_text("💰 Шаг 3/12\nЗакупочная цена")
    return STEP_PRICE_BUY


async def step_price_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["price_buy"] = update.message.text.strip()
    await update.message.reply_text("🏷 Шаг 4/12\nЦена продажи")
    return STEP_PRICE_SELL


async def step_price_sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["price_sell"] = update.message.text.strip()
    await update.message.reply_text("📊 Шаг 5/12\nКомиссия маркетплейса (%)")
    return STEP_COMMISSION


async def step_commission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["commission_percent"] = update.message.text.strip()
    await update.message.reply_text("🚚 Шаг 6/12\nЛогистика")
    return STEP_LOGISTICS


async def step_logistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["logistics"] = update.message.text.strip()
    await update.message.reply_text("📦 Шаг 7/12\nДоставка / возвраты")
    return STEP_DELIVERY


async def step_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["delivery"] = update.message.text.strip()
    await update.message.reply_text("📣 Шаг 8/12\nМаркетинг")
    return STEP_MARKETING


async def step_marketing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["marketing"] = update.message.text.strip()
    await update.message.reply_text("📎 Шаг 9/12\nПрочие расходы")
    return STEP_OTHER


async def step_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["other"] = update.message.text.strip()
    await update.message.reply_text("⚔ Шаг 10/12\nКонкуренция")
    return STEP_COMPETITION


async def step_competition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["competition"] = update.message.text.strip()
    await update.message.reply_text("📅 Шаг 11/12\nСезонность")
    return STEP_SEASONALITY


async def step_seasonality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["seasonality"] = update.message.text.strip()
    await update.message.reply_text("⚠ Шаг 12/12\nРиски")
    return STEP_RISKS


async def step_risks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["risks"] = update.message.text.strip()
    await update.message.reply_text("Запускаю AI-анализ товара… ⏳")
    await finalize_analysis(update, context, context.user_data["analysis"])
    return ConversationHandler.END


# ---------------------------------------------------------
# CANCEL
# ---------------------------------------------------------
async def cancel_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("analysis", None)
    await update.message.reply_text("Анализ товара отменён.")
    return ConversationHandler.END


# ---------------------------------------------------------
# HANDLER
# ---------------------------------------------------------
def get_analysis_conversation_handler():
    return ConversationHandler(
        entry_points=[
            CommandHandler("analyze", analysis_start),
            CommandHandler("analysis", analysis_start),
            MessageHandler(filters.Regex("^📈 Аналитика товара$"), analysis_start),
        ],
        states={
            STEP_NICHE: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_niche)],
            STEP_PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_product)],
            STEP_PRICE_BUY: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_price_buy)],
            STEP_PRICE_SELL: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_price_sell)],
            STEP_COMMISSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_commission)],
            STEP_LOGISTICS: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_logistics)],
            STEP_DELIVERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_delivery)],
            STEP_MARKETING: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_marketing)],
            STEP_OTHER: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_other)],
            STEP_COMPETITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_competition)],
            STEP_SEASONALITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_seasonality)],
            STEP_RISKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_risks)],
        },
        fallbacks=[CommandHandler("cancel", cancel_analysis)],
    )


# ---------------------------------------------------------
# РЕГИСТРАЦИЯ ДЛЯ user.py (АДАПТЕР)
# ---------------------------------------------------------
def register_analysis_product_handlers(app):
    app.add_handler(get_analysis_conversation_handler())
