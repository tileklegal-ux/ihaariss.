# -*- coding: utf-8 -*-

from telegram import ReplyKeyboardMarkup, KeyboardButton

# =============================
# BUTTONS (TEXT)
# =============================

BTN_YES = "Да"
BTN_NO = "Нет"
BTN_BACK = "⬅️ Назад"

BTN_BIZ = "📊 Бизнес-анализ"
BTN_PM = "💰 Прибыль и деньги"
BTN_GROWTH = "🚀 Рост и продажи"

BTN_ANALYSIS = "📦 Аналитика товара"
BTN_NICHE = "🔎 Подбор ниши"

BTN_PROFILE = "👤 Личный кабинет"
BTN_DOCS = "📄 Документы и условия"

BTN_PREMIUM = "❤️ Premium"
BTN_PREMIUM_BENEFITS = "❤️ Что даёт Premium"

# AI CHAT
BTN_AI_CHAT = "🧭 AI-наставник"
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
            [KeyboardButton(BTN_BACK)],
        ],
        resize_keyboard=True,
    )


def pm_step_keyboard(step):
    """Клавиатура для шагов FSM прибыли и денег"""
    if step == 1:
        # Шаг 1: Тип бизнеса
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("Услуги"), KeyboardButton("Товары")],
                [KeyboardButton("Смешанный"), KeyboardButton("Другое")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )
    elif step == 2:
        # Шаг 2: Источник выручки
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("Офлайн"), KeyboardButton("Онлайн")],
                [KeyboardButton("Оба"), KeyboardButton("Другое")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )
    elif step == 3:
        # Шаг 3: Постоянные расходы
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("Аренда"), KeyboardButton("Зарплаты")],
                [KeyboardButton("Налоги"), KeyboardButton("Другое")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )
    elif step == 4:
        # Шаг 4: Переменные расходы
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("Материалы"), KeyboardButton("Логистика")],
                [KeyboardButton("Реклама"), KeyboardButton("Другое")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )
    elif step == 5:
        # Шаг 5: Рентабельность
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("До 10%"), KeyboardButton("10-20%")],
                [KeyboardButton("20-30%"), KeyboardButton("30%+")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )
    else:
        return ReplyKeyboardMarkup(
            [[KeyboardButton(BTN_BACK)]],
            resize_keyboard=True,
        )


def growth_step_keyboard(step):
    """Клавиатура для шагов FSM роста и продаж"""
    if step == 1:
        # Шаг 1: Текущий канал
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("Instagram"), KeyboardButton("TikTok")],
                [KeyboardButton("Маркетплейсы"), KeyboardButton("Сарафан")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )
    elif step == 2:
        # Шаг 2: Конверсия
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("До 1%"), KeyboardButton("1-3%")],
                [KeyboardButton("3-5%"), KeyboardButton("5%+")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )
    elif step == 3:
        # Шаг 3: Стоимость привлечения
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("До 100р"), KeyboardButton("100-500р")],
                [KeyboardButton("500-1000р"), KeyboardButton("1000р+")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )
    elif step == 4:
        # Шаг 4: Удержание клиентов
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("До 10%"), KeyboardButton("10-30%")],
                [KeyboardButton("30-50%"), KeyboardButton("50%+")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )
    elif step == 5:
        # Шаг 5: Планы роста
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("Новый канал"), KeyboardButton("Улучшение текущего")],
                [KeyboardButton("Масштабирование"), KeyboardButton("Оптимизация")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )
    else:
        return ReplyKeyboardMarkup(
            [[KeyboardButton(BTN_BACK)]],
            resize_keyboard=True,
        )


def step_keyboard():
    """Общая клавиатура для шагов (только Назад)"""
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
