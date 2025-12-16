# handlers/export.py

from io import BytesIO
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from services.pdf_generator import generate_simple_pdf
from services.excel_generator import generate_excel_report


async def export_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Простой экспорт в PDF.
    Берём текст из context.user_data["export_text"] если есть, иначе дефолт.
    """
    title = context.user_data.get("pdf_title", "Отчёт")
    content = context.user_data.get("export_text", "Данных пока нет. Сначала сформируй отчёт, потом экспортируй.")
    filename = "report.pdf"

    file_path = generate_simple_pdf(filename=filename, title=title, content=content)

    with open(file_path, "rb") as f:
        await update.message.reply_document(document=f, filename=filename)


async def export_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Простой экспорт в Excel.
    Берём headers/rows из context.user_data если есть, иначе дефолт.
    """
    headers = context.user_data.get("excel_headers", ["Колонка 1", "Колонка 2"])
    rows = context.user_data.get("excel_rows", [["Пример", 123]])

    buffer: BytesIO = generate_excel_report(headers=headers, rows=rows)
    await update.message.reply_document(document=buffer, filename="report.xlsx")


def register_export_handlers(application):
    """
    Чтобы main.py мог подключить экспорт командами.
    """
    application.add_handler(CommandHandler("export_pdf", export_pdf))
    application.add_handler(CommandHandler("export_excel", export_excel))
