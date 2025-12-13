import logging
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

# Импортируем шаги анализа ТОЛЬКО из analysis_flow.py
from handlers.analysis_flow import (
    analysis_start,
    step_niche,
    step_product,
    step_buy,
    step_sell,
    step_commission,
    step_logistics,
    step_delivery,
    step_marketing,
    step_other,
    step_competition,
    step_seasonality,
    step_risks,
)

# Константы шагов
from services.artbazar_table_flow import (
    STEP_NICHE,
    STEP_PRODUCT,
    STEP_BUY,
    STEP_SELL,
    STEP_COMMISSION,
    STEP_LOGISTICS,
    STEP_DELIVERY,
    STEP_MARKETING,
    STEP_OTHER,
    STEP_COMPETITION,
    STEP_SEASONALITY,
    STEP_RISKS,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Старт анализа (через команду или кнопку)
# ---------------------------------------------------------
async def start_analysis_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await analysis_start(update, context)


# ---------------------------------------------------------
# ConversationHandler — безопасный, без циклических импортов
# ---------------------------------------------------------
def get_analysis_conversation():

    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^📊 Анализ товара$"), start_analysis_flow),
            CommandHandler("analysis", start_analysis_flow),
            CommandHandler("analyze", start_analysis_flow),
        ],
        allow_reentry=True,
        states={
            STEP_NICHE: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_niche)],
            STEP_PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_product)],
            STEP_BUY: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_buy)],
            STEP_SELL: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_sell)],
            STEP_COMMISSION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, step_commission)
            ],
            STEP_LOGISTICS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, step_logistics)
            ],
            STEP_DELIVERY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, step_delivery)
            ],
            STEP_MARKETING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, step_marketing)
            ],
            STEP_OTHER: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_other)],
            STEP_COMPETITION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, step_competition)
            ],
            STEP_SEASONALITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, step_seasonality)
            ],
            STEP_RISKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_risks)],
        },
        fallbacks=[],
    )


# ---------------------------------------------------------
# РЕГИСТРАЦИЯ ХЕНДЛЕРА
# ---------------------------------------------------------
def register_user_analysis_handlers(app):
    app.add_handler(get_analysis_conversation())
