# -*- coding: utf-8 -*-

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import ContextTypes


# ==================================================
# 📄 ЮРИДИЧЕСКИЕ ДОКУМЕНТЫ — ССЫЛКИ
# ==================================================

DOC_PRIVACY = "https://www.notion.so/2c901cd07aa780598f3edb433a04be57?source=copy_link"
DOC_TERMS = "https://www.notion.so/2c901cd07aa780568e40d5b82ca69420?source=copy_link"
DOC_CONSENT = "https://www.notion.so/2c901cd07aa780e4bf4fde3930c5129d?source=copy_link"
DOC_DISCLAIMER = "https://www.notion.so/2c901cd07aa780baa932ee8050f56db6?source=copy_link"
DOC_OFFER = "https://www.notion.so/Premium-2c901cd07aa7808b85ddec9d8019e742?source=copy_link"


# ==================================================
# 📄 ЭКРАН «ДОКУМЕНТЫ»
# ==================================================

async def on_documents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📄 *Юридические документы ArtBazar AI*\n\n"
        "Используя сервис ArtBazar AI, вы подтверждаете, что ознакомились "
        "и соглашаетесь с условиями, указанными в следующих документах:\n"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📑 Политика конфиденциальности", url=DOC_PRIVACY)],
            [InlineKeyboardButton("📘 Пользовательское соглашение", url=DOC_TERMS)],
            [InlineKeyboardButton("🗂 Согласие на обработку данных", url=DOC_CONSENT)],
            [InlineKeyboardButton("⚠️ Отказ от ответственности", url=DOC_DISCLAIMER)],
            [InlineKeyboardButton("💳 Публичная оферта (Premium)", url=DOC_OFFER)],
        ]
    )

    await update.message.reply_text(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
