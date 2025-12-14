from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters

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

# =============================
# КАНАЛЫ РОСТА
# =============================

GC_INST = "📸 Instagram"
GC_TG = "✈️ Telegram"
GC_KASPI = "💳 Kaspi"
GC_WB = "📦 Wildberries"
GC_OZON = "📦 Ozon"
GC_OFFLINE = "🏬 Офлайн"

# =============================
# FSM KEYS
# =============================

# 💰 Прибыль и деньги
PM_STATE_KEY = "pm_state"
PM_STATE_REVENUE = "revenue"
PM_STATE_EXPENSES = "expenses"

# 🚀 Рост и продажи
GROWTH_KEY = "growth"

# 📦 Аналитика товара
TA_STATE_KEY = "ta_state"
TA_STAGE = "ta_stage"
TA_PURPOSE = "ta_purpose"
TA_SEASON = "ta_season"
TA_COMP = "ta_comp"
TA_PRICE = "ta_price"
TA_RESOURCE = "ta_resource"

# 🔎 Подбор ниши
NS_STEP_KEY = "ns_step"

# ❤️ Premium
PREMIUM_KEY = "premium_screen"

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

# =============================
# START
# =============================

async def cmd_start_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
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
        reply_markup=main_menu_keyboard(),
    )

async def on_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Хорошо. Я рядом.",
        reply_markup=main_menu_keyboard(),
    )

# =============================
# 📊 БИЗНЕС-АНАЛИЗ (хаб)
# =============================

async def on_business_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "📊 Бизнес-анализ\n\n"
        "Здесь вы можете посмотреть на бизнес со стороны.\n"
        "Не чтобы найти «правильный ответ»,\n"
        "а чтобы прояснить риски, ограничения\n"
        "и точки неопределённости.",
        reply_markup=business_hub_keyboard(),
    )

async def on_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Главное меню",
        reply_markup=main_menu_keyboard(),
    )

# =============================
# 💰 ПРИБЫЛЬ И ДЕНЬГИ (FSM)
# =============================

async def pm_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data[PM_STATE_KEY] = PM_STATE_REVENUE

    await update.message.reply_text(
        "💰 Прибыль и деньги\n\n"
        "Укажи выручку за выбранный месяц.\n"
        "Сколько денег фактически поступило от клиентов.\n"
        "Без прогнозов и ожиданий — только реальные поступления.\n"
        "Период важен: считаем один конкретный месяц.",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton(BTN_BACK)]], resize_keyboard=True),
    )

async def pm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").replace(" ", "").replace(",", "").strip()
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
        context.user_data.clear()

        await update.message.reply_text(
            "Итог за месяц:\n"
            "Прибыль — разница между выручкой и расходами.\n"
            "Маржа показывает, сколько остаётся с каждого рубля.\n"
            "Это не оценка бизнеса, а снимок текущего состояния.\n\n"
            f"Выручка: {revenue}\n"
            f"Расходы: {expenses}\n"
            f"Прибыль: {profit}\n"
            f"Маржа: {margin:.1f}%",
            reply_markup=business_hub_keyboard(),
        )

# =============================
# 🚀 РОСТ И ПРОДАЖИ (FSM)
# =============================

async def growth_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data[GROWTH_KEY] = True

    await update.message.reply_text(
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
    context.user_data.clear()

    await update.message.reply_text(
        "📈 Текущая картина:\n\n"
        f"Источник клиентов: {channel}\n\n"
        "Мы зафиксировали основной источник клиентов.\n"
        "Это не оценка и не вывод о качестве канала,\n"
        "а точка текущего состояния.\n\n"
        "Фокус на одном канале нужен,\n"
        "чтобы видеть ограничения и нагрузку,\n"
        "а не распыляться на ожидания.\n\n"
        "Рост начинается не с ускорения,\n"
        "а с понимания пределов и того,\n"
        "выдерживает ли система большее давление.",
        reply_markup=business_hub_keyboard(),
    )

# =============================
# 📦 АНАЛИТИКА ТОВАРА — FSM v1
# =============================

async def ta_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data[TA_STATE_KEY] = TA_STAGE

    await update.message.reply_text(
        "📦 Аналитика товара\n\n"
        "Этот сценарий не даёт ответов «стоит или нет».\n"
        "Он помогает спокойно посмотреть на ограничения\n"
        "и снизить риск самообмана.\n\n"
        "Перед тем как идти дальше,\n"
        "важно понять, в каком контексте существует этот товар.\n\n"
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
            "Попробуем оценить, насколько товар чувствителен к изменению цены.\n\n"
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

    # простая логика ориентиров (не “совет”)
    verdict = "Осторожно"
    if data.get("product_purpose") == "Решает конкретную проблему" and data.get("resource") != "Минимальный ресурс":
        verdict = "Гипотеза допустима для проверки, но не является рекомендацией"
    if data.get("product_purpose") in ("Желание / эмоция", "Не до конца понятно") and data.get("resource") == "Минимальный ресурс":
        verdict = "Высокий риск"

    context.user_data.clear()

    await update.message.reply_text(
        "Мы зафиксировали текущее состояние товара.\n"
        "Вердикт — это ориентир, а не решение.\n"
        "Он показывает, где стоит двигаться аккуратно.\n\n"
        f"Вердикт: {verdict}\n\n"
        "Даже аккуратный анализ не снимает риск.\n"
        "Окончательное решение всегда остаётся за тобой.\n"
        "Этот сценарий помогает видеть рамки,\n"
        "а не обещает результат.\n\n"
        "Следующий шаг —\n"
        "проверить спрос малыми действиями\n"
        "без масштабирования.",
        reply_markup=main_menu_keyboard(),
    )

# =============================
# 🔎 ПОДБОР НИШИ — FSM v1
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
    context.user_data.clear()
    context.user_data[NS_STEP_KEY] = 1

    await update.message.reply_text(
        "🔎 Подбор ниши\n\n"
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

        # ориентир (не рекомендация)
        verdict = "Осторожно"
        if context.user_data.get("demand") == NS_DEMAND_PROBLEM and context.user_data.get("resource") != NS_RESOURCE_MIN:
            verdict = "Можно смотреть"
        if context.user_data.get("demand") == NS_DEMAND_EMOTION and context.user_data.get("resource") == NS_RESOURCE_MIN:
            verdict = "Высокий риск"

        context.user_data.clear()

        await update.message.reply_text(
            "Этот результат не подбирает нишу за тебя.\n"
            "Он показывает рамки и ограничения,\n"
            "с которыми придётся работать.\n\n"
            f"Вердикт: {verdict}\n\n"
            "Осторожность здесь — способ снизить риски,\n"
            "а не сигнал «не делать».\n\n"
            "Вердикт — ориентир, а не рекомендация.\n"
            "Решение и ответственность остаются у тебя.\n\n"
            "Следующий шаг —\n"
            "перейти к аналитике конкретного товара или идеи.",
            reply_markup=main_menu_keyboard(),
        )

# =============================
# ❤️ PREMIUM
# =============================

async def premium_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data[PREMIUM_KEY] = True

    await update.message.reply_text(
        "❤️ Premium — больше ясности\n\n"
        "Premium в Artbazar AI нужен не для ответов.\n"
        "Он помогает глубже увидеть связи между решениями,\n"
        "риски и ограничения, которые не всегда заметны сразу.\n"
        "Анализ становится спокойнее и последовательнее,\n"
        "без советов и без давления.\n\n"
        "Premium не снимает неопределённость —\n"
        "он делает её более видимой.\n\n"
        "Premium не делает решения правильными.\n"
        "Он делает их более осознанными.",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton(BTN_BACK)]], resize_keyboard=True),
    )

# =============================
# ПРОЧЕЕ
# =============================

async def on_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "👤 Личный кабинет\n\nИстория появится позже.",
        reply_markup=main_menu_keyboard(),
    )

# =============================
# ROUTER
# =============================

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""

    # глобальный Back
    if text == BTN_BACK:
        # если пользователь в бизнес-хабе (💰/🚀) — возвращаем туда, иначе в меню
        if context.user_data.get(PM_STATE_KEY) or context.user_data.get(GROWTH_KEY):
            context.user_data.clear()
            await update.message.reply_text("📊 Бизнес-анализ", reply_markup=business_hub_keyboard())
            return
        context.user_data.clear()
        await update.message.reply_text("Главное меню", reply_markup=main_menu_keyboard())
        return

    # FSM приоритеты
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
        # Premium одноэкранный, Back уже обработан выше
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

    # бизнес-хаб сценарии
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PM}$"), pm_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_GROWTH}$"), growth_start))

    # product/niche
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_ANALYSIS}$"), ta_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NICHE}$"), ns_start))

    # back
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_BACK}$"), on_back))

    # общий роутер текста
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
