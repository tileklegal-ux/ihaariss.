# -*- coding: utf-8 -*-

import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters

from handlers.user_keyboards import (
    BTN_AI_CHAT,
    BTN_EXIT_CHAT,
    ai_chat_keyboard,
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
    BTN_COMPANY_STAGE
)

from handlers.user_texts import t as T
from handlers.user_helpers import clear_fsm, save_insights
from handlers.profile import on_profile, on_export_excel, on_export_pdf
from handlers.documents import on_documents
from handlers.company_stage import (
    start_company_stage,
    handle_company_stage,
    handle_company_stage_export,
    COMPANY_STAGE_STATE
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
AI_CHAT_MODE_KEY = "ai_chat_mode"

# =============================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =============================

def _safe_text(update: Update) -> str:
    return (update.message.text or "").strip() if update and update.message else ""

def _is_user_context(update: Update) -> bool:
    if not update or not update.effective_user:
        return False
    return True

# =============================
# START / ONBOARDING
# =============================

async def cmd_start_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data.pop(AI_CHAT_MODE_KEY, None)

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
    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(
        T(lang, "choose_section"),
        reply_markup=main_menu_keyboard(),
    )

async def on_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop(ONBOARDING_KEY, None)
    await update.message.reply_text(
        "Хорошо. Я рядом.",
        reply_markup=main_menu_keyboard(),
    )

# =============================
# 📊 БИЗНЕС-АНАЛИЗ (ХАБ) - ТОЛЬКО ПОДМЕНЮ
# =============================

async def on_business_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
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
        await update.message.reply_text(
            "📊 Бизнес-анализ",
            reply_markup=business_hub_keyboard()
        )
        return

    if step == 1:
        context.user_data["pm_type"] = text
        context.user_data[PM_STEP] = 2
        await update.message.reply_text(
            T(lang, "pm_step1"),
            reply_markup=pm_step_keyboard(2)
        )
        return

    if step == 2:
        context.user_data["pm_source"] = text
        context.user_data[PM_STEP] = 3
        await update.message.reply_text(
            T(lang, "pm_step2"),
            reply_markup=pm_step_keyboard(3)
        )
        return

    if step == 3:
        context.user_data["pm_fixed"] = text
        context.user_data[PM_STEP] = 4
        await update.message.reply_text(
            T(lang, "pm_step3"),
            reply_markup=pm_step_keyboard(4)
        )
        return

    if step == 4:
        context.user_data["pm_variable"] = text
        context.user_data[PM_STEP] = 5
        await update.message.reply_text(
            T(lang, "pm_step4"),
            reply_markup=pm_step_keyboard(5)
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

        await update.message.reply_text(
            insights,
            reply_markup=business_hub_keyboard()
        )

        try:
            await update.message.chat.send_action("typing")
            ai_text = await ask_openai(ai_prompt)
            await update.message.reply_text(
                ai_text,
                reply_markup=business_hub_keyboard()
            )
        except Exception:
            await update.message.reply_text(
                "⚠️ Не удалось получить AI-комментарий.",
                reply_markup=business_hub_keyboard(),
            )

        save_insights(context, insights)
        clear_fsm(context)
        await update.message.reply_text(
            "📊 Бизнес-анализ",
            reply_markup=business_hub_keyboard()
        )
        return

# =============================
# 🚀 РОСТ И ПРОДАЖИ (FSM) - ТОЛЬКО В ПОДМЕНЮ
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
        await update.message.reply_text(
            "📊 Бизнес-анализ",
            reply_markup=business_hub_keyboard()
        )
        return

    if step == 1:
        context.user_data["growth_channel"] = text
        context.user_data[GROWTH_STEP] = 2
        await update.message.reply_text(
            T(lang, "growth_step1"),
            reply_markup=growth_step_keyboard(2)
        )
        return

    if step == 2:
        context.user_data["growth_conversion"] = text
        context.user_data[GROWTH_STEP] = 3
        await update.message.reply_text(
            T(lang, "growth_step2"),
            reply_markup=growth_step_keyboard(3)
        )
        return

    if step == 3:
        context.user_data["growth_cost"] = text
        context.user_data[GROWTH_STEP] = 4
        await update.message.reply_text(
            T(lang, "growth_step3"),
            reply_markup=growth_step_keyboard(4)
        )
        return

    if step == 4:
        context.user_data["growth_retention"] = text
        context.user_data[GROWTH_STEP] = 5
        await update.message.reply_text(
            T(lang, "growth_step4"),
            reply_markup=growth_step_keyboard(5)
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

        await update.message.reply_text(
            insights,
            reply_markup=business_hub_keyboard()
        )

        try:
            await update.message.chat.send_action("typing")
            ai_text = await ask_openai(ai_prompt)
            await update.message.reply_text(
                ai_text,
                reply_markup=business_hub_keyboard()
            )
        except Exception:
            await update.message.reply_text(
                "⚠️ Не удалось получить AI-комментарий.",
                reply_markup=business_hub_keyboard(),
            )

        save_insights(context, insights)
        clear_fsm(context)
        await update.message.reply_text(
            "📊 Бизнес-анализ",
            reply_markup=business_hub_keyboard()
        )
        return

# =============================
# 📈 ЭТАП КОМПАНИИ (НОВАЯ ФИЧА)
# =============================

async def company_stage_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await start_company_stage(update, context)

# =============================
# 📦 АНАЛИТИКА ТОВАРА (FSM)
# =============================

async def ta_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data[TA_STATE_KEY] = True
    context.user_data[TA_STEP] = 1

    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(
        T(lang, "ta_intro"),
        reply_markup=step_keyboard()
    )

async def ta_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "ru")
    text = _safe_text(update)
    step = int(context.user_data.get(TA_STEP, 1))

    if text == BTN_BACK:
        clear_fsm(context)
        await update.message.reply_text(
            T(lang, "choose_section"),
            reply_markup=main_menu_keyboard()
        )
        return

    if step == 1:
        context.user_data[TA_STAGE] = text
        context.user_data[TA_STEP] = 2
        await update.message.reply_text(
            T(lang, "ta_reason_ask"),
            reply_markup=step_keyboard()
        )
        return

    if step == 2:
        context.user_data[TA_REASON] = text
        context.user_data[TA_STEP] = 3
        await update.message.reply_text(
            T(lang, "ta_season_ask"),
            reply_markup=step_keyboard()
        )
        return

    if step == 3:
        context.user_data[TA_SEASON] = text
        context.user_data[TA_STEP] = 4
        await update.message.reply_text(
            T(lang, "ta_comp_ask"),
            reply_markup=step_keyboard()
        )
        return

    if step == 4:
        context.user_data[TA_COMP] = text
        context.user_data[TA_STEP] = 5
        await update.message.reply_text(
            T(lang, "ta_price_ask"),
            reply_markup=step_keyboard()
        )
        return

    if step == 5:
        context.user_data[TA_PRICE] = text
        context.user_data[TA_STEP] = 6
        await update.message.reply_text(
            T(lang, "ta_resource_ask"),
            reply_markup=step_keyboard()
        )
        return

    if step == 6:
        context.user_data[TA_RESOURCE] = text

        insights = (
            "Аналитический срез товара зафиксирован.\n"
            "Это ориентир и структура мыслей.\n\n"
            f"Стадия: {context.user_data.get(TA_STAGE, '')}\n"
            f"Причина покупки: {context.user_data.get(TA_REASON, '')}\n"
            f"Сезонность: {context.user_data.get(TA_SEASON, '')}\n"
            f"Конкуренция: {context.user_data.get(TA_COMP, '')}\n"
            f"Чувствительность к цене: {context.user_data.get(TA_PRICE, '')}\n"
            f"Ресурсы: {context.user_data.get(TA_RESOURCE, '')}\n"
        )

        ai_prompt = (
            "Сделай короткий аналитический разбор товара.\n"
            "Запрещено: советы, обещания, прогнозы, директивы.\n"
            "Нужно: 1) наблюдения 2) риски 3) варианты проверки.\n"
            "В конце: это ориентир, а не рекомендация; решение за пользователем.\n\n"
            f"{insights}\n"
        )

        await update.message.reply_text(
            insights,
            reply_markup=main_menu_keyboard()
        )

        try:
            await update.message.chat.send_action("typing")
            ai_text = await ask_openai(ai_prompt)
            await update.message.reply_text(
                ai_text,
                reply_markup=main_menu_keyboard()
            )
        except Exception:
            await update.message.reply_text(
                "⚠️ Не удалось получить AI-комментарий.",
                reply_markup=main_menu_keyboard(),
            )

        save_insights(context, insights)
        clear_fsm(context)
        await update.message.reply_text(
            T(lang, "choose_section"),
            reply_markup=main_menu_keyboard()
        )
        return

# =============================
# 🔎 ПОДБОР НИШИ (FSM)
# =============================

async def ns_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data[NS_STEP_KEY] = 1

    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(
        T(lang, "ns_intro"),
        reply_markup=step_keyboard()
    )

async def ns_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "ru")
    text = _safe_text(update)
    step = int(context.user_data.get(NS_STEP_KEY, 1))

    if text == BTN_BACK:
        clear_fsm(context)
        await update.message.reply_text(
            T(lang, "choose_section"),
            reply_markup=main_menu_keyboard()
        )
        return

    if step == 1:
        context.user_data["ns_goal"] = text
        context.user_data[NS_STEP_KEY] = 2
        await update.message.reply_text(
            T(lang, "ns_format_ask"),
            reply_markup=step_keyboard()
        )
        return

    if step == 2:
        context.user_data["ns_format"] = text
        context.user_data[NS_STEP_KEY] = 3
        await update.message.reply_text(
            T(lang, "ns_demand_ask"),
            reply_markup=step_keyboard()
        )
        return

    if step == 3:
        context.user_data["ns_demand"] = text
        context.user_data[NS_STEP_KEY] = 4
        await update.message.reply_text(
            T(lang, "ns_season_ask"),
            reply_markup=step_keyboard()
        )
        return

    if step == 4:
        context.user_data["ns_season"] = text
        context.user_data[NS_STEP_KEY] = 5
        await update.message.reply_text(
            T(lang, "ns_competition_ask"),
            reply_markup=step_keyboard()
        )
        return

    if step == 5:
        context.user_data["ns_comp"] = text
        context.user_data[NS_STEP_KEY] = 6
        await update.message.reply_text(
            T(lang, "ns_resources_ask"),
            reply_markup=step_keyboard()
        )
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

        await update.message.reply_text(
            insights,
            reply_markup=main_menu_keyboard()
        )

        try:
            await update.message.chat.send_action("typing")
            ai_text = await ask_openai(ai_prompt)
            await update.message.reply_text(
                ai_text,
                reply_markup=main_menu_keyboard()
            )
        except Exception:
            await update.message.reply_text(
                "⚠️ Не удалось получить AI-комментарий.",
                reply_markup=main_menu_keyboard(),
            )

        save_insights(context, insights)
        clear_fsm(context)
        await update.message.reply_text(
            T(lang, "choose_section"),
            reply_markup=main_menu_keyboard()
        )
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

# ===============================
# 🧭 AI-НАСТАВНИК (режим чата)
# ===============================

async def ai_mentor_intro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "ru")
    user_id = update.effective_user.id

    if is_user_premium(user_id):
        intro_text = T(lang, "ai_mentor_premium")
    else:
        intro_text = T(lang, "ai_mentor_free")

    await update.message.reply_text(intro_text)
    context.user_data[AI_CHAT_MODE_KEY] = True

    await update.message.reply_text(
        "✍️ Опиши свою ситуацию или вопрос.",
        reply_markup=ai_chat_keyboard(),
    )

async def ai_mentor_exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop(AI_CHAT_MODE_KEY, None)
    await update.message.reply_text(
        T(context.user_data.get("lang", "ru"), "choose_section"),
        reply_markup=main_menu_keyboard(),
    )

async def ai_mentor_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = _safe_text(update)
    if not user_text or user_text.startswith("/"):
        return

    await update.message.chat.send_action("typing")

    user_id = update.effective_user.id
    premium = is_user_premium(user_id)

    if not premium:
        prompt = (
            "Ты — AI-наставник предпринимателя.\n"
            "Дай короткий ответ на ситуацию.\n"
            "Строго: 3 пункта (нумерованный список).\n"
            "Без прогнозов, без обещаний, без директив.\n"
            "Фокус: суть / риск / что проверить.\n"
            "В конце одной строкой мягкий upsell в Premium.\n\n"
            f"Запрос:\n{user_text}"
        )
    else:
        prompt = (
            "Ты — AI-наставник предпринимателя.\n"
            "Дай глубокий аналитический ответ.\n"
            "Структура строго:\n"
            "1) Суть\n"
            "2) Риски\n"
            "3) Что проверить\n"
            "Без прогнозов, без обещаний, без директив.\n\n"
            f"Запрос:\n{user_text}"
        )

    try:
        answer = await ask_openai(prompt)
        await update.message.reply_text(
            answer,
            reply_markup=ai_chat_keyboard()
        )
    except Exception:
        await update.message.reply_text(
            "⚠️ Сейчас не удалось получить ответ. Попробуй чуть позже.",
            reply_markup=ai_chat_keyboard(),
        )

# =============================
# ROUTER - ИСПРАВЛЕННЫЙ (УБРАН BTN_PM и BTN_GROWTH)
# =============================

async def user_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_user_context(update):
        return

    user_id = update.effective_user.id
    text = _safe_text(update)
    if not text:
        return

    # 1. ONBOARDING — ПЕРВЫМ
    if context.user_data.get(ONBOARDING_KEY):
        if text == BTN_YES:
            await on_yes(update, context)
            return
        if text == BTN_NO:
            await on_no(update, context)
            return
        return

    # 2. AI-CHAT
    if context.user_data.get(AI_CHAT_MODE_KEY):
        if text == BTN_EXIT_CHAT:
            await ai_mentor_exit(update, context)
            return
        await ai_mentor_text_handler(update, context)
        return

    # 3. РОЛЬ (менеджер / юзер)
    role = get_user_role(update.effective_user.id)
    if role == "manager":
        return

    # 4. МЕНЮ ЮЗЕРА - ИСПРАВЛЕНО: УБРАНЫ BTN_PM и BTN_GROWTH
    if text == BTN_BIZ:
        await on_business_analysis(update, context)
        return

    # 5. ПОДМЕНЮ БИЗНЕС-АНАЛИЗА (только здесь обрабатываются)
    if context.user_data.get("in_business_submenu"):
        if text == BTN_PM:
            await pm_start(update, context)
            return
        if text == BTN_GROWTH:
            await growth_start(update, context)
            return
        if text == BTN_COMPANY_STAGE:
            await company_stage_start(update, context)
            return
        if text == BTN_BACK:
            context.user_data.pop("in_business_submenu", None)
            await update.message.reply_text(
                T(context.user_data.get("lang", "ru"), "choose_section"),
                reply_markup=main_menu_keyboard(),
            )
            return

    # 6. FSM HANDLERS
    if context.user_data.get(PM_STATE_KEY):
        await pm_handler(update, context)
        return

    if context.user_data.get(GROWTH_KEY):
        await growth_handler(update, context)
        return

    if context.user_data.get(COMPANY_STAGE_STATE):
        await handle_company_stage(update, context)
        return

    if text == "📊 Скачать Excel":
        await on_export_excel(update, context)
        return

    if text == "📄 Скачать PDF":
        await on_export_pdf(update, context)
        return

    if text == "📈 Экспорт этапа":
        await handle_company_stage_export(update, context)
        return

    if context.user_data.get(TA_STATE_KEY):
        await ta_handler(update, context)
        return

    if context.user_data.get(NS_STEP_KEY):
        await ns_handler(update, context)
        return

    # 7. ОСНОВНЫЕ КНОПКИ
    if text == BTN_ANALYSIS:
        await ta_start(update, context)
        return

    if text == BTN_NICHE:
        await ns_start(update, context)
        return

    if text == BTN_PROFILE:
        clear_fsm(context)
        await on_profile(update, context)
        return

    if text == BTN_DOCS:
        clear_fsm(context)
        await on_documents(update, context)
        return

    if text == BTN_PREMIUM:
        clear_fsm(context)
        await premium_start(update, context)
        return

    if text == BTN_PREMIUM_BENEFITS:
        await premium_benefits(update, context)
        return

    if text == BTN_AI_CHAT:
        clear_fsm(context)
        await ai_mentor_intro(update, context)
        return

    # 8. По умолчанию возвращаем в меню
    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(
        T(lang, "choose_section"),
        reply_markup=main_menu_keyboard(),
    )

def register_handlers_user(app):
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, user_text_router),
        group=1,
    )
