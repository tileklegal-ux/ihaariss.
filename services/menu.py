from telegram import ReplyKeyboardMarkup, KeyboardButton

# ==================================================
# КНОПКИ ГЛАВНОГО МЕНЮ (ТОЛЬКО ТОЧКА ВХОДА)
# ==================================================

BTN_BIZ = "📊 Бизнес-анализ"
BTN_ANALYSIS = "📊 Аналитика товара"
BTN_NICHE = "🔎 Подбор ниши"
BTN_PROFILE = "👤 Личный кабинет"
BTN_PREMIUM = "❤️ Премиум"

# ==================================================
# ГЛАВНОЕ МЕНЮ
# ❗ НИКАКОЙ FSM-ЛОГИКИ
# ❗ НИКАКИХ ПОДМЕНЮ
# ❗ ТОЛЬКО ВХОД В РАЗДЕЛЫ
# ==================================================

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_BIZ)],
            [KeyboardButton(BTN_ANALYSIS), KeyboardButton(BTN_NICHE)],
            [KeyboardButton(BTN_PROFILE), KeyboardButton(BTN_PREMIUM)],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )
