from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from services.niche_selection_flow import (
    map_telegram_answers_to_internal,
    generate_niche_recommendations,
)
from services.menu import send_main_menu


# -------------------------------------------------------------
# СТАДИИ
# -------------------------------------------------------------
ASK_SEASON, ASK_FORMAT, ASK_BUDGET, ASK_EXPERIENCE, ASK_AUDIENCE, ASK_INTERESTS = range(6)

# Кнопки
BTN_CANCEL = "❌ Отмена"
BTN_START_FLOW = "🚀 Начать подбор ниши"

SEASON_OPTIONS = ["Весна/Лето", "Осень/Зима", "Круглый год", "Пока не знаю"]
FORMAT_OPTIONS = [
    "Marketplace (Kaspi/Ozon/WB)",
    "Instagram/Telegram",
    "Оффлайн точка",
    "Самозанятый / мелкая торговля",
]
BUDGET_OPTIONS = ["Низкий бюджет", "Средний бюджет", "Высокий бюджет"]
EXPERIENCE_OPTIONS = ["Нет опыта", "Есть базовый опыт", "Опытный предприниматель"]
AUDIENCE_OPTIONS = [
    "Женская аудитория",
    "Мужская аудитория",
    "Родители и дети",
    "Автовладельцы",
    "Универсальные товары",
]

INTEREST_PRESETS = [
    "Авто и запчасти 🚗",
    "Дом, ремонт, интерьер 🏡",
    "Гаджеты и техника 📱",
    "Спорт и активность 🏋️",
    "Красота и уход 💄",
    "Детские товары 👶",
    "Хобби и творчество 🎨",
]


# -------------------------------------------------------------
# ONBOARDING
# -------------------------------------------------------------
async def start_niche_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [BTN_START_FLOW],
        [BTN_CANCEL],
    ]

    text = (
        "🔍 *Подбор ниши*\n\n"
        "Я помогу подобрать нишу под ваш бюджет, сезон, опыт и аудиторию.\n"
        "Работаю без воды — только реалистичные варианты.\n\n"
        "Готовы начать?"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )

    return ASK_SEASON


# -------------------------------------------------------------
# START FLOW (после нажатия 🚀)
# -------------------------------------------------------------
async def start_niche_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text != BTN_START_FLOW:
        # Если пришли сюда без нажатия кнопки — возвращаем онбординг
        return await start_niche_onboarding(update, context)

    context.user_data["niche_flow"] = {}

    keyboard = [
        [KeyboardButton(o) for o in SEASON_OPTIONS[:2]],
        [KeyboardButton(o) for o in SEASON_OPTIONS[2:]],
        [BTN_CANCEL],
    ]

    await update.message.reply_text(
        "Шаг 1 из 6\nВыберите сезон:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )

    return ASK_SEASON


# -------------------------------------------------------------
# CANCEL
# -------------------------------------------------------------
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Диалог подбора ниши отменён.")
    await send_main_menu(update)
    return ConversationHandler.END


# -------------------------------------------------------------
# SEASON
# -------------------------------------------------------------
async def ask_format(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == BTN_CANCEL:
        return await cancel(update, context)

    if text not in SEASON_OPTIONS:
        await update.message.reply_text("Выберите вариант с кнопок.")
        return ASK_SEASON

    context.user_data.setdefault("niche_flow", {})
    context.user_data["niche_flow"]["season"] = text

    keyboard = [[KeyboardButton(o)] for o in FORMAT_OPTIONS]
    keyboard.append([BTN_CANCEL])

    await update.message.reply_text(
        "Шаг 2 из 6\nВыберите формат бизнеса:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )

    return ASK_FORMAT


# -------------------------------------------------------------
# FORMAT
# -------------------------------------------------------------
async def ask_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == BTN_CANCEL:
        return await cancel(update, context)

    # Надёжная проверка формата бизнеса
    if text not in FORMAT_OPTIONS:
        await update.message.reply_text("Выберите вариант с кнопок.")
        return ASK_FORMAT

    context.user_data["niche_flow"]["format"] = text

    keyboard = [[KeyboardButton(o)] for o in BUDGET_OPTIONS]
    keyboard.append([BTN_CANCEL])

    await update.message.reply_text(
        "Шаг 3 из 6\nВыберите бюджет:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )

    return ASK_BUDGET


# -------------------------------------------------------------
# BUDGET
# -------------------------------------------------------------
async def ask_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == BTN_CANCEL:
        return await cancel(update, context)

    if text not in BUDGET_OPTIONS:
        await update.message.reply_text("Выберите вариант с кнопок.")
        return ASK_BUDGET

    context.user_data["niche_flow"]["budget"] = text

    keyboard = [[KeyboardButton(o)] for o in EXPERIENCE_OPTIONS]
    keyboard.append([BTN_CANCEL])

    await update.message.reply_text(
        "Шаг 4 из 6\nВаш уровень опыта:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )

    return ASK_EXPERIENCE


# -------------------------------------------------------------
# EXPERIENCE
# -------------------------------------------------------------
async def ask_audience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == BTN_CANCEL:
        return await cancel(update, context)

    if text not in EXPERIENCE_OPTIONS:
        await update.message.reply_text("Выберите вариант.")
        return ASK_EXPERIENCE

    context.user_data["niche_flow"]["experience"] = text

    keyboard = [[KeyboardButton(o)] for o in AUDIENCE_OPTIONS]
    keyboard.append([BTN_CANCEL])

    await update.message.reply_text(
        "Шаг 5 из 6\nВыберите аудиторию:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )

    return ASK_AUDIENCE


# -------------------------------------------------------------
# AUDIENCE
# -------------------------------------------------------------
async def ask_interests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == BTN_CANCEL:
        return await cancel(update, context)

    if text not in AUDIENCE_OPTIONS:
        await update.message.reply_text("Выберите вариант.")
        return ASK_AUDIENCE

    context.user_data["niche_flow"]["audience"] = text

    keyboard = [[KeyboardButton(p)] for p in INTEREST_PRESETS]
    keyboard.append([BTN_CANCEL])

    text_msg = (
        "Шаг 6 из 6\nРасскажите, что вам интересно.\n\n"
        "Можете выбрать вариант с кнопок или написать свой вариант."
    )

    await update.message.reply_text(
        text_msg,
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )

    return ASK_INTERESTS


# -------------------------------------------------------------
# FINAL STEP
# -------------------------------------------------------------
async def generate_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == BTN_CANCEL:
        return await cancel(update, context)

    context.user_data["niche_flow"]["interests"] = text
    flow = context.user_data["niche_flow"]

    await update.message.reply_text("Запускаем Artbazar AI… ⚙️")

    internal = map_telegram_answers_to_internal(
        season_text=flow["season"],
        business_format_text=flow["format"],
        budget_text=flow["budget"],
        experience_text=flow["experience"],
        audience_text=flow["audience"],
    )

    response = await generate_niche_recommendations(  # ✅ Исправлено здесь
        user_id=update.effective_user.id,
        season=internal["season"],
        business_format=internal["business_format"],
        budget=internal["budget"],
        experience=internal["experience"],
        audience=internal["audience"],
        interests=flow["interests"],
    )

    await update.message.reply_text(response)
    await send_main_menu(update)

    return ConversationHandler.END


# -------------------------------------------------------------
# EXPORT HANDLER
# -------------------------------------------------------------
def get_niche_selection_handler():
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^🔍 Подбор ниши$"), start_niche_onboarding),
        ],
        states={
            ASK_SEASON: [
                MessageHandler(
                    filters.Regex(f"^{BTN_START_FLOW}$"),
                    start_niche_selection,
                ),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    ask_format,
                ),
            ],
            ASK_FORMAT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    ask_budget,
                ),
            ],
            ASK_BUDGET: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    ask_experience,
                ),
            ],
            ASK_EXPERIENCE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    ask_audience,
                ),
            ],
            ASK_AUDIENCE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    ask_interests,
                ),
            ],
            ASK_INTERESTS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    generate_result,
                ),
            ],
        },
        fallbacks=[
            MessageHandler(filters.Regex(f"^{BTN_CANCEL}$"), cancel),
        ],
    )


# -------------------------------------------------------------
# REGISTRATION
# -------------------------------------------------------------
def register_niche_selection_handlers(app):
    app.add_handler(get_niche_selection_handler())
