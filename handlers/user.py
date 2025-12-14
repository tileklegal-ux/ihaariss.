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
            [KeyboardButton("📸 Instagram"), KeyboardButton("✈️ Telegram")],
            [KeyboardButton("💳 Kaspi"), KeyboardButton("📦 Wildberries")],
            [KeyboardButton("📦 Ozon"), KeyboardButton("🏬 Офлайн")],
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
        "Я помогаю разложить решения по полочкам,\n"
        "снизить неопределённость и увидеть ограничения.\n\n"
        "⚠️ Важно:\n"
        "Это не прогноз и не гарантия результата.\n"
        "Решения всегда остаются за тобой.\n\n"
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
# 📊 БИЗНЕС-АНАЛИЗ
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
# 💰 ПРИБЫЛЬ И ДЕНЬГИ (FSM)
# =============================

async def pm_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["pm_state"] = "revenue"

    await update.message.reply_text(
        "💰 Прибыль и деньги\n\n"
        "Укажи выручку за выбранный месяц.\n"
        "Сколько денег фактически поступило от клиентов.\n"
        "Без прогнозов и ожиданий — только реальные поступления.\n"
        "Считаем один конкретный месяц.",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton(BTN_BACK)]], resize_keyboard=True),
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
            "Теперь укажи расходы за этот же месяц.\n"
            "Включай всё, что платил для работы бизнеса.\n"
            "Лучше заложить больше, чем забыть часть затрат.\n"
            "Нужна общая сумма за период."
        )
        return

    revenue = context.user_data["revenue"]
    expenses = int(text)
    profit = revenue - expenses
    margin = (profit / revenue * 100) if revenue else 0
    context.user_data.clear()

    await update.message.reply_text(
        f"📊 Результат за месяц:\n\n"
        f"Выручка: {revenue}\n"
        f"Расходы: {expenses}\n"
        f"Прибыль: {profit}\n"
        f"Маржа: {margin:.1f}%\n\n"
        "Это не прогноз и не оценка будущего.\n"
        "Это снимок текущего состояния бизнеса за период.",
        reply_markup=business_hub_keyboard(),
    )

# =============================
# 🚀 РОСТ И ПРОДАЖИ
# =============================

async def growth_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["growth"] = True

    await update.message.reply_text(
        "🚀 Рост и продажи\n\n"
        "Этот шаг нужен не для оценки эффективности.\n"
        "Мы просто фиксируем, откуда клиенты приходят сейчас,\n"
        "без ожиданий и планов на рост.",
        reply_markup=growth_channels_keyboard(),
    )

async def growth_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel = update.message.text
    context.user_data.clear()

    await update.message.reply_text(
        f"📈 Текущая картина:\n\n"
        f"Источник клиентов: {channel}\n\n"
        "Это не оценка качества канала,\n"
        "а фиксация текущего состояния.\n\n"
        "Фокус на одном канале нужен,\n"
        "чтобы видеть ограничения и нагрузку.\n\n"
        "Рост — это не увеличение цифр,\n"
        "а проверка, выдерживает ли система большее давление.",
        reply_markup=business_hub_keyboard(),
    )

# =============================
# 📦 АНАЛИТИКА ТОВАРА / 🔎 ПОДБОР НИШИ
# (уже реализованы ранее)
# =============================

async def on_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👤 Личный кабинет\n\nИстория появится позже.",
        reply_markup=main_menu_keyboard(),
    )

async def on_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❤️ Premium\n\n"
        "Premium не делает решения правильными.\n"
        "Он делает их более осознанными.\n\n"
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

# =============================
# REGISTER
# =============================

def register_handlers_user(app):
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_YES}$"), on_yes))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NO}$"), on_no))

    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_BIZ}$"), on_business_analysis))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PM}$"), pm_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_GROWTH}$"), growth_start))

    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PROFILE}$"), on_profile))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PREMIUM}$"), on_premium))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_BACK}$"), on_back))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
