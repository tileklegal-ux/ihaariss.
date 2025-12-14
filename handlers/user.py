# -*- coding: utf-8 -*-

import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters,
)

from handlers.user_keyboards import (
    main_menu_keyboard,
    business_hub_keyboard,
    growth_channels_keyboard,
    step_keyboard,
    premium_keyboard,
    BTN_YES,
    BTN_NO,
    BTN_BACK,
    BTN_PM,
    BTN_GROWTH,
    BTN_ANALYSIS,
    BTN_NICHE,
    BTN_PREMIUM,
    BTN_PREMIUM_BENEFITS,
    BTN_BIZ,
)

from handlers.user_helpers import (
    clear_fsm,
    save_insights,
    insights_bridge_text,
)

from services.openai_client import ask_openai

logger = logging.getLogger(__name__)

# =============================
# FSM KEYS
# =============================

PM_STATE_KEY = "pm_state"
PM_STATE_REVENUE = "pm_revenue"
PM_STATE_EXPENSES = "pm_expenses"

GROWTH_KEY = "growth"

TA_STATE_KEY = "ta_state"
TA_STAGE = "stage"
TA_PURPOSE = "purpose"
TA_SEASON = "season"
TA_COMP = "competition"
TA_PRICE = "price"
TA_RESOURCE = "resource"

NS_STEP_KEY = "ns_step"

PREMIUM_KEY = "premium"

# =============================
# START / ONBOARDING
# =============================

async def cmd_start_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    user = update.effective_user
    name = user.first_name or user.username or "друг"

    await update.message.reply_text(
        f"Привет, {name} 👋\n\n"
        "Artbazar AI — помощник для предпринимателей.\n"
        "Здесь нет прогнозов и советов.\n"
        "Только спокойный разбор идей и рисков,\n"
        "чтобы решения принимались без лишнего давления.\n\n"
        "⚠️ Важно:\n"
        "Это не прогноз и не гарантия результата.\n"
        "Решение и ответственность остаются за тобой.\n\n"
        "Продолжим?",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(BTN_YES), KeyboardButton(BTN_NO)]],
            resize_keyboard=True,
        ),
    )

async def on_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Выбери раздел 👇",
        reply_markup=main_menu_keyboard()
    )

async def on_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Хорошо. Я рядом.",
        reply_markup=main_menu_keyboard()
    )

# =============================
# 📊 БИЗНЕС-АНАЛИЗ (ХАБ)
# =============================

async def on_business_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    await update.message.reply_text(
        "📊 Бизнес-анализ\n\n"
        "Здесь вы можете посмотреть на бизнес со стороны.\n"
        "Не чтобы найти «правильный ответ»,\n"
        "а чтобы прояснить риски, ограничения\n"
        "и точки неопределённости.",
        reply_markup=business_hub_keyboard(),
    )

# =============================
# 💰 ПРИБЫЛЬ И ДЕНЬГИ
# =============================

async def pm_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data[PM_STATE_KEY] = PM_STATE_REVENUE
    bridge = insights_bridge_text(context)

    await update.message.reply_text(
        bridge +
        "💰 Прибыль и деньги\n\n"
        "Укажи выручку за выбранный месяц.\n"
        "Сколько денег фактически поступило от клиентов.\n"
        "Без прогнозов и ожиданий — только реальные поступления.\n"
        "Период важен: считаем один конкретный месяц.",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(BTN_BACK)]],
            resize_keyboard=True
        ),
    )

async def pm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_raw = update.message.text or ""
    text = text_raw.replace(" ", "").replace(",", "").strip()

    if not text.isdigit():
        await update.message.reply_text("Введи число, без букв.")
        return

    state = context.user_data.get(PM_STATE_KEY)

    if state == PM_STATE_REVENUE:
        context.user_data["revenue"] = int(text)
        context.user_data[PM_STATE_KEY] = PM_STATE_EXPENSES
        await update.message.reply_text(
            "Теперь укажи расходы за этот же месяц.\n"
            "Закупки, реклама, аренда, сервисы, комиссии.\n"
            "Если сомневаешься — лучше завысить, чем забыть.\n"
            "Нужна общая сумма."
        )
        return

    if state == PM_STATE_EXPENSES:
        revenue = context.user_data.get("revenue", 0)
        expenses = int(text)
        profit = revenue - expenses
        margin = (profit / revenue * 100) if revenue else 0

        risk_level = "средний"
        if revenue == 0 or margin < 0:
            risk_level = "высокий"
        elif margin >= 10:
            risk_level = "низкий"

        last_verdict = "Осторожно"
        if margin >= 10:
            last_verdict = "Можно смотреть"
        if margin < 0:
            last_verdict = "Высокий риск"

        save_insights(
            context,
            last_scenario="💰 Деньги",
            last_verdict=last_verdict,
            risk_level=risk_level
        )

        clear_fsm(context)

        base_text = (
            "Итог за месяц:\n"
            "Прибыль — разница между выручкой и расходами.\n"
            "Маржа показывает, сколько остаётся с каждого рубля.\n"
            "Это не оценка бизнеса, а снимок текущего состояния.\n\n"
            f"Выручка: {revenue}\n"
            f"Расходы: {expenses}\n"
            f"Прибыль: {profit}\n"
            f"Маржа: {margin:.1f}%\n"
        )

        ai_prompt = (
            "Сделай короткий аналитический комментарий по месячной модели.\n"
            "Запрещено: обещать доход/рост, давать прямые советы.\n"
            "Нужно: 1) наблюдения 2) риски 3) варианты проверки.\n"
            "В конце: это ориентир, а не рекомендация; решение за пользователем.\n\n"
            f"Данные: выручка={revenue}, расходы={expenses}, прибыль={profit}, маржа%={margin:.1f}.\n"
        )

        ai_text = await ask_openai(ai_prompt)

        await update.message.reply_text(
            base_text + "\nКороткий разбор:\n" + ai_text,
            reply_markup=business_hub_keyboard(),
        )

# =============================
# 🚀 РОСТ И ПРОДАЖИ
# =============================

async def growth_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data[GROWTH_KEY] = True
    bridge = insights_bridge_text(context)

    await update.message.reply_text(
        bridge +
        "🚀 Рост и продажи\n\n"
        "Этот шаг нужен не для оценки эффективности.\n"
        "Мы просто фиксируем, откуда клиенты приходят сейчас,\n"
        "без ожиданий и планов на рост.\n\n"
        "Выбери канал, который реально приводит клиентов сегодня,\n"
        "даже если он кажется нестабильным или случайным.",
        reply_markup=growth_channels_keyboard(),
    )

async def growth_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel = update.message.text or ""

    save_insights(
        context,
        last_scenario="🚀 Рост",
        last_verdict="Зафиксировали текущий канал"
    )
    clear_fsm(context)

    await update.message.reply_text(
        "📈 Текущая картина:\n\n"
        f"Источник клиентов: {channel}\n\n"
        "Мы зафиксировали основной источник клиентов.\n"
        "Это не оценка и не вывод о качестве канала,\n"
        "а точка текущего состояния.\n\n"
        "Рост — это нагрузка на систему.\n"
        "Важно не ускоряться, а понимать пределы и узкие места.",
        reply_markup=business_hub_keyboard(),
    )

# =============================
# ROUTER + REGISTER
# =============================

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""

    if text == BTN_PREMIUM_BENEFITS:
        await premium_benefits(update, context)
        return

    if text == BTN_BACK:
        clear_fsm(context)
        await update.message.reply_text(
            "Главное меню",
            reply_markup=main_menu_keyboard()
        )
        return

    if context.user_data.get(PM_STATE_KEY):
        await pm_handler(update, context)
        return

    if context.user_data.get(GROWTH_KEY):
        await growth_handler(update, context)
        return

def register_handlers_user(app):
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_YES}$"), on_yes))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NO}$"), on_no))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_BIZ}$"), on_business_analysis))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PM}$"), pm_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_GROWTH}$"), growth_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
