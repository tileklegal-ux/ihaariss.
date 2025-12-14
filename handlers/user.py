# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from typing import Optional

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters

# =============================
# OpenAI (Async) — ONE PLACE
# =============================
try:
    from openai import AsyncOpenAI  # openai>=1.x
except Exception:
    AsyncOpenAI = None  # type: ignore

_OPENAI_CLIENT: Optional["AsyncOpenAI"] = None


def _load_system_prompt() -> str:
    """
    1) prompts/system_prompt.txt (если есть)
    2) fallback (жёстко зашитый)
    """
    path = os.path.join("prompts", "system_prompt.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            txt = f.read().strip()
            if txt:
                return txt
    except Exception:
        pass

    return (
        "Ты — спокойный аналитический бизнес-ассистент для предпринимателей СНГ.\n"
        "Ты НЕ даёшь советов и НЕ принимаешь решения за пользователя.\n"
        "Ты НЕ прогнозируешь доход, рост или успех.\n\n"
        "Твоя задача:\n"
        "— разобрать ограничения\n"
        "— указать риски\n"
        "— показать уязвимости мышления\n"
        "— предложить варианты проверки гипотез (без директив)\n\n"
        "Запрещено:\n"
        "— говорить «стоит / не стоит»\n"
        "— обещать результат\n"
        "— давить, мотивировать, вдохновлять\n\n"
        "Формат:\n"
        "коротко и структурно: 1) наблюдения 2) риски 3) варианты проверки.\n"
        "Всегда добавляй фразу: это ориентир, а не рекомендация; решение за пользователем.\n"
    )


async def ask_openai(prompt: str) -> str:
    """
    Безопасный вызов OpenAI.
    Если ключа/клиента нет — возвращаем нейтральную заглушку (бот не падает).
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or AsyncOpenAI is None:
        return (
            "AI-разбор сейчас недоступен (нет ключа/клиента).\n"
            "Это техническая пауза, а не вывод."
        )

    global _OPENAI_CLIENT
    if _OPENAI_CLIENT is None:
        _OPENAI_CLIENT = AsyncOpenAI(api_key=api_key)

    system_prompt = _load_system_prompt()
    try:
        resp = await _OPENAI_CLIENT.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
            max_tokens=450,
        )
        return (resp.choices[0].message.content or "").strip() or "Пустой ответ."
    except Exception:
        return (
            "AI-разбор временно недоступен (ошибка запроса).\n"
            "Это техническая пауза, а не вывод."
        )

# =============================
# КНОПКИ (основные)
# =============================
BTN_YES = "Да"
BTN_NO = "Нет"

BTN_BIZ = "📊 Бизнес-анализ"
BTN_PM = "💰 Прибыль и деньги"
BTN_GROWTH = "🚀 Рост и продажи"
BTN_BACK = "⬅️ Назад"
BTN_ANALYSIS = "📦 Аналитика товара"
BTN_NICHE = "🔎 Подбор ниши"
BTN_PROFILE = "👤 Личный кабинет"
BTN_PREMIUM = "❤️ Premium"
BTN_PREMIUM_BENEFITS = "📌 Что я получу конкретно"

# =============================
# КАНАЛЫ РОСТА
# =============================
GC_INST = "📸 Instagram"
GC_TG = "✈️ Telegram"
GC_KASPI = "💳 Kaspi"
GC_WB = "📦 Wildberries"
GC_OZON = "📦 Ozon"
GC_OFFLINE = "🏬 Оффлайн"

# =============================
# FSM KEYS
# =============================
INSIGHTS_KEY = "insights"

PM_STATE_KEY = "pm_state"
PM_STATE_REVENUE = "revenue"
PM_STATE_EXPENSES = "expenses"

GROWTH_KEY = "growth"

TA_STATE_KEY = "ta_state"
TA_STAGE = "ta_stage"
TA_PURPOSE = "ta_purpose"
TA_SEASON = "ta_season"
TA_COMP = "ta_comp"
TA_PRICE = "ta_price"
TA_RESOURCE = "ta_resource"

NS_STEP_KEY = "ns_step"
PREMIUM_KEY = "premium_screen"


# =============================
# HELPERS: инсайты + очистка FSM
# =============================
def _ensure_insights(context: ContextTypes.DEFAULT_TYPE):
    if INSIGHTS_KEY not in context.user_data or not isinstance(context.user_data.get(INSIGHTS_KEY), dict):
        context.user_data[INSIGHTS_KEY] = {}


def clear_fsm(context: ContextTypes.DEFAULT_TYPE):
    """ Очищаем только FSM/временные поля, НЕ трогаем insights. """
    _ensure_insights(context)
    keep = {INSIGHTS_KEY: context.user_data.get(INSIGHTS_KEY, {})}
    context.user_data.clear()
    context.user_data.update(keep)


def insights_bridge_text(context: ContextTypes.DEFAULT_TYPE) -> str:
    """ Короткая связка между сценариями. Без магии, без “я всё помню”. """
    _ensure_insights(context)
    ins = context.user_data.get(INSIGHTS_KEY, {})
    if not ins:
        return ""

    last = ins.get("last_scenario")
    last_v = ins.get("last_verdict")
    if last and last_v:
        return (
            "Я опираюсь на то, что мы уже разобрали, чтобы не начинать с нуля.\n"
            f"Прошлый ориентир: {last} → {last_v}.\n\n"
        )
    return "Я опираюсь на то, что мы уже разобрали, чтобы не начинать с нуля.\n\n"


def save_insights(
    context: ContextTypes.DEFAULT_TYPE,
    *,
    last_scenario: str,
    last_verdict: str,
    risk_level: Optional[str] = None,
    demand_type: Optional[str] = None,
    seasonality: Optional[str] = None,
    competition: Optional[str] = None,
    resource: Optional[str] = None,
):
    _ensure_insights(context)
    ins = context.user_data[INSIGHTS_KEY]
    ins["last_scenario"] = last_scenario
    ins["last_verdict"] = last_verdict
    if risk_level is not None:
        ins["risk_level"] = risk_level
    if demand_type is not None:
        ins["demand_type"] = demand_type
    if seasonality is not None:
        ins["seasonality"] = seasonality
    if competition is not None:
        ins["competition"] = competition
    if resource is not None:
        ins["resource"] = resource

# =============================
# КЛАВИАТУРЫ
# =============================
def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_BIZ)],
            [KeyboardButton(BTN_ANALYSIS)],
            [KeyboardButton(BTN_NICHE)],
            [KeyboardButton(BTN_PROFILE)],
            [KeyboardButton(BTN_PREMIUM)],
        ],
        resize_keyboard=True,
    )


def business_hub_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_PM)],
            [KeyboardButton(BTN_GROWTH)],
            [KeyboardButton(BTN_BACK)],
        ],
        resize_keyboard=True,
    )


def growth_channels_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(GC_INST), KeyboardButton(GC_TG)],
            [KeyboardButton(GC_KASPI), KeyboardButton(GC_WB)],
            [KeyboardButton(GC_OZON), KeyboardButton(GC_OFFLINE)],
            [KeyboardButton(BTN_BACK)],
        ],
        resize_keyboard=True,
    )


def step_keyboard(buttons):
    rows = [[KeyboardButton(b)] for b in buttons]
    rows.append([KeyboardButton(BTN_BACK)])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def premium_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_PREMIUM_BENEFITS)],
            [KeyboardButton(BTN_BACK)],
        ],
        resize_keyboard=True,
    )


# =============================
# PROFILE (профиль юзера)
# =============================
def generate_user_report(user_data: dict) -> str:
    insights = user_data.get("insights", {})

    last_scenario = insights.get("last_scenario", "Не указано")
    last_verdict = insights.get("last_verdict", "Не указано")
    risk_level = insights.get("risk_level", "не определён")
    demand_type = insights.get("demand_type", "неизвестно")
    seasonality = insights.get("seasonality", "неизвестна")
    competition = insights.get("competition", "неизвестна")
    resource = insights.get("resource", "неизвестен")

    report = (
        "👤 Личный кабинет\n\n"
        f"Последний сценарий: {last_scenario}\n"
        f"Вердикт: {last_verdict.capitalize()} (риск {risk_level})\n\n"
        "📊 Ключевые параметры:\n"
        f"- Тип спроса: {demand_type}\n"
        f"- Сезонность: {seasonality}\n"
        f"- Конкуренция: {competition}\n"
        f"- Ресурс: {resource}\n\n"
        "Это не рекомендация, а ориентир. Решение остаётся за тобой."
    )

    return report


# =============================
# ROUTER
# =============================
async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""

    # Кнопка профиля
    if text == BTN_PROFILE:
        _ensure_insights(context)
        report_text = generate_user_report(context.user_data)
        await update.message.reply_text(report_text, reply_markup=main_menu_keyboard())
        return

    # кнопка назад
    if text == BTN_BACK:
        await update.message.reply_text("Главное меню", reply_markup=main_menu_keyboard())
        return

    # fallback
    await update.message.reply_text("Выбери действие из меню", reply_markup=main_menu_keyboard())


# =============================
# REGISTER
# =============================
def register_handlers_user(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
