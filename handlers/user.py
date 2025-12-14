



from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters
from typing import Optional

# Константы
INSIGHTS_KEY = "insights"
PM_STATE_KEY = "pm_state"
PM_STATE_REVENUE = "revenue"
PM_STATE_EXPENSES = "expenses"
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

# Кнопки (должны быть определены где-то)
BTN_YES = "Да"
BTN_NO = "Нет"
BTN_BIZ = "📊 Бизнес-анализ"
BTN_ANALYSIS = "📦 Анализ товара"
BTN_NICHE = "🔎 Подбор ниши"
BTN_PROFILE = "👤 Профиль"
BTN_PREMIUM = "❤️ Premium"
BTN_PM = "💰 Прибыль и деньги"
BTN_GROWTH = "🚀 Рост и продажи"
BTN_BACK = "↩️ Назад"
BTN_PREMIUM_BENEFITS = "Что получу?"
GC_INST = "Instagram"
GC_TG = "Telegram"
GC_KASPI = "Kaspi"
GC_WB = "Wildberries"
GC_OZON = "Ozon"
GC_OFFLINE = "Оффлайн"

def clear_fsm(context):
    """Очистка состояний FSM"""
    keys_to_clear = [
        PM_STATE_KEY, GROWTH_KEY, TA_STATE_KEY, 
        NS_STEP_KEY, PREMIUM_KEY, "revenue", 
        "product_stage", "product_purpose", "seasonality",
        "competition", "price_reaction", "resource",
        "goal", "format", "demand"
    ]
    for key in keys_to_clear:
        context.user_data.pop(key, None)

def _ensure_insights(context):
    """Инициализация insights в user_data"""
    if INSIGHTS_KEY not in context.user_data:
        context.user_data[INSIGHTS_KEY] = {}

async def ask_openai(prompt):
    """Заглушка для запроса к OpenAI"""
    # Здесь должна быть реальная реализация
    return "Аналитический разбор будет здесь..."

def insights_bridge_text(context):
    """
    Короткая связка между сценариями. Без магии, без "я всё помню".
    """
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

# Дальше идет остальной код...

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
# START
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
# 📊 БИЗНЕС-АНАЛИЗ (хаб)
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
# 💰 ПРИБЫЛЬ И ДЕНЬГИ (FSM)
# =============================

async def pm_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data[PM_STATE_KEY] = PM_STATE_REVENUE
    bridge = insights_bridge_text(context)
    
    await update.message.reply_text(
        bridge + "💰 Прибыль и деньги\n\n"
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
    text_raw = (update.message.text or "")
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
        if revenue == 0:
            risk_level = "высокий"
        else:
            if margin < 0:
                risk_level = "высокий"
            elif margin < 10:
                risk_level = "средний"
            else:
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
# 🚀 РОСТ И ПРОДАЖИ (FSM)
# =============================

async def growth_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data[GROWTH_KEY] = True
    bridge = insights_bridge_text(context)
    
    await update.message.reply_text(
        bridge + "🚀 Рост и продажи\n\n"
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
# 📦 АНАЛИТИКА ТОВАРА — FSM v1 (полный)
# =============================

async def ta_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data[TA_STATE_KEY] = TA_STAGE
    bridge = insights_bridge_text(context)
    
    await update.message.reply_text(
        bridge + "📦 Аналитика товара\n\n"
        "Этот сценарий не даёт ответов «стоит или нет».\n"
        "Он помогает спокойно посмотреть на ограничения\n"
        "и снизить риск самообмана.\n\n"
        "На какой стадии ты сейчас?",
        reply_markup=step_keyboard(
            ["Рассматриваю конкретный товар", "Есть идея, без деталей", "Просто изучаю рынок"]
        ),
    )

async def ta_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get(TA_STATE_KEY)
    ans = update.message.text or ""
    
    if state == TA_STAGE:
        context.user_data["product_stage"] = ans
        context.user_data[TA_STATE_KEY] = TA_PURPOSE
        await update.message.reply_text(
            "Разберёмся, почему люди вообще его покупают.\n\n"
            "Зачем этот товар покупают чаще всего?",
            reply_markup=step_keyboard(
                ["Решает конкретную проблему", "Удобство / улучшение", "Желание / эмоция", "Не до конца понятно"]
            ),
        )
        return
    
    if state == TA_PURPOSE:
        context.user_data["product_purpose"] = ans
        context.user_data[TA_STATE_KEY] = TA_SEASON
        await update.message.reply_text(
            "Теперь посмотрим, как спрос на него распределяется во времени.\n\n"
            "Как выглядит спрос во времени?",
            reply_markup=step_keyboard(["Ровный", "Волнами", "Сезонный", "Ситуативный"]),
        )
        return
    
    if state == TA_SEASON:
        context.user_data["seasonality"] = ans
        context.user_data[TA_STATE_KEY] = TA_COMP
        await update.message.reply_text(
            "Посмотрим, насколько много внимания за него уже борются.\n\n"
            "Как ощущается конкуренция вокруг этого товара?",
            reply_markup=step_keyboard(["Тихо", "Заметно", "Перегрето"]),
        )
        return
    
    if state == TA_COMP:
        context.user_data["competition"] = ans
        context.user_data[TA_STATE_KEY] = TA_PRICE
        await update.message.reply_text(
            "Оценим чувствительность к цене.\n\n"
            "Что произойдёт, если цена станет выше?",
            reply_markup=step_keyboard(["Купят", "Сравнят", "Уйдут"]),
        )
        return
    
    if state == TA_PRICE:
        context.user_data["price_reaction"] = ans
        context.user_data[TA_STATE_KEY] = TA_RESOURCE
        await update.message.reply_text(
            "И напоследок — сверим идею с ресурсом.\n\n"
            "Что у тебя сейчас есть для старта?",
            reply_markup=step_keyboard(["Деньги", "Время", "Экспертиза", "Минимальный ресурс"]),
        )
        return
    
    if state == TA_RESOURCE:
        context.user_data["resource"] = ans
        await send_ta_result(update, context)

async def send_ta_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data
    stage = data.get("product_stage", "")
    purpose = data.get("product_purpose", "")
    season = data.get("seasonality", "")
    comp = data.get("competition", "")
    price = data.get("price_reaction", "")
    resource = data.get("resource", "")
    
    demand_type = "непонятно"
    if purpose == "Решает конкретную проблему":
        demand_type = "проблема"
    elif purpose == "Удобство / улучшение":
        demand_type = "удобство"
    elif purpose == "Желание / эмоция":
        demand_type = "желание"
    
    seasonality = "стабильно"
    if season in ("Сезонный", "Ситуативный"):
        seasonality = "сезонно"
    elif season == "Волнами":
        seasonality = "волнами"
    
    competition = "средняя"
    if comp == "Тихо":
        competition = "низкая"
    elif comp == "Перегрето":
        competition = "высокая"
    
    resource_level = "ограниченно"
    if resource in ("Деньги", "Время", "Экспертиза"):
        resource_level = "достаточно"
    if resource == "Минимальный ресурс":
        resource_level = "минимально"
    
    verdict = "Осторожно"
    risk_level = "средний"
    
    if purpose == "Решает конкретную проблему" and resource != "Минимальный ресурс":
        verdict = "Гипотеза допустима для проверки, но не является рекомендацией"
        risk_level = "средний"
    
    if purpose in ("Желание / эмоция", "Не до конца понятно") and resource == "Минимальный ресурс":
        verdict = "Высокий риск"
        risk_level = "высокий"
    
    if competition == "низкая" and seasonality == "стабильно" and resource_level == "достаточно":
        risk_level = "низкий"
    
    save_insights(
        context,
        last_scenario="📦 Товар",
        last_verdict=verdict if verdict != "Осторожно" else "Осторожно",
        risk_level=risk_level,
        demand_type=demand_type,
        seasonality=seasonality,
        competition=competition,
        resource=resource_level,
    )
    clear_fsm(context)
    
    base_text = (
        "Мы зафиксировали текущее состояние товара.\n"
        "Вердикт — это ориентир, а не решение.\n"
        "Он показывает, где стоит двигаться аккуратно.\n\n"
        f"Вердикт: {verdict}\n\n"
        "Даже аккуратный анализ не снимает риск.\n"
        "Окончательное решение всегда остаётся за тобой.\n"
    )
    
    ai_prompt = (
        "Дай короткий аналитический разбор по карточке товара/идеи.\n"
        "Запрещено: советы, обещания, прогнозы, директивы.\n"
        "Нужно: 1) наблюдения 2) риски 3) варианты проверки.\n"
        "В конце: это ориентир, а не рекомендация; решение за пользователем.\n\n"
        f"Стадия={stage}\n"
        f"Причина покупки={purpose}\n"
        f"Спрос по времени={season}\n"
        f"Конкуренция={comp}\n"
        f"Реакция на рост цены={price}\n"
        f"Ресурс={resource}\n"
        f"Ориентир-вердикт={verdict}\n"
    )
    
    ai_text = await ask_openai(ai_prompt)
    
    await update.message.reply_text(
        base_text + "\nКороткий разбор:\n" + ai_text,
        reply_markup=main_menu_keyboard(),
    )

# =============================
# 🔎 ПОДБОР НИШИ — FSM v1 (полный)
# =============================

NS_GOAL_START = "Запуск с нуля"
NS_GOAL_SWITCH = "Поиск нового направления"
NS_GOAL_RESEARCH = "Исследую рынок"

NS_FORMAT_GOODS = "Товары"
NS_FORMAT_SERVICE = "Услуги"
NS_FORMAT_ONLINE = "Онлайн / цифровое"
NS_FORMAT_UNKNOWN = "Пока не знаю"

NS_DEMAND_PROBLEM = "Решение проблемы"
NS_DEMAND_REGULAR = "Регулярная потребность"
NS_DEMAND_EMOTION = "Интерес / желание"
NS_DEMAND_UNKNOWN = "Не понимаю"

NS_SEASON_STABLE = "Нужна стабильность"
NS_SEASON_OK = "Готов к колебаниям"
NS_SEASON_UNKNOWN = "Не задумывался"

NS_COMPETITION_HARD = "Готов к плотному рынку"
NS_COMPETITION_SOFT = "Хочу менее занятые ниши"
NS_COMPETITION_UNKNOWN = "Не знаю, как оценивать"

NS_RESOURCE_MONEY = "Деньги"
NS_RESOURCE_TIME = "Время"
NS_RESOURCE_EXPERT = "Экспертиза"
NS_RESOURCE_MIN = "Минимальный ресурс"

async def ns_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data[NS_STEP_KEY] = 1
    bridge = insights_bridge_text(context)
    
    await update.message.reply_text(
        bridge + "🔎 Подбор ниши\n\n"
        "Этот сценарий помогает трезво посмотреть на направление,\n"
        "а не найти «правильную нишу».\n"
        "Здесь нет лучших ниш — есть только ниши\n"
        "с разным уровнем неопределённости.\n\n"
        "Зачем ты сейчас смотришь ниши?",
        reply_markup=step_keyboard([NS_GOAL_START, NS_GOAL_SWITCH, NS_GOAL_RESEARCH]),
    )

async def ns_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get(NS_STEP_KEY)
    ans = update.message.text or ""
    
    if step == 1:
        context.user_data["goal"] = ans
        context.user_data[NS_STEP_KEY] = 2
        await update.message.reply_text(
            "Какой формат тебе ближе?",
            reply_markup=step_keyboard([NS_FORMAT_GOODS, NS_FORMAT_SERVICE, NS_FORMAT_ONLINE, NS_FORMAT_UNKNOWN]),
        )
        return
    
    if step == 2:
        context.user_data["format"] = ans
        context.user_data[NS_STEP_KEY] = 3
        await update.message.reply_text(
            "На чём должен держаться спрос?",
            reply_markup=step_keyboard([NS_DEMAND_PROBLEM, NS_DEMAND_REGULAR, NS_DEMAND_EMOTION, NS_DEMAND_UNKNOWN]),
        )
        return
    
    if step == 3:
        context.user_data["demand"] = ans
        context.user_data[NS_STEP_KEY] = 4
        await update.message.reply_text(
            "Как ты относишься к сезонности?",
            reply_markup=step_keyboard([NS_SEASON_STABLE, NS_SEASON_OK, NS_SEASON_UNKNOWN]),
        )
        return
    
    if step == 4:
        context.user_data["seasonality"] = ans
        context.user_data[NS_STEP_KEY] = 5
        await update.message.reply_text(
            "Как ты смотришь на конкуренцию?",
            reply_markup=step_keyboard([NS_COMPETITION_HARD, NS_COMPETITION_SOFT, NS_COMPETITION_UNKNOWN]),
        )
        return
    
    if step == 5:
        context.user_data["competition"] = ans
        context.user_data[NS_STEP_KEY] = 6
        await update.message.reply_text(
            "Что у тебя есть на старт?",
            reply_markup=step_keyboard([NS_RESOURCE_MONEY, NS_RESOURCE_TIME, NS_RESOURCE_EXPERT, NS_RESOURCE_MIN]),
        )
        return
    
    if step == 6:
        context.user_data["resource"] = ans
        
        goal = context.user_data.get("goal", "")
        fmt = context.user_data.get("format", "")
        demand = context.user_data.get("demand", "")
        season = context.user_data.get("seasonality", "")
        comp = context.user_data.get("competition", "")
        res = context.user_data.get("resource", "")
        
        verdict = "Осторожно"
        risk_level = "средний"
        
        if demand == NS_DEMAND_PROBLEM and res != NS_RESOURCE_MIN:
            verdict = "Можно смотреть"
            risk_level = "средний"
        
        if demand == NS_DEMAND_EMOTION and res == NS_RESOURCE_MIN:
            verdict = "Высокий риск"
            risk_level = "высокий"
        
        demand_type = "непонятно"
        if demand == NS_DEMAND_PROBLEM:
            demand_type = "проблема"
        elif demand == NS_DEMAND_REGULAR:
            demand_type = "регулярность"
        elif demand == NS_DEMAND_EMOTION:
            demand_type = "желание"
        
        seasonality = "стабильно"
        if season == NS_SEASON_OK:
            seasonality = "сезонно"
        elif season == NS_SEASON_UNKNOWN:
            seasonality = "неясно"
        
        competition = "средняя"
        if comp == NS_COMPETITION_SOFT:
            competition = "низкая"
        elif comp == NS_COMPETITION_HARD:
            competition = "высокая"
        elif comp == NS_COMPETITION_UNKNOWN:
            competition = "неясно"
        
        resource_level = "ограниченно"
        if res in (NS_RESOURCE_MONEY, NS_RESOURCE_TIME, NS_RESOURCE_EXPERT):
            resource_level = "достаточно"
        if res == NS_RESOURCE_MIN:
            resource_level = "минимально"
        
        save_insights(
            context,
            last_scenario="🔎 Ниша",
            last_verdict=verdict,
            risk_level=risk_level,
            demand_type=demand_type,
            seasonality=seasonality,
            competition=competition,
            resource=resource_level,
        )
        clear_fsm(context)
        
        base_text = (
            "Этот результат не подбирает нишу за тебя.\n"
            "Он показывает рамки и ограничения,\n"
            "с которыми придётся работать.\n\n"
            f"Вердикт: {verdict}\n\n"
            "Вердикт — ориентир, а не рекомендация.\n"
            "Решение и ответственность остаются у тебя.\n"
        )
        
        ai_prompt = (
            "Дай короткий аналитический разбор по выбору направления (ниша).\n"
            "Запрещено: советы, обещания, прогнозы, директивы.\n"
            "Нужно: 1) наблюдения 2) риски 3) варианты проверки.\n"
            "В конце: это ориентир, а не рекомендация; решение за пользователем.\n\n"
            f"Зачем={goal}\n"
            f"Формат={fmt}\n"
            f"Спрос={demand}\n"
            f"Сезонность={season}\n"
            f"Конкуренция={comp}\n"
            f"Ресурс={res}\n"
            f"Ориентир-вердикт={verdict}\n"
        )
        
        ai_text = await ask_openai(ai_prompt)
        
        await update.message.reply_text(
            base_text + "\nКороткий разбор:\n" + ai_text,
            reply_markup=main_menu_keyboard(),
        )

# =============================
# ❤️ PREMIUM (коротко + цены + кнопка "что получу")
# =============================

async def premium_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data[PREMIUM_KEY] = True
    
    await update.message.reply_text(
        "❤️ Premium\n\n"
        "Быстро и по делу: цены + подключение.\n"
        "Без воды, без обещаний.\n\n"
        "💳 Стоимость:\n"
        "1 месяц — 499 сом / 2 499 ₸ / 449 ₽\n"
        "6 месяцев — 2 699 сом / 13 499 ₸ / 2 399 ₽\n"
        "12 месяцев — 4 999 сом / 24 999 ₸ / 4 499 ₽\n\n"
        "📩 Подключение через менеджера:\n"
        "@Artbazar_marketing",
        reply_markup=premium_keyboard(),
    )

async def premium_benefits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Что ты получишь в Premium\n\n"
        "1) Глубже разбор рисков\n"
        "— где идея ломается чаще всего\n\n"
        "2) Связка сценариев\n"
        "— ниша → товар → деньги → рост\n\n"
        "3) Чётче проверки\n"
        "— что проверить первым, чтобы не сжечь ресурс\n\n"
        "Это не гарантии и не советы.\n"
        "Это способ думать системнее.\n\n"
        "Решение остаётся за тобой.",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(BTN_BACK)]],
            resize_keyboard=True
        ),
    )


# =============================
# ROUTER
# =============================

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    
    # Premium — второе окно
    if text == BTN_PREMIUM_BENEFITS:
        await premium_benefits(update, context)
        return
    
    # глобальный Back (работает везде)
    if text == BTN_BACK:
        # если пользователь в бизнес-хаб сценариях — вернём в хаб
        if context.user_data.get(PM_STATE_KEY) or context.user_data.get(GROWTH_KEY):
            clear_fsm(context)
            await update.message.reply_text(
                "📊 Бизнес-анализ",
                reply_markup=business_hub_keyboard()
            )
            return
        clear_fsm(context)
        await update.message.reply_text(
            "Главное меню",
            reply_markup=main_menu_keyboard()
        )
        return
    
    # FSM приоритеты (если уже внутри)
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
    
    if context.user_data.get(PREMIUM_KEY):
        return

# =============================
# REGISTER
# =============================

def register_handlers_user(app):
    # стартовые
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_YES}$"), on_yes))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NO}$"), on_no))
    
    # меню/хабы
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_BIZ}$"), on_business_analysis))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PROFILE}$"), on_profile))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PREMIUM}$"), premium_start))
    
    # premium benefits (дублируем явным хендлером, чтобы не зависеть от router)
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PREMIUM_BENEFITS}$"), premium_benefits))
    
    # бизнес-хаб сценарии
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PM}$"), pm_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_GROWTH}$"), growth_start))
    
    # product/niche
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_ANALYSIS}$"), ta_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NICHE}$"), ns_start))
    
    # общий роутер текста
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))