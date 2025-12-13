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
        reply_markup=ReplyKeyboardMarkup(
            [
                [KeyboardButton(BTN_BIZ)],
                [KeyboardButton(BTN_ANALYSIS)],
                [KeyboardButton(BTN_NICHE)],
                [KeyboardButton(BTN_PROFILE)],
                [KeyboardButton(BTN_PREMIUM)],
            ],
            resize_keyboard=True,
        ),
    )


async def on_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Хорошо. Я рядом.",
        reply_markup=ReplyKeyboardMarkup(
            [
                [KeyboardButton(BTN_BIZ)],
                [KeyboardButton(BTN_ANALYSIS)],
                [KeyboardButton(BTN_NICHE)],
                [KeyboardButton(BTN_PROFILE)],
                [KeyboardButton(BTN_PREMIUM)],
            ],
            resize_keyboard=True,
        ),
    )

# =============================
# 📊 АНАЛИТИКА ТОВАРА — ЗАГЛУШКА (ОБЯЗАТЕЛЬНА)
# =============================

async def ta_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "📊 Аналитика товара\n\n"
        "Этот раздел сейчас в разработке.\n"
        "Скоро здесь можно будет проверить товар "
        "и понять, стоит ли его тестировать.\n\n"
        "Пока можешь воспользоваться другими разделами 👇",
        reply_markup=ReplyKeyboardMarkup(
            [
                [KeyboardButton(BTN_BIZ)],
                [KeyboardButton(BTN_NICHE)],
                [KeyboardButton(BTN_PROFILE)],
                [KeyboardButton(BTN_PREMIUM)],
            ],
            resize_keyboard=True,
        ),
    )

# =============================
# REGISTER
# =============================

def register_handlers_user(app):
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_YES}$"), on_yes))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NO}$"), on_no))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_ANALYSIS}$"), ta_start))
