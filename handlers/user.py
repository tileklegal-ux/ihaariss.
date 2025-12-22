# -*- coding: utf-8 -*-

import logging

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from telegram.ext import ApplicationHandlerStop
from handlers.user_keyboards import (
    BTN_AI_CHAT,  # 🤖 AI-наставник (одноразовый вопрос-ответ)
    main_menu_keyboard,
    business_hub_keyboard,
    pm_step_keyboard,
    growth_step_keyboard,
    step_keyboard,
    premium_keyboard,
    BTN_BACK,
    BTN_YES,
    BTN_NO,
    BTN_PM,
    BTN_GROWTH,
    BTN_ANALYSIS,
    BTN_NICHE,
    BTN_PROFILE,
    BTN_PREMIUM,
    BTN_PREMIUM_BENEFITS,
    BTN_BIZ,
    BTN_DOCS,
    BTN_COMPANY_STAGE,
)

from handlers.user_texts import t as T
from handlers.user_helpers import clear_fsm, save_insights
from handlers.profile import on_profile, on_export_excel, on_export_pdf
from handlers.documents import on_documents
from handlers.company_stage import (
    start_company_stage,
    handle_company_stage,
    handle_company_stage_export,
    COMPANY_STAGE_STATE,
)

from services.openai_client import ask_openai
from database.db import is_user_premium, get_user_role

logger = logging.getLogger(__name__)

# =============================
# FSM KEYS
# =============================
PM_STATE_KEY = "pm_state"
PM_STEP = "pm_step"

GROWTH_KEY = "growth_state"
GROWTH_STEP = "growth_step"

TA_STATE_KEY = "ta_state"
TA_STEP = "ta_step"
TA_STAGE = "ta_stage"
TA_REASON = "ta_reason"
TA_SEASON = "ta_season"
TA_COMP = "ta_comp"
TA_PRICE = "ta_price"
TA_RESOURCE = "ta_resource"

NS_STEP_KEY = "ns_step"

ONBOARDING_KEY = "onboarding"

# Канон: AI-наставник — НЕ режим. Разрешено только одноразовое ожидание 1 вопроса.
AI_MENTOR_PENDING_KEY = "ai_mentor_pending"
AI_DIALOG_ACTIVE_KEY = "ai_dialog_active"
# =============================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =============================


def _safe_text(update: Update) -> str:
    return (update.message.text or "").strip() if update and update.message else ""


def _is_user_context(update: Update) -> bool:
    return bool(update and update.effective_user)


# =============================
# START / ONBOARDING
# =============================


async def cmd_start_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data.pop(AI_MENTOR_PENDING_KEY, None)

    if "lang" not in context.user_data:
        context.user_data["lang"] = "ru"

    context.user_data[ONBOARDING_KEY] = True

    user = update.effective_user
    name = user.first_name or user.username or "друг"
    lang = context.user_data["lang"]

    await update.message.reply_text(
        T(lang, "start_greeting", name=name),
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(BTN_YES), KeyboardButton(BTN_NO)]],
            resize_keyboard=True,
        ),
    )


async def on_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop(ONBOARDING_KEY, None)
    context.user_data.pop(AI_MENTOR_PENDING_KEY, None)
    clear_fsm(context)

    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(
        T(lang, "choose_section"),
        reply_markup=main_menu_keyboard(),
    )


async def on_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop(ONBOARDING_KEY, None)
    context.user_data.pop(AI_MENTOR_PENDING_KEY, None)
    clear_fsm(context)

    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(
        "Хорошо. Я рядом.",
        reply_markup=main_menu_keyboard(),
    )


# =============================
# 📊 БИЗНЕС-АНАЛИЗ (ХАБ) - ТОЛЬКО ПОДМЕНЮ
# =============================


async def on_business_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data["in_business_submenu"] = True
    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(
        T(lang, "business_hub_intro"),
        reply_markup=business_hub_keyboard(),
    )


# =============================
# 💰 ПРИБЫЛЬ И ДЕНЬГИ (FSM) - ТОЛЬКО В ПОДМЕНЮ
# =============================


async def pm_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data[PM_STATE_KEY] = True
    context.user_data[PM_STEP] = 1

    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(
        T(lang, "pm_intro"),
        reply_markup=pm_step_keyboard(1),
    )


async def pm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = _safe_text(update)
    lang = context.user_data.get("lang", "ru")
    step = int(context.user_data.get(PM_STEP, 1))

    if text == BTN_BACK:
        clear_fsm(context)
        context.user_data["in_business_submenu"] = True
        await update.message.reply_text(
            "📊 Бизнес-анализ",
            reply_markup=business_hub_keyboard(),
        )
        return

    if step == 1:
        context.user_data["pm_type"] = text
        context.user_data[PM_STEP] = 2
        await update.message.reply_text(
            T(lang, "pm_step1"),
            reply_markup=pm_step_keyboard(2),
        )
        return

    if step == 2:
        context.user_data["pm_source"] = text
        context.user_data[PM_STEP] = 3
        await update.message.reply_text(
            T(lang, "pm_step2"),
            reply_markup=pm_step_keyboard(3),
        )
        return

    if step == 3:
        context.user_data["pm_fixed"] = text
        context.user_data[PM_STEP] = 4
        await update.message.reply_text(
            T(lang, "pm_step3"),
            reply_markup=pm_step_keyboard(4),
        )
        return

    if step == 4:
        context.user_data["pm_variable"] = text
        context.user_data[PM_STEP] = 5
        await update.message.reply_text(
            T(lang, "pm_step4"),
            reply_markup=pm_step_keyboard(5),
        )
        return

    if step == 5:
        context.user_data["pm_profitability"] = text

        insights = (
            "📊 Анализ прибыли и денег:\n\n"
            f"Тип бизнеса: {context.user_data.get('pm_type', '')}\n"
            f"Источник выручки: {context.user_data.get('pm_source', '')}\n"
            f"Постоянные расходы: {context.user_data.get('pm_fixed', '')}\n"
            f"Переменные расходы: {context.user_data.get('pm_variable', '')}\n"
            f"Рентабельность: {context.user_data.get('pm_profitability', '')}\n\n"
            "Это аналитический снимок, не рекомендация."
        )

        ai_prompt = (
            "Сделай короткий аналитический комментарий по модели прибыли.\n"
            "Запрещено: советы, обещания, прогнозы, директивы.\n"
            "Нужно: 1) наблюдения 2) риски 3) варианты проверки.\n"
            "В конце: это ориентир, а не рекомендация; решение за пользователем.\n\n"
            f"Данные:\n{insights}\n"
        )

        await update.message.reply_text(insights, reply_markup=business_hub_keyboard())

        try:
            await update.message.chat.send_action("typing")
            ai_text = await ask_openai(ai_prompt)
            await update.message.reply_text(ai_text, reply_markup=business_hub_keyboard())
        except Exception:
            await update.message.reply_text(
                "⚠️ Не удалось получить AI-комментарий.",
                reply_markup=business_hub_keyboard(),
            )

        save_insights(context, insights)
        clear_fsm(context)
        await update.message.reply_text("📊 Бизнес-анализ", reply_markup=business_hub_keyboard())
        return


# =============================
# 🚀 РОСТ И ПРОДАЖИ (FSM) - ПОЛНЫЙ 5 ШАГОВ
# =============================


async def growth_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data[GROWTH_KEY] = True
    context.user_data[GROWTH_STEP] = 1

    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(
        T(lang, "growth_intro"),
        reply_markup=growth_step_keyboard(1),
    )


async def growth_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = _safe_text(update)
    lang = context.user_data.get("lang", "ru")
    step = int(context.user_data.get(GROWTH_STEP, 1))

    if text == BTN_BACK:
        clear_fsm(context)
        await update.message.reply_text("📊 Бизнес-анализ", reply_markup=business_hub_keyboard())
        return

    if step == 1:
        context.user_data["growth_channel"] = text
        context.user_data[GROWTH_STEP] = 2
        await update.message.reply_text(
            T(lang, "growth_step1"),
            reply_markup=growth_step_keyboard(2),
        )
        return

    if step == 2:
        context.user_data["growth_conversion"] = text
        context.user_data[GROWTH_STEP] = 3
        await update.message.reply_text(
            T(lang, "growth_step2"),
            reply_markup=growth_step_keyboard(3),
        )
        return

    if step == 3:
        context.user_data["growth_cost"] = text
        context.user_data[GROWTH_STEP] = 4
        await update.message.reply_text(
            T(lang, "growth_step3"),
            reply_markup=growth_step_keyboard(4),
        )
        return

    if step == 4:
        context.user_data["growth_retention"] = text
        context.user_data[GROWTH_STEP] = 5
        await update.message.reply_text(
            T(lang, "growth_step4"),
            reply_markup=growth_step_keyboard(5),
        )
        return

    if step == 5:
        context.user_data["growth_plans"] = text

        insights = (
            "🚀 Анализ роста и продаж:\n\n"
            f"Канал привлечения: {context.user_data.get('growth_channel', '')}\n"
            f"Конверсия: {context.user_data.get('growth_conversion', '')}\n"
            f"Стоимость привлечения: {context.user_data.get('growth_cost', '')}\n"
            f"Удержание клиентов: {context.user_data.get('growth_retention', '')}\n"
            f"Планы роста: {context.user_data.get('growth_plans', '')}\n\n"
            "Это аналитический снимок, не рекомендация."
        )

        ai_prompt = (
            "Сделай короткий аналитический комментарий по модели роста.\n"
            "Запрещено: советы, обещания, прогнозы, директивы.\n"
            "Нужно: 1) наблюдения 2) риски 3) варианты проверки.\n"
            "В конце: это ориентир, а не рекомендация; решение за пользователем.\n\n"
            f"Данные:\n{insights}\n"
        )

        await update.message.reply_text(insights, reply_markup=business_hub_keyboard())

        try:
            await update.message.chat.send_action("typing")
            ai_text = await ask_openai(ai_prompt)
            await update.message.reply_text(ai_text, reply_markup=business_hub_keyboard())
        except Exception:
            await update.message.reply_text(
                "⚠️ Не удалось получить AI-комментарий.",
                reply_markup=business_hub_keyboard(),
            )

        save_insights(context, insights)
        clear_fsm(context)
        await update.message.reply_text("📊 Бизнес-анализ", reply_markup=business_hub_keyboard())
        return


# =============================
# 📦 АНАЛИТИКА ТОВАРА (FSM)
# =============================


async def ta_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data[TA_STATE_KEY] = True
    context.user_data[TA_STEP] = 1

    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(T(lang, "ta_intro"), reply_markup=step_keyboard())


async def ta_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "ru")
    text = _safe_text(update)
    step = int(context.user_data.get(TA_STEP, 1))

    if text == BTN_BACK:
        clear_fsm(context)
        await update.message.reply_text("📊 Бизнес-анализ", reply_markup=business_hub_keyboard())
        return

    if step == 1:
        context.user_data[TA_STAGE] = text
        context.user_data[TA_STEP] = 2
        await update.message.reply_text(T(lang, "ta_reason_ask"), reply_markup=step_keyboard())
        return

    if step == 2:
        context.user_data[TA_REASON] = text
        context.user_data[TA_STEP] = 3
        await update.message.reply_text(T(lang, "ta_season_ask"), reply_markup=step_keyboard())
        return

    if step == 3:
        context.user_data[TA_SEASON] = text
        context.user_data[TA_STEP] = 4
        await update.message.reply_text(T(lang, "ta_comp_ask"), reply_markup=step_keyboard())
        return

    if step == 4:
        context.user_data[TA_COMP] = text
        context.user_data[TA_STEP] = 5
        await update.message.reply_text(T(lang, "ta_price_ask"), reply_markup=step_keyboard())
        return

    if step == 5:
        context.user_data[TA_PRICE] = text
        context.user_data[TA_STEP] = 6
        await update.message.reply_text(T(lang, "ta_resource_ask"), reply_markup=step_keyboard())
        return

    if step == 6:
        context.user_data[TA_RESOURCE] = text

        stage = context.user_data.get(TA_STAGE, "")
        reason = context.user_data.get(TA_REASON, "")
        season = context.user_data.get(TA_SEASON, "")
        comp = context.user_data.get(TA_COMP, "")
        price = context.user_data.get(TA_PRICE, "")
        res = context.user_data.get(TA_RESOURCE, "")

        insights = (
            "Аналитический срез товара зафиксирован.\n"
            "Это ориентир и структура мыслей.\n\n"
            f"Стадия: {stage}\n"
            f"Причина покупки: {reason}\n"
            f"Сезонность: {season}\n"
            f"Конкуренция: {comp}\n"
            f"Чувствительность к цене: {price}\n"
            f"Ресурсы: {res}\n"
        )

        ai_prompt = (
            "Сделай короткий аналитический разбор товара.\n"
            "Запрещено: советы, обещания, прогнозы, директивы.\n"
            "Нужно: 1) наблюдения 2) риски 3) варианты проверки.\n"
            "В конце: это ориентир, а не рекомендация; решение за пользователем.\n\n"
            f"{insights}\n"
        )

        await update.message.reply_text(insights, reply_markup=business_hub_keyboard())

        try:
            await update.message.chat.send_action("typing")
            ai_text = await ask_openai(ai_prompt)
            await update.message.reply_text(ai_text, reply_markup=business_hub_keyboard())
        except Exception:
            await update.message.reply_text(
                "⚠️ Не удалось получить AI-комментарий.",
                reply_markup=business_hub_keyboard(),
            )

        save_insights(context, insights)
        clear_fsm(context)
        await update.message.reply_text("📊 Бизнес-анализ", reply_markup=business_hub_keyboard())
        return


# =============================
# 🔎 ПОДБОР НИШИ (FSM)
# =============================


async def ns_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data[NS_STEP_KEY] = 1

    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(T(lang, "ns_intro"), reply_markup=step_keyboard())


async def ns_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "ru")
    text = _safe_text(update)
    step = int(context.user_data.get(NS_STEP_KEY, 1))

    if text == BTN_BACK:
        clear_fsm(context)
        await update.message.reply_text("📊 Бизнес-анализ", reply_markup=business_hub_keyboard())
        return

    if step == 1:
        context.user_data["ns_goal"] = text
        context.user_data[NS_STEP_KEY] = 2
        await update.message.reply_text(T(lang, "ns_format_ask"), reply_markup=step_keyboard())
        return

    if step == 2:
        context.user_data["ns_format"] = text
        context.user_data[NS_STEP_KEY] = 3
        await update.message.reply_text(T(lang, "ns_demand_ask"), reply_markup=step_keyboard())
        return

    if step == 3:
        context.user_data["ns_demand"] = text
        context.user_data[NS_STEP_KEY] = 4
        await update.message.reply_text(T(lang, "ns_season_ask"), reply_markup=step_keyboard())
        return

    if step == 4:
        context.user_data["ns_season"] = text
        context.user_data[NS_STEP_KEY] = 5
        await update.message.reply_text(T(lang, "ns_competition_ask"), reply_markup=step_keyboard())
        return

    if step == 5:
        context.user_data["ns_comp"] = text
        context.user_data[NS_STEP_KEY] = 6
        await update.message.reply_text(T(lang, "ns_resources_ask"), reply_markup=step_keyboard())
        return

    if step == 6:
        context.user_data["ns_res"] = text

        insights = (
            "Ниша зафиксирована как аналитический ориентир.\n\n"
            f"Цель: {context.user_data.get('ns_goal', '')}\n"
            f"Формат: {context.user_data.get('ns_format', '')}\n"
            f"Тип спроса: {context.user_data.get('ns_demand', '')}\n"
            f"Сезонность: {context.user_data.get('ns_season', '')}\n"
            f"Конкуренция: {context.user_data.get('ns_comp', '')}\n"
            f"Ресурсы: {context.user_data.get('ns_res', '')}\n"
        )

        ai_prompt = (
            "Сделай краткий аналитический срез по нише.\n"
            "Запрещено: советы, обещания, прогнозы, директивы.\n"
            "Нужно: 1) наблюдения 2) риски 3) варианты проверки.\n"
            "В конце: это ориентир, а не рекомендация; решение за пользователем.\n\n"
            f"{insights}\n"
        )

        await update.message.reply_text(insights, reply_markup=main_menu_keyboard())

        try:
            await update.message.chat.send_action("typing")
            ai_text = await ask_openai(ai_prompt)
            await update.message.reply_text(ai_text, reply_markup=main_menu_keyboard())
        except Exception:
            await update.message.reply_text(
                "⚠️ Не удалось получить AI-комментарий.",
                reply_markup=main_menu_keyboard(),
            )

        save_insights(context, insights)
        clear_fsm(context)
        await update.message.reply_text(T(lang, "choose_section"), reply_markup=main_menu_keyboard())
        return


# =============================
# ⭐ PREMIUM
# =============================


async def premium_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(
        T(lang, "premium_intro"),
        reply_markup=premium_keyboard(),
    )


async def premium_benefits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        (
            "📌 Что ты получишь в Premium:\n\n"
            "1️⃣ Более глубокий анализ ниши и рисков\n"
            "2️⃣ История и логика выводов\n"
            "3️⃣ Возможность экспорта (PDF / Excel)\n"
            "4️⃣ Полный анализ этапа компании (10 вопросов)\n\n"
            "⚠️ Это ориентир, а не инвестиционная рекомендация.\n"
            "Решение всегда остаётся за тобой.\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "🔐 Как активировать Premium:\n\n"
            "Для активации Premium отправь менеджеру свой Telegram ID.\n\n"
            "Как узнать свой Telegram ID:\n"
            "1️⃣ Напиши боту @userinfobot\n"
            "2️⃣ Скопируй число (ID)\n"
            "3️⃣ Отправь его менеджеру\n"
        ),
        reply_markup=premium_keyboard(),
    )


# =============================
# 🧭 AI-НАСТАВНИК — ОДНОРАЗОВО (НЕ РЕЖИМ)
# =============================


async def ai_mentor_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)

    context.user_data[AI_DIALOG_ACTIVE_KEY] = True

    await update.message.reply_text(
        "🧭 AI-наставник\n\n"
        "Я здесь, чтобы разобраться в твоей ситуации глубоко.\n"
        "Опиши контекст, задай вопрос или просто начни с того, что сейчас волнует.\n\n"
        "Диалог продолжится, пока ты сам не решишь выйти.",
    )

    await update.message.reply_text(
    "Напиши свой вопрос или опиши ситуацию 👇",
    reply_markup=ReplyKeyboardMarkup([[KeyboardButton(BTN_BACK)]], resize_keyboard=True),
    )


async def ai_mentor_handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop(AI_MENTOR_PENDING_KEY, None)

    user_text = _safe_text(update)
    if not user_text or user_text.startswith("/"):
        return

    

    user_id = update.effective_user.id
    try:
        premium = is_user_premium(user_id)
    except Exception:
        premium = False

    # ↓↓↓ ДАЛЬШЕ ИДЁТ ТВОЙ prompt (его НЕ трогаем)

    if not premium:
        prompt = (
    "Ты — AI-наставник предпринимателя, работающий как опытный бизнес-партнёр.\n\n"
    "Твоя задача — глубоко понять бизнес пользователя, его контекст, ограничения и цели, "
    "и только после этого помогать формировать решения.\n\n"
    "Ключевое правило:\n"
    "— Ты НЕ ограничен количеством вопросов.\n"
    "— Ты обязан задавать уточняющие вопросы до тех пор, пока картина бизнеса не станет ясной.\n\n"
    "Ты должен учитывать:\n"
    "— Финансы и налоги\n"
    "— Рынок и конкуренцию\n"
    "— Человеческий фактор (владелец, команда, усталость, страхи)\n"
    "— Законодательство и регуляторные риски\n"
    "— Региональные особенности\n\n"
    "Контекст 2025 (Кыргызстан и Казахстан):\n"
    "— Кыргызстан: цифровизация налогов, ККМ, маркировка, ЭТТН, рост ВВП и дефицит кадров.\n"
    "— Казахстан: административные барьеры, штрафные риски, господдержка и кадровое давление.\n"
    "— Общие тренды: рост торговли КР↔РК, финтех, автоматизация, ИИ в бизнесе.\n\n"
    "Формат ответа:\n"
    "1. Кратко отрази, как ты понял текущую ситуацию пользователя.\n"
    "2. Отметь ключевые риски, противоречия или слепые зоны.\n"
    "3. Задавай уточняющие вопросы (столько, сколько нужно), чтобы понять бизнес до конца.\n"
    "4. Не давай финальных рекомендаций, пока понимание не станет полным.\n\n"
    "Тон:\n"
    "— Профессиональный\n"
    "— Спокойный\n"
    "— Человечный\n"
    "— Без давления и без шаблонов\n\n"
    f"Ситуация пользователя:\n{user_text}"
        )
    else:
        prompt = (
    "Ты — AI-наставник для предпринимателей.\n\n"
    "Твоя задача — быстро понять суть бизнес-ситуации пользователя и дать ценную, "
    "но ограниченную по глубине аналитику.\n\n"
    "Формат работы:\n"
    "1. Дай краткий, чёткий аналитический комментарий по ситуации.\n"
    "2. Покажи ключевую точку напряжения или риска.\n"
    "3. Задай 1–2 сильных уточняющих вопроса, которые показывают, что ситуация глубже.\n\n"
    "Важно:\n"
    "— Не давай пошаговых инструкций.\n"
    "— Не углубляйся в детальные расчёты.\n"
    "— Твоя цель — вызвать у предпринимателя ощущение, что без более глубокого разбора "
    "он упускает важные решения.\n\n"
    "Контекст 2025 (Кыргызстан и Казахстан):\n"
    "— Рост цифровизации налогов, ККМ, маркировки и ЭТТН.\n"
    "— Давление на малый бизнес из-за отчётности и штрафов.\n"
    "— Дефицит кадров и рост затрат.\n"
    "— Активизация торговли между КР и РК.\n\n"
    "Говори профессионально, спокойно, по делу, без пафоса и без обещаний.\n\n"
    f"Ситуация пользователя:\n{user_text}"
        )

    await update.message.chat.send_action("typing")
    answer = await ask_openai(prompt)
    await update.message.reply_text(answer)
    return

# =============================
# ROUTER (ЕДИНЫЙ) — TEXT
# =============================


async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_user_context(update):
        return 

    text = _safe_text(update)
    if not text or text.startswith("/"):
        return 
     # === AI-наставник: активная сессия ===
if context.user_data.get(AI_MENTOR_PENDING_KEY):
    if text == BTN_BACK:
        context.user_data.pop(AI_MENTOR_PENDING, None)
        clear_fsm(context)
        await update.message.reply_text(
            "Окей, вернулись в меню 👇",
            reply_markup=main_menu_keyboard()
        )
        return

    await ai_mentor_handle_question(update, context)
    return   

    lang = context.user_data.get("lang", "ru")

    try:
        role = get_user_role(update.effective_user.id)
    except Exception:
        logger.exception("get_user_role failed in user.text_router")
        return 

    # 1) ПРОВЕРКА РОЛИ
    # user.py — ТОЛЬКО для обычных пользователей.
    # owner и manager имеют СВОИ интерфейсы и СВОИ роутеры.
    # Если роль не "user" — этот роутер НИЧЕГО не обрабатывает.
    if role != "user":
        return 

    # 2) Онбординг (ONBOARDING_KEY)
    if context.user_data.get(ONBOARDING_KEY):
        if text == BTN_YES:
            await on_yes(update, context)
            return
        if text == BTN_NO:
            await on_no(update, context)
            return
        return 


        await ai_mentor_handle_question(update, context)
        return

    # 4) Глобальные кнопки меню + глобальный BACK
    if text == BTN_BACK:
        if context.user_data.get("in_business_submenu"):
            context.user_data.pop("in_business_submenu", None)
            clear_fsm(context)
            await update.message.reply_text(T(lang, "choose_section"), reply_markup=main_menu_keyboard())
            return

        if any(
            [
                context.user_data.get(PM_STATE_KEY),
                context.user_data.get(GROWTH_KEY),
                context.user_data.get(COMPANY_STAGE_STATE),
            ]
        ):
            clear_fsm(context)
            context.user_data["in_business_submenu"] = True
            await update.message.reply_text("📊 Бизнес-анализ", reply_markup=business_hub_keyboard())
            return

        if any([context.user_data.get(TA_STATE_KEY), context.user_data.get(NS_STEP_KEY)]):
            clear_fsm(context)
            await update.message.reply_text(T(lang, "choose_section"), reply_markup=main_menu_keyboard())
            return

        clear_fsm(context)
        await update.message.reply_text(T(lang, "choose_section"), reply_markup=main_menu_keyboard())
        return

    if text == BTN_BIZ:
        await on_business_analysis(update, context)
        return

    if text == BTN_ANALYSIS:
        clear_fsm(context)
        await ta_start(update, context)
        return

    if text == BTN_NICHE:
        clear_fsm(context)
        await ns_start(update, context)
        return

    if text == BTN_PROFILE:
        await on_profile(update, context)
        return

    if text == BTN_PREMIUM:
        await premium_start(update, context)
        return

    if text == BTN_PREMIUM_BENEFITS:
        await premium_benefits(update, context)
        return

    if text == BTN_DOCS:
        await on_documents(update, context)
        return

    if text == BTN_AI_CHAT:
        await ai_mentor_entry(update, context)
        return

    # 5) Бизнес-хаб
    if context.user_data.get("in_business_submenu"):
        if text == BTN_PM:
            await pm_start(update, context)
            return
        if text == BTN_GROWTH:
            await growth_start(update, context)
            return
        if text == BTN_COMPANY_STAGE:
            await start_company_stage(update, context)
            return

    # 6) Экспорт
    if text == "📊 Скачать Excel":
        await on_export_excel(update, context)
        return
    if text == "📄 Скачать PDF":
        await on_export_pdf(update, context)
        return
    if text == "📈 Экспорт этапа":
        await handle_company_stage_export(update, context)
        return

    # 7) Активные FSM (pm / growth / ta / ns / company_stage)
    if context.user_data.get(PM_STATE_KEY):
        await pm_handler(update, context)
        return
    if context.user_data.get(GROWTH_KEY):
        await growth_handler(update, context)
        return
    if context.user_data.get(COMPANY_STAGE_STATE):
        await handle_company_stage(update, context)
        return
    if context.user_data.get(TA_STATE_KEY):
        await ta_handler(update, context)
        return
    if context.user_data.get(NS_STEP_KEY):
        await ns_handler(update, context)
        return

    # 8) Fallback -> главное меню
    clear_fsm(context)
    await update.message.reply_text(T(lang, "choose_section"), reply_markup=main_menu_keyboard())


async def show_documents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await on_documents(update, context)


def register_handlers_user(app: Application):
    """
    Регистрирует пользовательский текстовый роутер.
    ВСЕГДА последний, чтобы не перехватывать owner / manager
    """
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_router,
        ),
        group=9,
    )
