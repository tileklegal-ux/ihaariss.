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
BTN_AI_CHAT = "🤖 AI чат"
BTN_EXIT_CHAT = "❌ Выйти из AI-чата"

# =============================
# KEYBOARDS
# =============================

def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        [
            # 🔝 Самое важное — наверху
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


def growth_channels_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("Instagram"), KeyboardButton("TikTok")],
            [KeyboardButton("Маркетплейсы"), KeyboardButton("Сарафан")],
            [KeyboardButton(BTN_BACK)],
        ],
        resize_keyboard=True,
    )


def step_keyboard(options):
    return ReplyKeyboardMarkup(
        [[KeyboardButton(opt)] for opt in options]
        + [[KeyboardButton(BTN_BACK)]],
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
