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

# Аналитика товара — кнопки FSM
BTN_CTX_PRODUCT = "Конкретный товар"
BTN_CTX_IDEA = "Идея / направление"
BTN_CTX_RESEARCH = "Изучаю рынок"

BTN_PURPOSE_PAIN = "Решает проблему"
BTN_PURPOSE_CONVENIENCE = "Удобство"
BTN_PURPOSE_EMOTION = "Эмоция"
BTN_PURPOSE_UNCLEAR = "Не до конца понятно"

BTN_SEASON_ALWAYS = "Почти всегда"
BTN_SEASON_MONTHS = "В определённые месяцы"
BTN_SEASON_WAVES = "Всплесками"
BTN_SEASON_UNKNOWN = "Не знаю"

BTN_COMP_LOW = "Почти нигде"
BTN_COMP_MED = "Иногда встречается"
BTN_COMP_HIGH = "Везде"
BTN_COMP_UNKNOWN = "Не смотрел"

BTN_PRICE_LOW = "Ниже рынка"
BTN_PRICE_MED = "Как у других"
BTN_PRICE_HIGH = "Выше рынка"
BTN_PRICE_UNKNOWN = "Пока не знаю"

BTN_RESOURCE_MONEY = "Деньги"
BTN_RESOURCE_TIME = "Время"
BTN_RESOURCE_SKILL = "Экспертиза"
BTN_RESOURCE_MIN = "Минимальный ресурс"

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

def kb(*rows):
    return ReplyKeyboardMarkup([[KeyboardButton(b) for b in row] for row in rows] + [[KeyboardButton(BTN_BACK)]], resize_keyboard=True)

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
        "Я помогаю:\n"
        "• разобраться в логике решений\n"
        "• увидеть ограничения и риски\n"
        "• выбрать следующий шаг без иллюзий\n\n"
        "⚠️ Важно:\n"
        "Любая аналитика — это ориентир, а не гарантия.\n"
        "Решения всегда остаются за тобой.\n\n"
        "Продолжим?",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton(BTN_YES), KeyboardButton(BTN_NO)]], resize_keyboard=True),
    )

async def on_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выбери, с чего начнём 👇", reply_markup=main_menu_keyboard())

async def on_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Хорошо. Я рядом.", reply_markup=main_menu_keyboard())

# =============================
# БИЗНЕС-АНАЛИЗ
# =============================

async def on_business_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Бизнес-анализ\n\n"
        "Здесь анализ — это логика и ограничения,\n"
        "а не отчёты и прогнозы.",
        reply_markup=business_hub_keyboard(),
    )

async def on_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Главное меню", reply_markup=main_menu_keyboard())

# =============================
# FSM 📦 АНАЛИТИКА ТОВАРА
# =============================

async def ta_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["ta_step"] = 1

    await update.message.reply_text(
        "📦 Аналитика товара\n\n"
        "Этот сценарий помогает трезво посмотреть на товар.\n"
        "Без прогнозов и обещаний.\n\n"
        "В каком контексте ты его рассматриваешь?",
        reply_markup=kb(
            [BTN_CTX_PRODUCT, BTN_CTX_IDEA],
            [BTN_CTX_RESEARCH],
        ),
    )

async def ta_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("ta_step")
    text = update.message.text

    if step == 1:
        context.user_data["context"] = text
        context.user_data["ta_step"] = 2
        await update.message.reply_text(
            "Зачем его обычно покупают?",
            reply_markup=kb(
                [BTN_PURPOSE_PAIN, BTN_PURPOSE_CONVENIENCE],
                [BTN_PURPOSE_EMOTION, BTN_PURPOSE_UNCLEAR],
            ),
        )
        return

    if step == 2:
        context.user_data["purpose"] = text
        context.user_data["ta_step"] = 3
        await update.message.reply_text(
            "Когда его покупают активнее?",
            reply_markup=kb(
                [BTN_SEASON_ALWAYS, BTN_SEASON_MONTHS],
                [BTN_SEASON_WAVES, BTN_SEASON_UNKNOWN],
            ),
        )
        return

    if step == 3:
        context.user_data["season"] = text
        context.user_data["ta_step"] = 4
        await update.message.reply_text(
            "Где ты уже видел этот товар?",
            reply_markup=kb(
                [BTN_COMP_LOW, BTN_COMP_MED],
                [BTN_COMP_HIGH, BTN_COMP_UNKNOWN],
            ),
        )
        return

    if step == 4:
        context.user_data["competition"] = text
        context.user_data["ta_step"] = 5
        await update.message.reply_text(
            "Как ты видишь цену относительно рынка?",
            reply_markup=kb(
                [BTN_PRICE_LOW, BTN_PRICE_MED],
                [BTN_PRICE_HIGH, BTN_PRICE_UNKNOWN],
            ),
        )
        return

    if step == 5:
        context.user_data["price"] = text
        context.user_data["ta_step"] = 6
        await update.message.reply_text(
            "Что у тебя есть для старта?",
            reply_markup=kb(
                [BTN_RESOURCE_MONEY, BTN_RESOURCE_TIME],
                [BTN_RESOURCE_SKILL, BTN_RESOURCE_MIN],
            ),
        )
        return

    if step == 6:
        context.user_data["resource"] = text

        await update.message.reply_text(
            "📊 Итог анализа\n\n"
            "Вердикт — это ориентир, а не инструкция.\n"
            "Я не выбираю за тебя — я показываю, где решение может быть хрупким.\n\n"
            "Следующий шаг:\n"
            "— протестировать малым объёмом\n"
            "— уточнить реальный спрос\n\n"
            "Осторожность здесь — не минус,\n"
            "а способ не потерять время и деньги.",
            reply_markup=main_menu_keyboard(),
        )

        context.user_data.clear()

# =============================
# ROUTER
# =============================

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("ta_step"):
        await ta_handler(update, context)

# =============================
# REGISTER
# =============================

def register_handlers_user(app):
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_YES}$"), on_yes))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NO}$"), on_no))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_BIZ}$"), on_business_analysis))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_ANALYSIS}$"), ta_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_BACK}$"), on_back))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
