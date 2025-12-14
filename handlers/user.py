from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters

# =============================
# КНОПКИ (USER)
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

# Рост и продажи — каналы (человеческие + аккуратные)
BTN_INST = "📸 Instagram"
BTN_TG = "✈️ Telegram"
BTN_MP = "🛒 Маркетплейсы"
BTN_KASPI = "💳 Kaspi"
BTN_WB = "📦 Wildberries"
BTN_OZON = "📦 Ozon"
BTN_OFFLINE = "🏬 Офлайн"
BTN_OTHER = "🔧 Другое"

# Подбор ниши — форматы
BTN_N_ONLINE = "🌐 Онлайн"
BTN_N_OFFLINE = "🏬 Офлайн"
BTN_N_NO_STOCK = "📦 Без склада"
BTN_N_SERVICE = "🛠 Услуги"
BTN_N_FAST = "⚡ Быстрый старт"


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


def niche_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_N_ONLINE), KeyboardButton(BTN_N_OFFLINE)],
            [KeyboardButton(BTN_N_NO_STOCK), KeyboardButton(BTN_N_SERVICE)],
            [KeyboardButton(BTN_N_FAST)],
            [KeyboardButton(BTN_BACK)],
        ],
        resize_keyboard=True,
    )


def back_only_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton(BTN_BACK)]],
        resize_keyboard=True,
    )


# =============================
# /start (USER) — КАНОН
# =============================

async def cmd_start_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    user = update.effective_user
    name = user.first_name or user.username or "друг"

    text = (
        f"Привет, {name} 👋\n\n"
        "Ты в *Artbazar AI* — помощнике для предпринимателей.\n\n"
        "Здесь ты можешь:\n"
        "• спокойно проверить идею\n"
        "• понять, где деньги, а где риск\n"
        "• выбрать нишу без догадок\n"
        "• не наделать типичных ошибок\n\n"
        "⚠️ Важно:\n"
        "Бот не обещает прибыль.\n"
        "Он помогает *думать трезво* и принимать решения.\n\n"
        "Продолжим?"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
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
# 📊 БИЗНЕС-АНАЛИЗ (ХАБ)
# =============================

async def on_business_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 *Бизнес-анализ*\n\n"
        "Тут — короткие сценарии без сложных терминов.\n"
        "Выбирай, что сейчас важнее:",
        parse_mode="Markdown",
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
        "💰 *Прибыль и деньги*\n\n"
        "Сейчас быстро посчитаем базовую картину.\n"
        "Это займёт ~30 секунд.\n\n"
        "Шаг 1/2: введи *выручку в месяц* (одно число).\n"
        "Пример: 150000",
        parse_mode="Markdown",
        reply_markup=back_only_keyboard(),
    )


async def pm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("pm_state")
    raw = (update.message.text or "").strip()

    # страховка: если внезапно текст пустой
    if not raw:
        await update.message.reply_text("Введи число, пожалуйста. Например: 150000")
        return

    text = raw.replace(" ", "")

    if not text.isdigit():
        await update.message.reply_text("Нужно ввести число. Пример: 150000")
        return

    if state == "revenue":
        context.user_data["revenue"] = int(text)
        context.user_data["pm_state"] = "expenses"
        await update.message.reply_text(
            "Шаг 2/2: теперь введи *расходы в месяц* (одно число).\n"
            "Пример: 90000",
            parse_mode="Markdown",
        )
        return

    if state == "expenses":
        revenue = context.user_data.get("revenue", 0)
        expenses = int(text)

        profit = revenue - expenses
        margin = (profit / revenue * 100) if revenue else 0

        context.user_data.clear()

        await update.message.reply_text(
            "📊 *Результат:*\n\n"
            f"Выручка: {revenue}\n"
            f"Расходы: {expenses}\n"
            f"Прибыль: {profit}\n"
            f"Маржа: {margin:.1f}%\n\n"
            "Коротко:\n"
            "• *прибыль* — сколько остаётся после расходов\n"
            "• *маржа* — доля прибыли в выручке\n\n"
            "Это ориентир, а не финансовый совет.",
            parse_mode="Markdown",
            reply_markup=business_hub_keyboard(),
        )


# =============================
# FSM 🚀 РОСТ И ПРОДАЖИ
# =============================

async def growth_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["gs_state"] = "channel"

    await update.message.reply_text(
        "🚀 *Рост и продажи*\n\n"
        "Сначала определим, откуда сейчас приходят клиенты.\n"
        "Так план будет “в тему”, а не пальцем в небо.\n\n"
        "Шаг 1/1: выбери основной канал:",
        parse_mode="Markdown",
        reply_markup=growth_channels_keyboard(),
    )


async def growth_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("gs_state") != "channel":
        return

    channel = (update.message.text or "").strip()
    context.user_data.clear()

    await update.message.reply_text(
        "📈 *План роста (коротко):*\n\n"
        f"Канал: {channel}\n\n"
        "1️⃣ Усиль поток клиентов\n"
        "— больше людей должны увидеть тебя/оффер\n\n"
        "2️⃣ Проверь оффер\n"
        "— понятно ли, что ты продаёшь и почему это выгодно\n\n"
        "3️⃣ Убери узкие места\n"
        "— где теряются клиенты: сообщение/сайт/оплата/доставка\n\n"
        "Работай по одному шагу.",
        parse_mode="Markdown",
        reply_markup=business_hub_keyboard(),
    )


# =============================
# 📦 АНАЛИТИКА ТОВАРА (БАЗОВЫЙ ГОТОВЫЙ FLOW)
# =============================

async def ta_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "📦 *Аналитика товара*\n\n"
        "Этот блок нужен, чтобы *не закупиться в стену*.\n\n"
        "Что ты получишь:\n"
        "• на что смотреть в спросе\n"
        "• где чаще всего риск\n"
        "• стоит ли тестировать (и как безопасно)\n\n"
        "✅ Если после анализа остаются сомнения — это тоже результат.",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )


# =============================
# 🔎 ПОДБОР НИШИ (ПРОСТОЙ ГОТОВЫЙ FLOW)
# =============================

async def ns_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["niche_state"] = "choose"

    await update.message.reply_text(
        "🔎 *Подбор ниши*\n\n"
        "Выбери формат, который тебе ближе.\n"
        "Я дам короткую рекомендацию и следующий шаг:",
        parse_mode="Markdown",
        reply_markup=niche_keyboard(),
    )


async def niche_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("niche_state") != "choose":
        return

    choice = (update.message.text or "").strip()
    context.user_data.clear()

    await update.message.reply_text(
        "🎯 *Рекомендация:*\n\n"
        f"Формат: {choice}\n\n"
        "Дальше делай так:\n"
        "1) выбери 1 идею\n"
        "2) проверь спрос маленьким тестом\n"
        "3) не вкладывай всё сразу\n\n"
        "Если хочешь — вернись и выбери другой формат, сравним.",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )


# =============================
# 👤 ЛИЧНЫЙ КАБИНЕТ (ПОКА ПРОСТОЙ)
# =============================

async def on_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👤 *Личный кабинет*\n\n"
        "Здесь будет история расчётов и сценариев.\n"
        "Пока — в разработке.",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )


# =============================
# ❤️ PREMIUM (КАНОН. КОНТАКТ ФИКСИРОВАН)
# =============================

async def on_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❤️ *Premium*\n\n"
        "Premium — это помощь менеджера, когда нужно принять решение.\n\n"
        "📩 Для подключения напиши менеджеру:\n"
        "@Artbazar_marketing",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )


# =============================
# ROUTER (FSM)
# =============================

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # если это нажатие “⬅️ Назад” — НЕ трогаем FSM
    if (update.message.text or "").strip() == BTN_BACK:
        return

    if context.user_data.get("pm_state"):
        await pm_handler(update, context)
        return

    if context.user_data.get("gs_state"):
        await growth_handler(update, context)
        return

    if context.user_data.get("niche_state"):
        await niche_handler(update, context)
        return


# =============================
# REGISTER
# =============================

def register_handlers_user(app):
    # стартовые “Да/Нет”
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_YES}$"), on_yes))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NO}$"), on_no))

    # главное меню
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_BIZ}$"), on_business_analysis))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_ANALYSIS}$"), ta_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NICHE}$"), ns_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PROFILE}$"), on_profile))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PREMIUM}$"), on_premium))

    # бизнес-хаб
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PM}$"), pm_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_GROWTH}$"), growth_start))

    # назад
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_BACK}$"), on_back))

    # роутер FSM — в самом конце
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
