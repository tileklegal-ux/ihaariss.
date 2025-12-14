# -*- coding: utf-8 -*-
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from handlers.user_helpers import get_results_summary
from handlers.user_keyboards import (
    main_menu_keyboard,
    BTN_BACK,
)
from handlers.user_texts import t

from services.export_excel import build_excel_report
from services.export_pdf import build_pdf_report


# ==================================================
# 👤 ЛИЧНЫЙ КАБИНЕТ
# ==================================================

async def on_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    is_premium = user_data.get("is_premium", False)
    history = user_data.get("history", [])
    lang = user_data.get("lang", "ru")

    # ------------------------------
    # 🆓 FREE
    # ------------------------------
    if not is_premium:
        summary = get_results_summary(context)

        lines = [
            t(lang, "profile_free"),
            "",
            "Что уже сделано:",
        ]

        if not summary:
            lines.append("— пока нет завершённых анализов")
        else:
            for k, v in summary.items():
                lines.append(f"— {k}: {v}")

        lines.extend([
            "",
            "Ты можешь анализировать идеи и риски.",
            "В Premium доступны отчёты, история и выгрузка в PDF / Excel.",
        ])

        await update.message.reply_text(
            "\n".join(lines),
            reply_markup=ReplyKeyboardMarkup(
                [
                    [KeyboardButton("❤️ Что даёт Premium")],
                    [KeyboardButton(BTN_BACK)],
                ],
                resize_keyboard=True,
            ),
        )
        return

    # ------------------------------
    # ⭐ PREMIUM
    # ------------------------------
    lines = [
        t(lang, "profile_premium"),
        "",
        "Последние результаты:",
    ]

    if not history:
        lines.append("— нет данных для отчётов")
    else:
        for item in history[-5:]:
            tpe = item.get("type", "—")
            d = item.get("date", "")
            s = item.get("summary", "")
            lines.append(f"• {tpe} | {d} | {s}")

    lines.extend([
        "",
        "Экспорт:",
    ])

    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=ReplyKeyboardMarkup(
            [
                [KeyboardButton("📄 Скачать PDF"), KeyboardButton("📊 Скачать Excel")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        ),
    )


# ==================================================
# 📊 EXCEL EXPORT
# ==================================================

async def on_export_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history = context.user_data.get("history", [])
    lang = context.user_data.get("lang", "ru")

    if not history:
        await update.message.reply_text(
            t(lang, "no_data_for_export"),
            reply_markup=main_menu_keyboard(),
        )
        return

    stream = build_excel_report(history)

    await update.message.reply_document(
        document=stream,
        filename="artbazar_report.xlsx",
        caption="📊 Excel",
        reply_markup=main_menu_keyboard(),
    )


# ==================================================
# 📄 PDF EXPORT
# ==================================================

async def on_export_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history = context.user_data.get("history", [])
    lang = context.user_data.get("lang", "ru")

    if not history:
        await update.message.reply_text(
            t(lang, "no_data_for_export"),
            reply_markup=main_menu_keyboard(),
        )
        return

    stream = build_pdf_report(history)

    await update.message.reply_document(
        document=stream,
        filename="artbazar_report.pdf",
        caption="📄 PDF",
        reply_markup=main_menu_keyboard(),
    )
