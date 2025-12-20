# -*- coding: utf-8 -*-

from telegram import ReplyKeyboardMarkup, KeyboardButton

# =============================
# BUTTONS (TEXT)
# =============================

BTN_YES = "Да"
BTN_NO = "Нет"
BTN_BACK = "⬅️ Назад"

BTN_BIZ = "📊 Бизнес-анализ"
BTN_PM = "💰 Деньги и прибыль"
BTN_GROWTH = "📈 Рост и продажи"
BTN_COMPANY_STAGE = "📈 Этап компании"

BTN_ANALYSIS = "📦 Аналитика товара"
BTN_NICHE = "🔍 Подбор ниши"

BTN_PROFILE = "👤 Личный кабинет"
BTN_DOCS = "📄 Документы и условия"

BTN_PREMIUM = "⭐ Premium"
BTN_PREMIUM_BENEFITS = "❤️ Что даёт Premium"

# =============================
# AI НАСТАВНИК
# =============================

BTN_AI_CHAT = "🤖 AI-наставник"
BTN_EXIT_CHAT = "❌ Выйти из AI-чата"

# =============================
# KEYBOARDS
# =============================

def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_BIZ), KeyboardButton(BTN_AI_CHAT)],
            [KeyboardButton(BTN_ANALYSIS), KeyboardButton(BTN_NICHE)],
            [KeyboardButton(BTN_PROFILE)],
            [KeyboardButton(BTN_DOCS)],
            [KeyboardButton(BTN_PREMIUM)],
        ],
        resize_keyboard=True,
    )

def business_hub_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_PM), KeyboardButton(BTN_GROWTH)],
            [KeyboardButton(BTN_COMPANY_STAGE)],
            [KeyboardButton(BTN_BACK)],
        ],
        resize_keyboard=True,
    )

def pm_step_keyboard(step):
    if step == 1:
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("Услуги"), KeyboardButton("Товары")],
                [KeyboardButton("Смешанный"), KeyboardButton("Другое")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )
    elif step == 2:
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("Офлайн"), KeyboardButton("Онлайн")],
                [KeyboardButton("Оба"), KeyboardButton("Другое")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )
    elif step == 3:
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("Аренда"), KeyboardButton("Зарплаты")],
                [KeyboardButton("Налоги"), KeyboardButton("Другое")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )
    elif step == 4:
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("Материалы"), KeyboardButton("Логистика")],
                [KeyboardButton("Реклама"), KeyboardButton("Другое")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )
    elif step == 5:
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("До 10%"), KeyboardButton("10-20%")],
                [KeyboardButton("20-30%"), KeyboardButton("30%+")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )
    else:
        return step_keyboard()

def growth_step_keyboard(step):
    if step == 1:
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("Instagram"), KeyboardButton("TikTok")],
                [KeyboardButton("Маркетплейсы"), KeyboardButton("Сарафан")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )
    elif step == 2:
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("До 1%"), KeyboardButton("1-3%")],
                [KeyboardButton("3-5%"), KeyboardButton("5%+")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )
    elif step == 3:
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("До 100р"), KeyboardButton("100-500р")],
                [KeyboardButton("500-1000р"), KeyboardButton("1000р+")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )
    elif step == 4:
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("До 10%"), KeyboardButton("10-30%")],
                [KeyboardButton("30-50%"), KeyboardButton("50%+")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )
    elif step == 5:
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("Новый канал"), KeyboardButton("Улучшение текущего")],
                [KeyboardButton("Масштабирование"), KeyboardButton("Оптимизация")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )
    else:
        return step_keyboard()

def company_stage_keyboard(step, is_premium):
    if not is_premium and step == 2:
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("Посмотреть премиум")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )
    
    if is_premium and step == 10:
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("📈 Экспорт этапа")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )
    
    return step_keyboard()

def step_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton(BTN_BACK)]],
        resize_keyboard=True,
    )

def premium_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_PREMIUM_BENEFITS)],
            [KeyboardButton(BTN_BACK)],
        ],
        resize_keyboard=True,
    )

def ai_chat_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_EXIT_CHAT)],
        ],
        resize_keyboard=True,
    )
