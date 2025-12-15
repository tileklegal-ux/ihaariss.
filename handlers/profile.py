# -*- coding: utf-8 -*-

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import ContextTypes

from handlers.user_helpers import get_results_summary
from handlers.user_keyboards import BTN_BACK, BTN_DOCS
from handlers.user_texts import t

from services.export_excel import build_excel_report
from services.export_pdf import build_pdf_report
from services.premium_checker import is_premium_user


# ==================================================
# 👤 ЛИЧНЫЙ КАБИНЕТ
# ==================================================

async def on_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "ru")
    premium = bool(is_premium_user(user_id))
    history = context.user_data.get("history", [])

    # ------------------------------
    # 🆓 FREE
    # ------------------------------
    if not premium:
        summary = get_results_summary(context)

        lines = [
            "👤 Личный кабинет",
            "",
            "Тариф: FREE",
            "",
            "Что уже сделано:",
        ]

        if not summary:
            lines.append("— пока нет завершённых анализов")
        else:
            for k, v in summary.items():
                lines.append(f"— {k}: {v}")

        lines += [
            "",
            "В Premium доступно:",
            "• история результатов",
            "• экспорт PDF и Excel",
        ]

        keyboard = ReplyKeyboardMarkup(
            [
                [KeyboardButton("❤️ Что даёт Premium")],
                [KeyboardButton(BTN_DOCS)],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )

        await update.message.reply_text(
            "\n".join(lines),
            reply_markup=keyboard,
        )
        return

    # ------------------------------
    # ⭐ PREMIUM
    # ------------------------------
    lines = [
        "👤 Личный кабинет",
        "",
        "Тариф: PREMIUM ⭐",
        "",
        "Последние результаты:",
    ]

    if not history:
        lines.append("— пока нет данных")
    else:
        for item in history[-5:]:
            lines.append(
                f"• {item.get('type','')} | {item.get('date','')} | {item.get('summary','')}"
            )

    lines += [
        "",
        "📤 Экспорт отчётов:",
        "• PDF — краткий отчёт",
        "• Excel — таблица с данными",
    ]

    keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton("📄 Скачать PDF"), KeyboardButton("📊 Скачать Excel")],
            [KeyboardButton(BTN_DOCS)],
            [KeyboardButton(BTN_BACK)],
        ],
        resize_keyboard=True,
    )

    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=keyboard,
    )


# ==================================================
# 📊 EXCEL EXPORT
# ==================================================

async def on_export_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_premium_user(update.effective_user.id):
        return

    history = context.user_data.get("history", [])
    if not history:
        return

    stream = build_excel_report(history)
    await update.message.reply_document(
        document=stream,
        filename="artbazar_report.xlsx",
    )


# ==================================================
# 📄 PDF EXPORT
# ==================================================

async def on_export_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_premium_user(update.effective_user.id):
        return

    history = context.user_data.get("history", [])
    if not history:
        return

    stream = build_pdf_report(history)
    await update.message.reply_document(
        document=stream,
        filename="artbazar_report.pdf",
    )
