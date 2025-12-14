from typing import Dict, Any

from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    filters,
)

from database.db import is_user_premium
from services.menu import send_main_menu
from services.openai_client import ask_ai


# Кнопки главного меню пользователя — чтобы по ним прерывать аналитику
MAIN_MENU_BUTTONS = {
    "🔍 Подбор ниши",
    "📈 Аналитика товара",
    "⭐ Премиум",
    "👤 Личный кабинет",
    "ℹ️ О нас",
}

# =====================================================================
# СТАДИИ 12-ШАГОВОГО АНАЛИЗА
# =====================================================================

(
    STEP_NICHE,
    STEP_COST_PRICE,
    STEP_LOGISTICS,
    STEP_MARKETPLACE_FEE,
    STEP_EXTRA_FEES,
    STEP_SELLING_PRICE,
    STEP_DELIVERY,
    STEP_MARKETING,
    STEP_OTHER_COSTS,
    STEP_COMPETITION,
    STEP_SEASONALITY,
    STEP_RISKS,
) = range(12)

ANALYSIS_DATA_KEY = "analysis_data"


# =====================================================================
# СЛУЖЕБНАЯ ПРОВЕРКА: НЕ НАЖАЛ ЛИ ПОЛЬЗОВАТЕЛЬ КНОПКУ МЕНЮ
# =====================================================================

async def _check_menu_interrupt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    text = (update.message.text or "").strip()
    if text in MAIN_MENU_BUTTONS:
        await update.message.reply_text(
            "Аналитика товара прервана. Вы вернулись в главное меню."
        )
        context.user_data.pop(ANALYSIS_DATA_KEY, None)
        await send_main_menu(update)
        return True
    return False


# =====================================================================
# ПОСТОБРАБОТКА ОТЧЁТА
# =====================================================================

def _postprocess_report(text: str) -> str:
    if not text:
        return "Не удалось сформировать отчёт. Попробуйте ещё раз позже."

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        stripped = line.lstrip()
        while stripped.startswith("#"):
            stripped = stripped[1:].lstrip()
        stripped = stripped.replace("**", "")
        cleaned_lines.append(stripped)

    result = "\n".join(cleaned_lines).strip()
    return result or "Не удалось сформировать отчёт. Попробуйте ещё раз позже."


# =====================================================================
# PROMPT
# =====================================================================

def _build_analysis_prompt(data: Dict[str, Any], is_premium_user: bool) -> str:
    base_block = (
        "Ты — бизнес-аналитик для предпринимателей Кыргызстана и Казахстана.\n"
        "Пиши простым текстом, без markdown.\n\n"
        "Исходные данные:\n"
        f"- Ниша: {data.get('niche')}\n"
        f"- Себестоимость: {data.get('cost_price')}\n"
        f"- Логистика: {data.get('logistics')}\n"
        f"- Комиссия маркетплейса: {data.get('marketplace_fee')}\n"
        f"- Доп. комиссии: {data.get('extra_fees')}\n"
        f"- Цена продажи: {data.get('selling_price')}\n"
        f"- Доставка: {data.get('delivery')}\n"
        f"- Маркетинг: {data.get('marketing')}\n"
        f"- Прочие расходы: {data.get('other_costs')}\n"
        f"- Конкуренция: {data.get('competition')}\n"
        f"- Сезонность: {data.get('seasonality')}\n"
        f"- Риски: {data.get('risks')}\n\n"
    )

    structure = (
        "Сделай аналитический отчёт:\n"
        "1) Краткое резюме\n"
        "2) Финансовая картина\n"
        "3) Конкуренция\n"
        "4) Сезонность\n"
        "5) Риски\n"
        "6) Итог\n\n"
        "Запрещено: советы, прогнозы, обещания.\n"
        "В конце: это ориентир, а не рекомендация; решение за пользователем.\n\n"
    )

    if is_premium_user:
        premium = (
            "После отчёта добавь PREMIUM-блок:\n"
            "— сценарии\n"
            "— где уязвимости\n"
            "— что проверить первым\n\n"
        )
    else:
        premium = (
            "В конце добавь строку:\n"
            "Глубокий разбор доступен в Premium версии Artbazar AI.\n"
        )

    return base_block + structure + premium


# =====================================================================
# ОБРАБОТЧИКИ
# =====================================================================

async def start_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data[ANALYSIS_DATA_KEY] = {}
    await update.message.reply_text(
        "📈 Аналитика товара\n\n"
        "Шаг 1/12 — Ниша\n"
        "Введите нишу или категорию товара:"
    )
    return STEP_NICHE


async def step_niche(update, context):
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END
    context.user_data[ANALYSIS_DATA_KEY]["niche"] = update.message.text
    await update.message.reply_text("Шаг 2/12 — Себестоимость:")
    return STEP_COST_PRICE


async def step_cost_price(update, context):
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END
    context.user_data[ANALYSIS_DATA_KEY]["cost_price"] = update.message.text
    await update.message.reply_text("Шаг 3/12 — Логистика:")
    return STEP_LOGISTICS


async def step_logistics(update, context):
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END
    context.user_data[ANALYSIS_DATA_KEY]["logistics"] = update.message.text
    await update.message.reply_text("Шаг 4/12 — Комиссия маркетплейса:")
    return STEP_MARKETPLACE_FEE


async def step_marketplace_fee(update, context):
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END
    context.user_data[ANALYSIS_DATA_KEY]["marketplace_fee"] = update.message.text
    await update.message.reply_text("Шаг 5/12 — Дополнительные комиссии:")
    return STEP_EXTRA_FEES


async def step_extra_fees(update, context):
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END
    context.user_data[ANALYSIS_DATA_KEY]["extra_fees"] = update.message.text
    await update.message.reply_text("Шаг 6/12 — Цена продажи:")
    return STEP_SELLING_PRICE


async def step_selling_price(update, context):
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END
    context.user_data[ANALYSIS_DATA_KEY]["selling_price"] = update.message.text
    await update.message.reply_text("Шаг 7/12 — Доставка:")
    return STEP_DELIVERY


async def step_delivery(update, context):
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END
    context.user_data[ANALYSIS_DATA_KEY]["delivery"] = update.message.text
    await update.message.reply_text("Шаг 8/12 — Маркетинг:")
    return STEP_MARKETING


async def step_marketing(update, context):
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END
    context.user_data[ANALYSIS_DATA_KEY]["marketing"] = update.message.text
    await update.message.reply_text("Шаг 9/12 — Прочие расходы:")
    return STEP_OTHER_COSTS


async def step_other_costs(update, context):
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END
    context.user_data[ANALYSIS_DATA_KEY]["other_costs"] = update.message.text
    await update.message.reply_text("Шаг 10/12 — Конкуренция:")
    return STEP_COMPETITION


async def step_competition(update, context):
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END
    context.user_data[ANALYSIS_DATA_KEY]["competition"] = update.message.text
    await update.message.reply_text("Шаг 11/12 — Сезонность:")
    return STEP_SEASONALITY


async def step_seasonality(update, context):
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END
    context.user_data[ANALYSIS_DATA_KEY]["seasonality"] = update.message.text
    await update.message.reply_text("Шаг 12/12 — Риски:")
    return STEP_RISKS


async def step_risks(update, context):
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END

    context.user_data[ANALYSIS_DATA_KEY]["risks"] = update.message.text
    user_id = update.effective_user.id

    try:
        premium = is_user_premium(user_id)
    except Exception:
        premium = False

    prompt = _build_analysis_prompt(
        context.user_data[ANALYSIS_DATA_KEY],
        premium,
    )

    await update.message.reply_text("Формирую отчёт...")
    report = ask_ai(prompt)
    report = _postprocess_report(report)

    await update.message.reply_text(report)

    context.user_data.pop(ANALYSIS_DATA_KEY, None)
    await send_main_menu(update)

    return ConversationHandler.END


async def cancel_analysis(update, context):
    context.user_data.pop(ANALYSIS_DATA_KEY, None)
    await update.message.reply_text("Аналитика отменена.")
    await send_main_menu(update)
    return ConversationHandler.END


def get_analysis_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^📈 Аналитика товара$"), start_analysis)
        ],
        states={
            STEP_NICHE: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_niche)],
            STEP_COST_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_cost_price)],
            STEP_LOGISTICS: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_logistics)],
            STEP_MARKETPLACE_FEE: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_marketplace_fee)],
            STEP_EXTRA_FEES: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_extra_fees)],
            STEP_SELLING_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_selling_price)],
            STEP_DELIVERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_delivery)],
            STEP_MARKETING: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_marketing)],
            STEP_OTHER_COSTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_other_costs)],
            STEP_COMPETITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_competition)],
            STEP_SEASONALITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_seasonality)],
            STEP_RISKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_risks)],
        },
        fallbacks=[CommandHandler("cancel", cancel_analysis)],
        allow_reentry=False,
    )
