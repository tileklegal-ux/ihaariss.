
# handlers/export.py

from telegram import Update
from telegram.ext import ContextTypes

from generators.pdf_generator import generate_pdf
from generators.excel_generator import generate_excel


# =====================================
# EXPORT PDF
# =====================================

async def export_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Экспорт данных пользователя в PDF
    """
    user_id = update.effective_user.id

    # данные берём из user_data (они уже там есть)
    data = context.user_data.get("export_data")

    if not data:
        await update.message.reply_text(
            "❌ Нет данных для экспорта"
        )
        return

    pdf_path = generate_pdf(
        user_id=user_id,
        data=data,
    )

    await update.message.reply_document(
        document=open(pdf_path, "rb"),
        filename="report.pdf",
    )


# =====================================
# EXPORT EXCEL
# =====================================

async def export_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Экспорт данных пользователя в Excel
    """
    user_id = update.effective_user.id

    data = context.user_data.get("export_data")

    if not data:
        await update.message.reply_text(
            "❌ Нет данных для экспорта"
        )
        return

    excel_path = generate_excel(
        user_id=user_id,
        data=data,
    )

    await update.message.reply_document(
        document=open(excel_path, "rb"),
        filename="report.xlsx",
    )
