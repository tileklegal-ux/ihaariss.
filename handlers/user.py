from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters

# =============================
# КНОПКИ
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

# Каналы продаж
BTN_INST = "📸 Instagram"
BTN_TG = "✈️ Telegram"
BTN_KASPI = "💳 Kaspi"
BTN_WB = "📦 Wildberries"
BTN_OZON = "📦 Ozon"
BTN_OFFLINE = "🏬 Офлайн"
BTN_OTHER = "🔧 Другое"

# Ниши
BTN_ONLINE = "🌐 Онлайн"
BTN_OFFLINE_N = "🏬 Офлайн"
BTN_NO_STOCK = "📦 Без склада"
BTN_SERVICE = "🛠 Услуги"
BTN_FAST = "⚡ Быстрый старт"

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
            [KeyboardButton(BTN_INST), KeyboardButton(BTN_TG)],
            [KeyboardButton(BTN_KASPI), KeyboardButton(BTN_WB)],
            [KeyboardButton(BTN_OZON), KeyboardButton(BTN_OFFLINE)],
            [KeyboardButton(BTN_OTHER)],
            [KeyboardButton(BTN_BACK)],
        ],
        resize_keyboard=True,
    )

def niche_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_ONLINE), KeyboardButton(BTN_OFFLINE_N)],
            [KeyboardButton(BTN_NO_STOCK), KeyboardButton(BTN_SERVICE)],
            [KeyboardButton(BTN_FAST)],
            [KeyboardButton(BTN_BACK)],
        ],
        resize_keyboard=True,
    )

# =============================
# START
# =============================

async def cmd_start_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    user = update.effective_user
    name = user.first_name or user.username or "друг"

    await update.message.reply_text(
        f"Привет, {name} 👋\n\n"
        "Ты в Artbazar AI — аналитическом помощнике для предпринимателей.\n\n"
        "Я помогаю разложить бизнес-решения по полочкам и снизить неопределённость.\n\n"
        "⚠️ Важно:\n"
        "Любая аналитика — это ориентир, а не гарантия.\n"
        "Решения всегда остаются за тобой.\n\n"
        "Продолжим?",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(BTN_YES), KeyboardButton(BTN_NO)]],
            resize_keyboard=True,
        ),
    )

async def on_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Выбери, с чего начнём 👇",
        reply_markup=main_menu_keyboard(),
    )

async def on_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Хорошо. Я рядом, когда понадобится.",
        reply_markup=main_menu_keyboard(),
    )

# =============================
# БИЗНЕС-АНАЛИЗ
# =============================

async def on_business_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Бизнес-анализ\n\n"
        "Здесь анализ — это логика и ограничения,\n"
        "а не отчёты и графики.",
        reply_markup=business_hub_keyboard(),
    )

async def on_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Главное меню",
        reply_markup=main_menu_keyboard(),
    )

# =============================
# FSM 💰 ПРИБЫЛЬ И ДЕНЬГИ
# =============================

async def pm_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["pm_state"] = "revenue"

    await update.message.reply_text(
        "💰 Прибыль и деньги\n\n"
        "Разберём деньги без обещаний и прогнозов —\n"
        "только реальность и ограничения.\n\n"
        "Укажи выручку за месяц.\n"
        "Сколько денег фактически пришло от клиентов.\n"
        "Без ожиданий и планов — только факт.",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(BTN_BACK)]],
            resize_keyboard=True,
        ),
    )

async def pm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace(" ", "")
    if not text.isdigit():
        await update.message.reply_text("Введи число, без букв.")
        return

    if context.user_data.get("pm_state") == "revenue":
        context.user_data["revenue"] = int(text)
        context.user_data["pm_state"] = "expenses"
        await update.message.reply_text(
            "Теперь расходы за этот же месяц.\n"
            "Закупки, реклама, аренда, сервисы, комиссии.\n"
            "Если сомневаешься — лучше завысить, чем забыть."
        )
        return

    revenue = context.user_data["revenue"]
    expenses = int(text)
    profit = revenue - expenses
    margin = (profit / revenue * 100) if revenue else 0
    context.user_data.clear()

    await update.message.reply_text(
        f"📊 Итог за месяц:\n\n"
        f"Прибыль: {profit}\n"
        f"Маржа: {margin:.1f}%\n\n"
        "Это не оценка бизнеса.\n"
        "Это снимок текущего состояния.",
        reply_markup=business_hub_keyboard(),
    )

# =============================
# FSM 🚀 РОСТ И ПРОДАЖИ
# =============================

async def growth_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["growth"] = True

    await update.message.reply_text(
        "🚀 Рост и продажи\n\n"
        "Рост здесь — не ускорение любой ценой,\n"
        "а понимание, где он вообще возможен.\n\n"
        "Откуда к вам сейчас чаще всего приходят клиенты?",
        reply_markup=growth_channels_keyboard(),
    )

async def growth_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel = update.message.text
    context.user_data.clear()

    await update.message.reply_text(
        f"📈 План роста:\n\n"
        f"Основной канал: {channel}\n\n"
        "Мы фиксируем точку контроля.\n"
        "Следующий шаг — усилить этот канал\n"
        "или снизить зависимость от него.",
        reply_markup=business_hub_keyboard(),
    )

# =============================
# 📦 АНАЛИТИКА ТОВАРА (ПРЕ-ЭКРАН)
# =============================

async def ta_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📦 Аналитика товара\n\n"
        "Этот сценарий помогает трезво посмотреть на конкретный товар.\n"
        "Мы разберём спрос, сезонность и риски,\n"
        "чтобы понять, стоит ли его тестировать сейчас.\n\n"
        "Результат — ориентир для решения, а не прогноз.",
        reply_markup=main_menu_keyboard(),
    )

# =============================
# 🔎 ПОДБОР НИШИ (ПРЕ-ЭКРАН)
# =============================

async def ns_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["niche"] = True

    await update.message.reply_text(
        "🔎 Подбор ниши\n\n"
        "Здесь мы не ищем «лучшую нишу».\n"
        "Мы сужаем варианты и убираем заведомо слабые направления.\n\n"
        "На выходе — рамки и риски, с которыми придётся работать.",
        reply_markup=niche_keyboard(),
    )

async def niche_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    context.user_data.clear()

    await update.message.reply_text(
        f"🎯 Формат: {choice}\n\n"
        "Это не рекомендация.\n"
        "Это ориентир для первого шага.",
        reply_markup=main_menu_keyboard(),
    )

# =============================
# ПРОЧЕЕ
# =============================

async def on_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👤 Личный кабинет\n\nИстория появится позже.",
        reply_markup=main_menu_keyboard(),
    )

async def on_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❤️ Premium\n\n"
        "Больше глубины и спокойствия при решениях.\n\n"
        "📩 Напиши: @Artbazar_marketing",
        reply_markup=main_menu_keyboard(),
    )

# =============================
# ROUTER
# =============================

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("pm_state"):
        await pm_handler(update, context)
    elif context.user_data.get("growth"):
        await growth_handler(update, context)
    elif context.user_data.get("niche"):
        await niche_handler(update, context)

# =============================
# REGISTER
# =============================

def register_handlers_user(app):
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_YES}$"), on_yes))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NO}$"), on_no))

    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_BIZ}$"), on_business_analysis))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PM}$"), pm_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_GROWTH}$"), growth_start))

    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_ANALYSIS}$"), ta_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NICHE}$"), ns_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PROFILE}$"), on_profile))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PREMIUM}$"), on_premium))

    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_BACK}$"), on_back))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
