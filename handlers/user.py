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

# Рост и продажи — каналы
BTN_INST = "Instagram"
BTN_TG = "Telegram"
BTN_MP = "Маркетплейс"
BTN_KASPI = "Kaspi"
BTN_WB = "Wildberries"
BTN_OZON = "Ozon"
BTN_OFFLINE = "Офлайн"
BTN_OTHER = "Другое"

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
            [KeyboardButton(BTN_MP), KeyboardButton(BTN_KASPI)],
            [KeyboardButton(BTN_WB), KeyboardButton(BTN_OZON)],
            [KeyboardButton(BTN_OFFLINE), KeyboardButton(BTN_OTHER)],
            [KeyboardButton(BTN_BACK)],
        ],
        resize_keyboard=True,
    )

# =============================
# START FLOW (USER) — CANONICAL
# =============================

async def cmd_start_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    user = update.effective_user
    name = user.first_name or user.username or "друг"

    text = (
        f"Привет, {name} 👋\n\n"
        "Тебя приветствует Artbazar AI — аналитический помощник для предпринимателей.\n\n"
        "Я помогаю:\n"
        "• проверять идеи и товары\n"
        "• считать экономику\n"
        "• выбирать ниши\n"
        "• снижать риск ошибок\n\n"
        "⚠️ Важно:\n"
        "Любая аналитика — это ориентир, а не гарантия.\n"
        "Рынок меняется, данные могут быть неполными.\n"
        "Финальные решения всегда остаются за тобой.\n\n"
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
# 📊 БИЗНЕС-АНАЛИЗ (ХАБ)
# =============================

async def on_business_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Бизнес-анализ\n\nВыбери сценарий:",
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
        "💰 Прибыль и деньги\n\nВведи выручку:",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(BTN_BACK)]],
            resize_keyboard=True,
        ),
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
        await update.message.reply_text("Теперь введи расходы:")
        return

    if state == "expenses":
        revenue = context.user_data["revenue"]
        expenses = int(text)
        profit = revenue - expenses
        margin = (profit / revenue * 100) if revenue else 0

        context.user_data.clear()

        await update.message.reply_text(
            f"📊 Результат:\n\n"
            f"Выручка: {revenue}\n"
            f"Расходы: {expenses}\n"
            f"Прибыль: {profit}\n"
            f"Маржа: {margin:.1f}%\n\n"
            "Это ориентир, а не финансовый совет.",
            reply_markup=business_hub_keyboard(),
        )

# =============================
# FSM 🚀 РОСТ И ПРОДАЖИ
# =============================

async def growth_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["gs_state"] = "channel"

    await update.message.reply_text(
        "🚀 Рост и продажи\n\nГде основной канал продаж?",
        reply_markup=growth_channels_keyboard(),
    )


async def growth_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("gs_state") == "channel":
        channel = update.message.text
        context.user_data.clear()

        await update.message.reply_text(
            "📈 План роста:\n\n"
            f"Канал: {channel}\n\n"
            "1️⃣ Усиль поток клиентов\n"
            "2️⃣ Проверь оффер\n"
            "3️⃣ Убери узкие места\n\n"
            "Работай по одному шагу.",
            reply_markup=business_hub_keyboard(),
        )

# =============================
# ЗАГЛУШКИ
# =============================

async def ta_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "📊 Аналитика товара\n\nРаздел в разработке.",
        reply_markup=main_menu_keyboard(),
    )


async def ns_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔎 Подбор ниши\n\nРаздел в разработке.",
        reply_markup=main_menu_keyboard(),
    )


async def on_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👤 Личный кабинет\n\nРаздел в разработке.",
        reply_markup=main_menu_keyboard(),
    )


async def on_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❤️ Premium\n\nПодключение будет доступно позже.",
        reply_markup=main_menu_keyboard(),
    )

# =============================
# FSM ROUTER
# =============================

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("pm_state"):
        await pm_handler(update, context)
    elif context.user_data.get("gs_state"):
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

    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_ANALYSIS}$"), ta_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NICHE}$"), ns_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PROFILE}$"), on_profile))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PREMIUM}$"), on_premium))

    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_BACK}$"), on_back))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
