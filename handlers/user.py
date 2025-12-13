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

BTN_ANALYSIS = "📊 Аналитика товара"
BTN_NICHE = "🔎 Подбор ниши"
BTN_PROFILE = "👤 Личный кабинет"
BTN_PREMIUM = "❤️ Премиум"

# Категории
BTN_CAT_CLOTHES = "👗 Одежда / обувь"
BTN_CAT_ELECTRONICS = "📱 Электроника"
BTN_CAT_HOME = "🏠 Товары для дома"
BTN_CAT_KIDS = "🧸 Детские товары"
BTN_CAT_AUTO = "🚗 Авто / аксессуары"
BTN_CAT_FOOD = "🍔 Еда / напитки"
BTN_CAT_BEAUTY = "🧴 Красота / уход"
BTN_CAT_OTHER = "📦 Другое"

# Цена
BTN_PRICE_LOW = "до 1 000"
BTN_PRICE_MID = "1 000 – 3 000"
BTN_PRICE_HIGH = "3 000 – 7 000"
BTN_PRICE_PREMIUM = "7 000+" 

# Конкуренция
BTN_COMP_LOW = "Низкая"
BTN_COMP_MED = "Средняя"
BTN_COMP_HIGH = "Высокая"


# =============================
# КЛАВИАТУРЫ
# =============================

def get_main_menu_keyboard():
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


def product_category_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_CAT_CLOTHES), KeyboardButton(BTN_CAT_ELECTRONICS)],
            [KeyboardButton(BTN_CAT_HOME), KeyboardButton(BTN_CAT_KIDS)],
            [KeyboardButton(BTN_CAT_AUTO), KeyboardButton(BTN_CAT_FOOD)],
            [KeyboardButton(BTN_CAT_BEAUTY), KeyboardButton(BTN_CAT_OTHER)],
            [KeyboardButton(BTN_BACK)],
        ],
        resize_keyboard=True,
    )


def price_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_PRICE_LOW), KeyboardButton(BTN_PRICE_MID)],
            [KeyboardButton(BTN_PRICE_HIGH), KeyboardButton(BTN_PRICE_PREMIUM)],
            [KeyboardButton(BTN_BACK)],
        ],
        resize_keyboard=True,
    )


def competition_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_COMP_LOW)],
            [KeyboardButton(BTN_COMP_MED)],
            [KeyboardButton(BTN_COMP_HIGH)],
            [KeyboardButton(BTN_BACK)],
        ],
        resize_keyboard=True,
    )


# =============================
# START FLOW
# =============================

async def cmd_start_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or user.username or "друг"

    await update.message.reply_text(
        f"Привет, {name} 👋\n\nПродолжим?",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(BTN_YES), KeyboardButton(BTN_NO)]],
            resize_keyboard=True,
        ),
    )


async def on_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выбери раздел 👇", reply_markup=get_main_menu_keyboard())


async def on_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Хорошо. Я рядом.", reply_markup=get_main_menu_keyboard())


# =============================
# БИЗНЕС-АНАЛИЗ
# =============================

async def on_business_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выбери сценарий:", reply_markup=business_hub_keyboard())


async def on_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Главное меню", reply_markup=get_main_menu_keyboard())


# =============================
# FSM 💰 ПРИБЫЛЬ И ДЕНЬГИ
# =============================

async def pm_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["pm_state"] = "revenue"
    await update.message.reply_text(
        "Введи выручку:",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton(BTN_BACK)]], resize_keyboard=True),
    )


async def pm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("pm_state")
    text = update.message.text.replace(" ", "")

    if not text.isdigit():
        await update.message.reply_text("Введи число.")
        return

    if state == "revenue":
        context.user_data["revenue"] = int(text)
        context.user_data["pm_state"] = "expenses"
        await update.message.reply_text("Теперь расходы:")
        return

    if state == "expenses":
        revenue = context.user_data["revenue"]
        expenses = int(text)
        profit = revenue - expenses
        margin = (profit / revenue * 100) if revenue else 0
        context.user_data.clear()

        await update.message.reply_text(
            f"Прибыль: {profit}\nМаржа: {margin:.1f}%",
            reply_markup=business_hub_keyboard(),
        )


# =============================
# FSM 🚀 РОСТ
# =============================

async def growth_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["gs_state"] = "start"
    await update.message.reply_text(
        "Где основной канал продаж?",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton(BTN_BACK)]], resize_keyboard=True),
    )


async def growth_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("План роста готов.", reply_markup=business_hub_keyboard())


# =============================
# FSM 📊 АНАЛИТИКА ТОВАРА (v1)
# =============================

async def ta_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["ta_state"] = "category"
    await update.message.reply_text(
        "Что ты хочешь продавать?",
        reply_markup=product_category_keyboard(),
    )


async def ta_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("ta_state")
    text = update.message.text

    if state == "category":
        context.user_data["category"] = text
        context.user_data["ta_state"] = "price"
        await update.message.reply_text("Выбери цену продажи:", reply_markup=price_keyboard())
        return

    if state == "price":
        context.user_data["price"] = text
        context.user_data["ta_state"] = "competition"
        await update.message.reply_text("Оцени конкуренцию:", reply_markup=competition_keyboard())
        return

    if state == "competition":
        category = context.user_data.get("category")
        price = context.user_data.get("price")
        competition = text

        verdict = "Можно тестировать"
        if competition == BTN_COMP_HIGH:
            verdict = "Сомнительно — высокая конкуренция"

        context.user_data.clear()

        await update.message.reply_text(
            f"📊 Итог:\n\n"
            f"{verdict}\n\n"
            f"Категория: {category}\n"
            f"Цена: {price}\n"
            f"Конкуренция: {competition}\n\n"
            f"Следующий шаг: протестируй спрос без закупки.",
            reply_markup=get_main_menu_keyboard(),
        )


# =============================
# FSM ROUTER
# =============================

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("pm_state"):
        await pm_handler(update, context)
    elif context.user_data.get("gs_state"):
        await growth_handler(update, context)
    elif context.user_data.get("ta_state"):
        await ta_handler(update, context)


# =============================
# ДРУГИЕ РАЗДЕЛЫ
# =============================

async def ns_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Скоро.", reply_markup=get_main_menu_keyboard())


async def on_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Скоро.", reply_markup=get_main_menu_keyboard())


async def on_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Скоро.", reply_markup=get_main_menu_keyboard())


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
