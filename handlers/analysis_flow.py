from typing import Dict, Any

from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    filters,
)
from openai import OpenAI

from config import OPENAI_API_KEY
from database.db import is_user_premium
from services.menu import send_main_menu

client = OpenAI(api_key=OPENAI_API_KEY)

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
    """
    Если пользователь вместо ответа нажал кнопку меню —
    прерываем аналитику и возвращаем главное меню.
    """
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
# ПОСТОБРАБОТКА ОТЧЁТА (РЕЖЕМ Markdown-ШУМ)
# =====================================================================

def _postprocess_report(text: str) -> str:
    if not text:
        return "Не удалось сформировать отчёт. Попробуйте ещё раз позже."

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        stripped = line.lstrip()

        # режем любые # и ## в начале строки
        while stripped.startswith("#"):
            stripped = stripped[1:].lstrip()

        # убираем **жирность**
        stripped = stripped.replace("**", "")

        cleaned_lines.append(stripped)

    result = "\n".join(cleaned_lines).strip()
    if not result:
        result = "Не удалось сформировать отчёт. Попробуйте ещё раз позже."

    return result


# =====================================================================
# ГЕНЕРАЦИЯ ИТОГОВОГО ОТЧЁТА (СТИЛЬ C3 + PREMIUM P3)
# =====================================================================

def _build_analysis_prompt(data: Dict[str, Any], is_premium_user: bool) -> str:
    """
    Формируем промпт для OpenAI в стиле:
    - C3: гибрид консалтинга + живой язык
    - P3: для премиума — два отчёта: базовый + отдельный premium-блок
    """

    base_block = (
        "Ты — бизнес-аналитик, который пишет отчёты для предпринимателей Кыргызстана и Казахстана.\n"
        "Твоя задача — сделать аналитический отчёт по товару без воды, но живым, человеческим языком.\n"
        "Не используй Markdown-разметку, решётки #, звёздочки ** и сложные списки.\n"
        "Пиши простым текстом, разделяя блоки пустыми строками.\n\n"
        "Исходные данные:\n"
        f"- Ниша / категория: {data.get('niche')}\n"
        f"- Себестоимость: {data.get('cost_price')}\n"
        f"- Логистика: {data.get('logistics')}\n"
        f"- Комиссия маркетплейса: {data.get('marketplace_fee')}\n"
        f"- Дополнительные комиссии / налоги: {data.get('extra_fees')}\n"
        f"- Цена продажи: {data.get('selling_price')}\n"
        f"- Доставка до клиента: {data.get('delivery')}\n"
        f"- Маркетинг / привлечение клиента: {data.get('marketing')}\n"
        f"- Прочие расходы: {data.get('other_costs')}\n"
        f"- Конкуренция: {data.get('competition')}\n"
        f"- Сезонность: {data.get('seasonality')}\n"
        f"- Ключевые риски: {data.get('risks')}\n\n"
    )

    # Базовый отчёт — одинаковый для всех
    base_structure = (
        "Сначала сформируй БАЗОВЫЙ ОТЧЁТ, как для обычного пользователя.\n"
        "Структура базового отчёта должна быть такой:\n"
        "1) Заголовок и краткое резюме (что за ниша и общая оценка).\n"
        "2) Описание ниши и товара простым языком.\n"
        "3) Финансовая картина: себестоимость, комиссии, логистика, прочие расходы и примерной маржи.\n"
        "4) Потенциал ниши: за счёт чего могут быть продажи, какие есть плюсы.\n"
        "5) Конкуренция: кто уже в нише и насколько сложно будет заходить.\n"
        "6) Сезонность: как время года влияет на спрос.\n"
        "7) Основные риски: без паники, но честно.\n"
        "8) Итоговый вывод: стоит ли заходить, при каких условиях, и для кого это особенно подходит.\n\n"
        "Не пиши слова 'пункт 1', 'пункт 2' — просто делай блоки с понятными подзаголовками и текстом.\n"
        "Пиши так, как будто объясняешь предпринимателю, который мыслит здраво, но не любит сложную теорию.\n\n"
    )

    if is_premium_user:
        # P3 — для премиума: два отчёта в одном
        premium_block = (
            "После того как ты полностью закончишь базовый отчёт, добавь разделитель из дефисов:\n"
            "-----\n"
            "А ниже сформируй отдельный блок PREMIUM-ОТЧЁТ.\n\n"
            "В PREMIUM-ОТЧЁТЕ сделай:\n"
            "1) Сценарный анализ: оптимистичный, базовый и пессимистичный.\n"
            "2) Комментарий по цене и марже: где можно усилить, на чём нельзя экономить.\n"
            "3) Рекомендации по запуску: как протестировать нишу небольшими партиями.\n"
            "4) Рекомендации по позиционированию: чем отличаться от конкурентов.\n"
            "5) 3–5 конкретных практических советов: что делать в первую очередь в ближайшие 30 дней.\n\n"
            "Не используй Markdown, не добавляй буллеты с тире, пиши ровным текстом, разделяя блоки пустыми строками.\n"
        )
    else:
        # Для обычного пользователя — только базовый отчёт + мягкий апселл
        premium_block = (
            "После базового отчёта добавь одну короткую отдельную строку:\n"
            "Например: 'Более глубокий разбор с сценариями и стратегией запуска доступен в премиум-версии Artbazar AI.'\n"
            "Но не расписывай сам premium-отчёт, не давай дополнительные детали.\n"
        )

    return base_block + base_structure + premium_block


def _generate_final_report_sync(data: Dict[str, Any], is_premium_user: bool) -> str:
    prompt = _build_analysis_prompt(data, is_premium_user)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0.3,
    )

    content = response.choices[0].message.content
    if not content:
        return "Не удалось сформировать отчёт. Попробуйте ещё раз позже."

    return _postprocess_report(content)


# =====================================================================
# ОБРАБОТЧИКИ 12 ШАГОВ
# =====================================================================

async def start_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Старт сценария анализа товара.
    """
    context.user_data[ANALYSIS_DATA_KEY] = {}

    text = (
        "📈 Аналитика товара\n\n"
        "Сейчас пройдём 12 шагов. Отвечайте максимально честно и конкретно — "
        "на основе этих данных бот сформирует отчёт.\n\n"
        "Шаг 1/12 — Ниша\n"
        "Напишите нишу или категорию товара.\n\n"
        "Примеры:\n"
        "- детские игрушки\n"
        "- автоаксессуары\n"
        "- товары для кухни\n"
        "- спортивное питание\n\n"
        "Введите нишу:"
    )

    await update.message.reply_text(text)
    return STEP_NICHE


async def step_niche(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END

    niche = (update.message.text or "").strip()
    context.user_data[ANALYSIS_DATA_KEY]["niche"] = niche

    text = (
        "Шаг 2/12 — Себестоимость\n\n"
        "Укажите себестоимость одной единицы товара (закупочная цена).\n\n"
        "Примеры:\n"
        "- 150 сом\n"
        "- 2 000 тенге\n\n"
        "Можно указать просто число или число + валюта:"
    )
    await update.message.reply_text(text)
    return STEP_COST_PRICE


async def step_cost_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END

    cost_price = (update.message.text or "").strip()
    context.user_data[ANALYSIS_DATA_KEY]["cost_price"] = cost_price

    text = (
        "Шаг 3/12 — Логистика\n\n"
        "Опишите, как товар попадает к вам.\n\n"
        "Примеры:\n"
        "- заказываю из Китая, доставка 30–40 дней;\n"
        "- беру у местного оптовика в Бишкеке;\n"
        "- вожу сам из Казахстана раз в месяц.\n\n"
        "Напишите кратко:"
    )
    await update.message.reply_text(text)
    return STEP_LOGISTICS


async def step_logistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END

    logistics = (update.message.text or "").strip()
    context.user_data[ANALYSIS_DATA_KEY]["logistics"] = logistics

    text = (
        "Шаг 4/12 — Комиссия маркетплейса\n\n"
        "Укажите комиссию маркетплейса или платформы в процентах.\n\n"
        "Примеры:\n"
        "- 10%\n"
        "- 15%\n"
        "- продаю без маркетплейса (так и напишите)\n\n"
        "Введите процент или опишите ситуацию:"
    )
    await update.message.reply_text(text)
    return STEP_MARKETPLACE_FEE


async def step_marketplace_fee(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END

    fee = (update.message.text or "").strip()
    context.user_data[ANALYSIS_DATA_KEY]["marketplace_fee"] = fee

    text = (
        "Шаг 5/12 — Дополнительные комиссии и налоги\n\n"
        "Есть ли дополнительные комиссии, проценты, налоги?\n\n"
        "Примеры:\n"
        "- эквайринг 2%\n"
        "- налог на самозанятых 4%\n"
        "- нет дополнительных комиссий\n\n"
        "Опишите кратко:"
    )
    await update.message.reply_text(text)
    return STEP_EXTRA_FEES


async def step_extra_fees(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END

    extra_fees = (update.message.text or "").strip()
    context.user_data[ANALYSIS_DATA_KEY]["extra_fees"] = extra_fees

    text = (
        "Шаг 6/12 — Цена продажи\n\n"
        "По какой цене вы планируете продавать товар за одну единицу?\n\n"
        "Примеры:\n"
        "- 450 сом\n"
        "- 6 990 тенге\n\n"
        "Укажите цену продажи:"
    )
    await update.message.reply_text(text)
    return STEP_SELLING_PRICE


async def step_selling_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END

    selling_price = (update.message.text or "").strip()
    context.user_data[ANALYSIS_DATA_KEY]["selling_price"] = selling_price

    text = (
        "Шаг 7/12 — Доставка до клиента\n\n"
        "Как вы планируете доставлять товар клиенту?\n\n"
        "Примеры:\n"
        "- курьер по городу, клиент оплачивает доставку отдельно;\n"
        "- отправка ТК, часть стоимости включена в цену;\n"
        "- самовывоз из точки.\n\n"
        "Опишите ваш формат доставки:"
    )
    await update.message.reply_text(text)
    return STEP_DELIVERY


async def step_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END

    delivery = (update.message.text or "").strip()
    context.user_data[ANALYSIS_DATA_KEY]["delivery"] = delivery

    text = (
        "Шаг 8/12 — Маркетинг\n\n"
        "Во сколько примерно обойдётся привлечение одного клиента?\n\n"
        "Примеры:\n"
        "- таргет 150–200 сом за заказ;\n"
        "- блогеры, бартер + доплата;\n"
        "- органика, практически без платной рекламы.\n\n"
        "Опишите ваши ожидания по маркетингу:"
    )
    await update.message.reply_text(text)
    return STEP_MARKETING


async def step_marketing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END

    marketing = (update.message.text or "").strip()
    context.user_data[ANALYSIS_DATA_KEY]["marketing"] = marketing

    text = (
        "Шаг 9/12 — Прочие расходы\n\n"
        "Есть ли дополнительные расходы, которые стоит учесть?\n\n"
        "Примеры:\n"
        "- аренда склада;\n"
        "- зарплата помощнику;\n"
        "- упаковка, коробки, пакеты;\n"
        "- нет дополнительных расходов.\n\n"
        "Напишите основные дополнительные расходы:"
    )
    await update.message.reply_text(text)
    return STEP_OTHER_COSTS


async def step_other_costs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END

    other_costs = (update.message.text or "").strip()
    context.user_data[ANALYSIS_DATA_KEY]["other_costs"] = other_costs

    text = (
        "Шаг 10/12 — Конкуренция\n\n"
        "Опишите конкуренцию в этой нише.\n\n"
        "Примеры:\n"
        "- много конкурентов, демпингуют ценой;\n"
        "- есть 2–3 сильных игрока, но есть место для новичка;\n"
        "- практически нет конкурентов, ниша пустая.\n\n"
        "Напишите, как вы видите конкуренцию:"
    )
    await update.message.reply_text(text)
    return STEP_COMPETITION


async def step_competition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END

    competition = (update.message.text or "").strip()
    context.user_data[ANALYSIS_DATA_KEY]["competition"] = competition

    text = (
        "Шаг 11/12 — Сезонность\n\n"
        "Есть ли выраженные сезоны спроса?\n\n"
        "Примеры:\n"
        "- продаётся круглый год;\n"
        "- пики продаж летом;\n"
        "- только перед праздниками.\n\n"
        "Опишите сезонность:"
    )
    await update.message.reply_text(text)
    return STEP_SEASONALITY


async def step_seasonality(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END

    seasonality = (update.message.text or "").strip()
    context.user_data[ANALYSIS_DATA_KEY]["seasonality"] = seasonality

    text = (
        "Шаг 12/12 — Ключевые риски\n\n"
        "Какие ключевые риски вы видите в этом товаре или нише?\n\n"
        "Примеры:\n"
        "- может сильно вырасти закупочная цена;\n"
        "- сложная логистика, возможны задержки;\n"
        "- тренд может быстро закончиться.\n\n"
        "Опишите основные риски:"
    )
    await update.message.reply_text(text)
    return STEP_RISKS


async def step_risks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await _check_menu_interrupt(update, context):
        return ConversationHandler.END

    risks = (update.message.text or "").strip()
    context.user_data[ANALYSIS_DATA_KEY]["risks"] = risks

    user = update.effective_user
    user_id = user.id

    analysis_data: Dict[str, Any] = context.user_data.get(ANALYSIS_DATA_KEY, {})

    # проверяем премиум-статус
    try:
        premium = is_user_premium(user_id)
    except Exception:
        premium = False

    await update.message.reply_text("Формирую отчёт по вашему товару...")

    try:
        report_text = _generate_final_report_sync(analysis_data, premium)
    except Exception:
        report_text = "Не удалось сформировать отчёт. Попробуйте ещё раз чуть позже."

    await update.message.reply_text(report_text)

    # очищаем данные
    context.user_data.pop(ANALYSIS_DATA_KEY, None)

    # после отчёта — главное меню
    await send_main_menu(update)

    return ConversationHandler.END


async def cancel_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Принудительная отмена пользователем через /cancel.
    """
    context.user_data.pop(ANALYSIS_DATA_KEY, None)
    await update.message.reply_text(
        "Аналитика товара отменена. Вы вернулись в главное меню."
    )
    await send_main_menu(update)
    return ConversationHandler.END


# =====================================================================
# ConversationHandler
# =====================================================================

def get_analysis_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex("^📈 Аналитика товара$"),
                start_analysis,
            )
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
