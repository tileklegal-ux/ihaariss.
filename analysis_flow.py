import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from database.db import get_user_role, is_user_premium
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
    finalize_analysis,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# START ANALYSIS
# ---------------------------------------------------------
async def analysis_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    role = get_user_role(user_id)

    if role == "owner":
        await update.message.reply_text(
            "Владельцу недоступен AI-анализ. Используйте отдельный пользовательский аккаунт."
        )
        return ConversationHandler.END

    context.user_data["is_premium"] = is_user_premium(user_id)
    context.user_data["analysis"] = {}

    await update.message.reply_text(
        "Шаг 1 из 12\nНиша\nПожалуйста, укажите нишу товара.\nНапример: одежда, товары для дома, техника"
    )
    return STEP_NICHE


# ---------------------------------------------------------
# STEPS
# ---------------------------------------------------------
async def step_niche(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["niche"] = update.message.text
    await update.message.reply_text(
        "Шаг 2 из 12\nТовар\nПожалуйста, укажите товар."
    )
    return STEP_PRODUCT


async def step_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["product"] = update.message.text
    await update.message.reply_text(
        "Шаг 3 из 12\nЗакупочная цена\nУкажите цену закупки."
    )
    return STEP_BUY


async def step_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["price_buy"] = update.message.text
    await update.message.reply_text("Шаг 4 из 12\nЦена продажи")
    return STEP_SELL


async def step_sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["price_sell"] = update.message.text
    await update.message.reply_text("Шаг 5 из 12\nКомиссия (%)")
    return STEP_COMMISSION


async def step_commission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["commission_percent"] = update.message.text
    await update.message.reply_text("Шаг 6 из 12\nЛогистика")
    return STEP_LOGISTICS


async def step_logistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["logistics"] = update.message.text
    await update.message.reply_text("Шаг 7 из 12\nДоставка")
    return STEP_DELIVERY


async def step_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["delivery"] = update.message.text
    await update.message.reply_text("Шаг 8 из 12\nМаркетинг")
    return STEP_MARKETING


async def step_marketing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["marketing"] = update.message.text
    await update.message.reply_text("Шаг 9 из 12\nПрочие расходы")
    return STEP_OTHER


async def step_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["other"] = update.message.text
    await update.message.reply_text("Шаг 10 из 12\nКонкуренция")
    return STEP_COMPETITION


async def step_competition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["competition"] = update.message.text
    await update.message.reply_text("Шаг 11 из 12\nСезонность")
    return STEP_SEASONALITY


async def step_seasonality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["seasonality"] = update.message.text
    await update.message.reply_text("Шаг 12 из 12\nРиски")
    return STEP_RISKS


async def step_risks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["analysis"]["risks"] = update.message.text

    data = context.user_data["analysis"]
    await finalize_analysis(update, context, data)

    return ConversationHandler.END
