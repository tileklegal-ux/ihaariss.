# -*- coding: utf-8 -*-

import logging
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters,
    Application,
)

from handlers.user_keyboards import (
    BTN_AI_CHAT,
    BTN_EXIT_CHAT,
    ai_chat_keyboard,
    main_menu_keyboard,
    business_hub_keyboard,
    growth_channels_keyboard,
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
)

from handlers.user_texts import t

from handlers.user_helpers import (
    clear_fsm,
    save_insights,
    insights_bridge_text,
)

# ✅ ЕДИНСТВЕННЫЙ "владелец" личного кабинета и экспорта — handlers/profile.py
from handlers.profile import on_profile, on_export_excel, on_export_pdf

# ✅ ДОБАВЛЕНО: юридические документы
from handlers.documents import on_documents

from services.openai_client import ask_openai
from database.db import is_user_premium
# ✅ ДОБАВЛЕНО РАНЕЕ (и теперь ИСПОЛЬЗУЕМ): роль пользователя
from database.db import get_user_role

logger = logging.getLogger(__name__)

# =============================
# FSM KEYS
# =============================

PM_STATE_KEY = "pm_state"
PM_STEP = "pm_step"
PM_REVENUE = "pm_revenue"
PM_EXPENSES = "pm_expenses"

GROWTH_KEY = "growth_state"
GROWTH_STEP = "growth_step"
GROWTH_CHANNEL = "growth_channel"

TA_STATE_KEY = "ta_state"
TA_STEP = "ta_step"
TA_STAGE = "ta_stage"
TA_REASON = "ta_reason"
TA_SEASON = "ta_season"
TA_COMP = "ta_comp"
TA_PRICE = "ta_price"
TA_RESOURCE = "ta_resource"

NS_STEP_KEY = "ns_step"

# премиум-флаг, который читает profile.py
PREMIUM_KEY = "is_premium"
AI_CHAT_MODE_KEY = "ai_chat_mode"  # Используем для изоляции режима

# onboarding-flag для фикса первого шага
ONBOARDING_KEY = "onboarding"

# =============================
# START / ONBOARDING
# =============================

async def cmd_start_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data.pop(AI_CHAT_MODE_KEY, None)  # Очищаем режим при старте

    if "lang" not in context.user_data:
        context.user_data["lang"] = "ru"

    # фиксируем, что пользователь в онбординге
    context.user_data[ONBOARDING_KEY] = True

    user = update.effective_user
    name = user.first_name or user.username or "друг"
    lang = context.user_data["lang"]

    # Ваш оригинальный текст с дисклеймером
    text = (
        f"Привет, {name}! 👋\n\n"
        "Я — AI-ассистент для анализа ниши и товаров.\n"
        "Помогаю находить точки роста и быстрее принимать решения.\n\n"
        "Важно: я не заменяю эксперта и не даю гарантированных результатов —\n"
        "ты сам принимаешь финальные решения.\n\n"
        "Продолжим?"
    )

    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(BTN_YES), KeyboardButton(BTN_NO)]],
            resize_keyboard=True,
        ),
    )


async def on_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop(ONBOARDING_KEY, None)
    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(t(lang, "choose_section"), reply_markup=main_menu_keyboard())


async def on_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop(ONBOARDING_KEY, None)
    await update.message.reply_text("Хорошо. Я рядом.", reply_markup=main_menu_keyboard())


# =============================
# 📊 БИЗНЕС-АНАЛИЗ (ХАБ)
# =============================

async def on_business_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(
        t(lang, "business_hub_intro"),
        reply_markup=business_hub_keyboard(),
    )


# =============================
# 💰 ПРИБЫЛЬ И ДЕНЬГИ (FSM)
# =============================

async def pm_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data[PM_STATE_KEY] = True
    context.user_data[PM_STEP] = 1

    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(
        t(lang, "pm_intro"),
        reply_markup=step_keyboard(),
    )


async def pm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    lang = context.user_data.get("lang", "ru")
    step = context.user_data.get(PM_STEP, 1)

    if text == BTN_BACK:
        clear_fsm(context)
        await update.message.reply_text("📊 Бизнес-анализ", reply_markup=business_hub_keyboard())
        return

    if step == 1:
        # Выручка
        try:
            revenue = float(text.replace(",", "."))
        except Exception:
            await update.message.reply_text(t(lang, "pm_revenue_err"), reply_markup=step_keyboard())
            return

        context.user_data[PM_REVENUE] = revenue
        context.user_data[PM_STEP] = 2
        await update.message.reply_text(t(lang, "pm_expenses_ask"), reply_markup=step_keyboard())
        return

    if step == 2:
        # Расходы
        try:
            expenses = float(text.replace(",", "."))
        except Exception:
            await update.message.reply_text(t(lang, "pm_expenses_err"), reply_markup=step_keyboard())
            return

        context.user_data[PM_EXPENSES] = expenses
        revenue = float(context.user_data.get(PM_REVENUE, 0))
        profit = revenue - expenses
        margin = (profit / revenue * 100) if revenue else 0.0

        # Сохраним инсайт
        insights = (
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
            "Запрещено: советы, обещания, прогнозы, директивы.\n"
            "Нужно: 1) наблюдения 2) риски 3) варианты проверки.\n"
            "В конце: это ориентир, а не рекомендация; решение за пользователем.\n\n"
            f"Данные:\nВыручка={revenue}\nРасходы={expenses}\nПрибыль={profit}\nМаржа={margin:.1f}%\n"
        )

        await update.message.reply_text(insights, reply_markup=business_hub_keyboard())

        try:
            await update.message.chat.send_action("typing")
            ai_text = await ask_openai(ai_prompt)
            await update.message.reply_text(ai_text, reply_markup=business_hub_keyboard())
        except Exception:
            await update.message.reply_text("⚠️ Не удалось получить AI-комментарий.", reply_markup=business_hub_keyboard())

        save_insights(context, insights)

        clear_fsm(context)
        await update.message.reply_text("📊 Бизнес-анализ", reply_markup=business_hub_keyboard())
        return


# =============================
# 🚀 РОСТ И ПРОДАЖИ (FSM)
# =============================

async def growth_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data[GROWTH_KEY] = True
    context.user_data[GROWTH_STEP] = 1

    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(
        t(lang, "growth_intro"),
        reply_markup=growth_channels_keyboard(),
    )


async def growth_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == BTN_BACK:
        clear_fsm(context)
        await update.message.reply_text("📊 Бизнес-анализ", reply_markup=business_hub_keyboard())
        return

    # фиксируем канал
    context.user_data[GROWTH_CHANNEL] = text

    insights = (
        "Текущий канал привлечения зафиксирован.\n"
        "Здесь нет оценки эффективности — это просто снимок.\n\n"
        f"Канал: {text}\n"
    )

    ai_prompt = (
        "Сделай короткую аналитическую рефлексию по выбранному каналу привлечения.\n"
        "Запрещено: советы, обещания, прогнозы, директивы.\n"
        "Нужно: 1) наблюдения 2) риски 3) варианты проверки.\n"
        "В конце: это ориентир, а не рекомендация; решение за пользователем.\n\n"
        f"Канал: {text}\n"
    )

    await update.message.reply_text(insights, reply_markup=business_hub_keyboard())

    try:
        await update.message.chat.send_action("typing")
        ai_text = await ask_openai(ai_prompt)
        await update.message.reply_text(ai_text, reply_markup=business_hub_keyboard())
    except Exception:
        await update.message.reply_text("⚠️ Не удалось получить AI-комментарий.", reply_markup=business_hub_keyboard())

    save_insights(context, insights)

    clear_fsm(context)
    await update.message.reply_text("📊 Бизнес-анализ", reply_markup=business_hub_keyboard())


# =============================
# 📦 АНАЛИТИКА ТОВАРА (FSM)
# =============================

async def ta_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data[TA_STATE_KEY] = True
    context.user_data[TA_STEP] = 1

    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(t(lang, "ta_intro"), reply_markup=step_keyboard())


async def ta_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "ru")
    text = (update.message.text or "").strip()
    step = context.user_data.get(TA_STEP, 1)

    if text == BTN_BACK:
        clear_fsm(context)
        await update.message.reply_text("📊 Бизнес-анализ", reply_markup=business_hub_keyboard())
        return

    if step == 1:
        context.user_data[TA_STAGE] = text
        context.user_data[TA_STEP] = 2
        await update.message.reply_text(t(lang, "ta_reason_ask"), reply_markup=step_keyboard())
        return

    if step == 2:
        context.user_data[TA_REASON] = text
        context.user_data[TA_STEP] = 3
        await update.message.reply_text(t(lang, "ta_season_ask"), reply_markup=step_keyboard())
        return

    if step == 3:
        context.user_data[TA_SEASON] = text
        context.user_data[TA_STEP] = 4
        await update.message.reply_text(t(lang, "ta_comp_ask"), reply_markup=step_keyboard())
        return

    if step == 4:
        context.user_data[TA_COMP] = text
        context.user_data[TA_STEP] = 5
        await update.message.reply_text(t(lang, "ta_price_ask"), reply_markup=step_keyboard())
        return

    if step == 5:
        context.user_data[TA_PRICE] = text
        context.user_data[TA_STEP] = 6
        await update.message.reply_text(t(lang, "ta_resource_ask"), reply_markup=step_keyboard())
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
            await update.message.reply_text("⚠️ Не удалось получить AI-комментарий.", reply_markup=business_hub_keyboard())

        save_insights(context, insights)

        clear_fsm(context)
        await update.message.reply_text("📊 Бизнес-анализ", reply_markup=business_hub_keyboard())


# =============================
# 🔎 ПОДБОР НИШИ (FSM)
# =============================

async def ns_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data[NS_STEP_KEY] = 1

    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(t(lang, "ns_intro"), reply_markup=step_keyboard())


async def ns_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "ru")
    text = (update.message.text or "").strip()
    step = context.user_data.get(NS_STEP_KEY, 1)

    if text == BTN_BACK:
        clear_fsm(context)
        await update.message.reply_text("📊 Бизнес-анализ", reply_markup=business_hub_keyboard())
        return

    if step == 1:
        context.user_data["ns_goal"] = text
        context.user_data[NS_STEP_KEY] = 2
        await update.message.reply_text(t(lang, "ns_format_ask"), reply_markup=step_keyboard())
        return

    if step == 2:
        context.user_data["ns_format"] = text
        context.user_data[NS_STEP_KEY] = 3
        await update.message.reply_text(t(lang, "ns_demand_ask"), reply_markup=step_keyboard())
        return

    if step == 3:
        context.user_data["ns_demand"] = text
        context.user_data[NS_STEP_KEY] = 4
        await update.message.reply_text(t(lang, "ns_season_ask"), reply_markup=step_keyboard())
        return

    if step == 4:
        context.user_data["ns_season"] = text
        context.user_data[NS_STEP_KEY] = 5
        await update.message.reply_text(t(lang, "ns_competition_ask"), reply_markup=step_keyboard())
        return

    if step == 5:
        context.user_data["ns_comp"] = text
        context.user_data[NS_STEP_KEY] = 6
        await update.message.reply_text(t(lang, "ns_resources_ask"), reply_markup=step_keyboard())
        return

    if step == 6:
        context.user_data["ns_res"] = text

        goal = context.user_data.get("ns_goal", "")
        fmt = context.user_data.get("ns_format", "")
        demand = context.user_data.get("ns_demand", "")
        season = context.user_data.get("ns_season", "")
        comp = context.user_data.get("ns_comp", "")
        res = context.user_data.get("ns_res", "")

        insights = (
            "Ниша зафиксирована как аналитический ориентир.\n\n"
            f"Цель: {goal}\n"
            f"Формат: {fmt}\n"
            f"Тип спроса: {demand}\n"
            f"Сезонность: {season}\n"
            f"Конкуренция: {comp}\n"
            f"Ресурсы: {res}\n"
        )

        ai_prompt = (
            "Сделай краткий аналитический срез по нише.\n"
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
            await update.message.reply_text("⚠️ Не удалось получить AI-комментарий.", reply_markup=business_hub_keyboard())

        save_insights(context, insights)

        clear_fsm(context)
        await update.message.reply_text("📊 Бизнес-анализ", reply_markup=business_hub_keyboard())


# =============================
# ⭐ PREMIUM
# =============================

async def premium_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(
        t(lang, "premium_intro"),
        reply_markup=premium_keyboard(),
    )


async def premium_benefits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Что ты получишь в Premium\n\n"
        "1) Глубже разбор рисков\n"
        "2) История результатов\n"
        "3) Экспорт PDF / Excel\n\n"
        "Это ориентир, а не рекомендация.\n"
        "Решение остаётся за тобой.",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton(BTN_BACK)]], resize_keyboard=True),
    )


# =============================
# 💬 AI ЧАТ (Premium) — MODE
# =============================

async def ai_chat_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = (update.message.text or "").strip()

    if not user_text or user_text.startswith("/"):
        return

    if not is_user_premium(update.effective_user.id):
        return

    await update.message.chat.send_action("typing")

    try:
        ai_prompt = (
            "Ты — аналитическое зеркало мыслей предпринимателя. Запрещено: советы, прогнозы, обещания, директивы.\n"
            "Формат ответа строго: 1) Наблюдения 2) Риски 3) Варианты проверки.\n"
            "Последняя строка обязательно: это ориентир, а не рекомендация; решение за пользователем\n\n"
            f"Текст пользователя:\n{user_text}"
        )
        answer = await ask_openai(ai_prompt)
        await update.message.reply_text(
            answer,
            reply_markup=ai_chat_keyboard(),
        )
    except Exception:
        await update.message.reply_text("⚠️ Ошибка AI. Попробуй позже.")


# =============================
# ROUTER (ЕДИНЫЙ) — TEXT
# =============================

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text or ""
    text = user_text

    if user_text.startswith("/"):
        return

    try:
        role = get_user_role(update.effective_user.id)
    except Exception:
        logger.exception("get_user_role failed in user.text_router")
        return

    # РАННИЙ ВЫХОД для owner/manager
    if role != "user":
        return

    # 1) Режим AI-чата
    if context.user_data.get(AI_CHAT_MODE_KEY):
        if text in (BTN_BACK, BTN_EXIT_CHAT):
            context.user_data.pop(AI_CHAT_MODE_KEY, None)
            clear_fsm(context)
            lang = context.user_data.get("lang", "ru")
            await update.message.reply_text(t(lang, "choose_section"), reply_markup=main_menu_keyboard())
            return

        await ai_chat_text_handler(update, context)
        return

    # 2) Кнопка AI ЧАТ
    if text == BTN_AI_CHAT:
        await enter_ai_chat(update, context)
        return

    # 3) Онбординг (фиксируем первые кнопки)
    if context.user_data.get(ONBOARDING_KEY):
        if text == BTN_YES:
            await on_yes(update, context)
            return
        if text == BTN_NO:
            await on_no(update, context)
            return

    # 4) Документы
    if text in ("📄 Документы", "📄 Документы и условия"):
        await on_documents(update, context)
        return

    # 5) Преимущества
    if text == BTN_PREMIUM_BENEFITS:
        await premium_benefits(update, context)
        return

    # 6) Экспорт (уходит в profile.py, но мы ловим кнопки здесь)
    if text == "📊 Скачать Excel":
        await on_export_excel(update, context)
        return
    if text == "📄 Скачать PDF":
        await on_export_pdf(update, context)
        return

    # 7) Кнопка НАЗАД (глобальная) - ВАЖНО: обработка для non-premium AI-chat
    if text == BTN_BACK:
        # Специальная обработка для возврата после отказа в AI-чате
        if not is_user_premium(update.effective_user.id) and not any([
            context.user_data.get(PM_STATE_KEY),
            context.user_data.get(GROWTH_KEY),
            context.user_data.get(TA_STATE_KEY),
            context.user_data.get(NS_STEP_KEY),
            context.user_data.get(AI_CHAT_MODE_KEY)
        ]):
            # Если пользователь non-premium и не в FSM - возвращаем в меню
            clear_fsm(context)
            lang = context.user_data.get("lang", "ru")
            await update.message.reply_text(t(lang, "choose_section"), reply_markup=main_menu_keyboard())
            return

        # Обычная логика возврата из FSM
        if context.user_data.get(PM_STATE_KEY) or \
           context.user_data.get(GROWTH_KEY) or \
           context.user_data.get(TA_STATE_KEY) or \
           context.user_data.get(NS_STEP_KEY):
            # Если внутри FSM — выходим в ХАБ
            clear_fsm(context)
            await update.message.reply_text("📊 Бизнес-анализ", reply_markup=business_hub_keyboard())
            return

        # Иначе в главное меню
        clear_fsm(context)
        lang = context.user_data.get("lang", "ru")
        await update.message.reply_text(t(lang, "choose_section"), reply_markup=main_menu_keyboard())
        return

    # 8) Активные FSM
    if context.user_data.get(PM_STATE_KEY):
        await pm_handler(update, context)
        return
    if context.user_data.get(GROWTH_KEY):
        await growth_handler(update, context)
        return
    if context.user_data.get(TA_STATE_KEY):
        await ta_handler(update, context)
        return
    if context.user_data.get(NS_STEP_KEY):
        await ns_handler(update, context)
        return

    # 9) Кнопки переходов (Главное меню) - ТОЛЬКО ПЕРВЫЙ УРОВЕНЬ
    if text == BTN_BIZ:
        await on_business_analysis(update, context)
        return
    if text == BTN_AI_CHAT:
        await enter_ai_chat(update, context)
        return
    if text == BTN_PROFILE:
        await on_profile(update, context)
        return
    if text == BTN_PREMIUM:
        await premium_start(update, context)
        return
    if text == BTN_ANALYSIS or text == BTN_NICHE:
        # Эти кнопки должны быть удалены из main_menu_keyboard
        # Но на случай, если они остались - показываем бизнес-хаб
        await on_business_analysis(update, context)
        return

    # 10) Кнопки ПОДМЕНЮ "Бизнес-анализ"
    if text == BTN_PM:
        await pm_start(update, context)
        return
    if text == BTN_GROWTH:
        await growth_start(update, context)
        return
    if text == BTN_ANALYSIS:
        await ta_start(update, context)
        return
    if text == BTN_NICHE:
        await ns_start(update, context)
        return

    # Если ничего не подошло
    clear_fsm(context)
    lang = context.user_data.get("lang", "ru")
    await update.message.reply_text(t(lang, "choose_section"), reply_markup=main_menu_keyboard())


async def enter_ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)

    # Non-premium: короткое сообщение + кнопка "Назад", чтобы не застрять
    if not is_user_premium(update.effective_user.id):
        context.user_data.pop(AI_CHAT_MODE_KEY, None)
        await update.message.reply_text(
            "💬 AI-чат доступен только для Premium.\n\nНажми «Назад», чтобы вернуться в меню.",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton(BTN_BACK)]], resize_keyboard=True),
        )
        return

    # Premium: сразу в режим чата
    context.user_data[AI_CHAT_MODE_KEY] = True
    await update.message.reply_text(
        "💬 **AI Чат (Premium)**\n\n"
        "Ты в режиме чата. Пиши сообщение текстом.\n\n"
        "Для выхода нажми «❌ Выйти из AI-чата» или «Назад».",
        reply_markup=ai_chat_keyboard(),
        parse_mode="Markdown",
    )


async def show_documents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await on_documents(update, context)


def register_handlers_user(app: Application):
    """
    Регистрирует пользовательский текстовый роутер.
    """
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_router),
        group=4,
    )
