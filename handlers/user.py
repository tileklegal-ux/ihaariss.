import os

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from config import OWNER_ID
from services.artbazar_table_flow import start_table_flow
from services.ai_analysis import analyze_artbazar_table
from services.premium_logic import is_premium
from services.history_service import save_history, get_last_analysis
from services.export_pdf import generate_pdf
from services.export_excel import generate_excel


# -------------------------------
# Команда USER
# -------------------------------
async def user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Это пользовательский режим.\nИспользуйте /analysis чтобы начать анализ."
    )


# -------------------------------
# Основная команда анализа
# -------------------------------
async def analysis_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    # Владелец не имеет доступа к AI-анализу по ТЗ
    if user_id == OWNER_ID:
        await update.message.reply_text(
            "Владельцу недоступен AI-анализ.\nИспользуйте отдельный пользовательский аккаунт."
        )
        return

    premium = is_premium(user_id)

    # 1) собираем таблицу
    table_data, metrics, summary = await start_table_flow(update, context)

    # 2) AI-анализ
    ai_result = await analyze_artbazar_table(
        table_data=table_data,
        metrics=metrics,
        raw_summary=summary,
        is_premium=premium
    )

    # 3) сохраняем историю (только PREMIUM)
    if premium:
        save_history(user_id, table_data, ai_result)

    # 4) Формирование ответа
    if premium:
        text = f"""
🧠 *AI-анализ от Artbazar AI (PREMIUM)*

📄 *Отчёт:*
{ai_result['report']}

📊 *Прогноз:*
{ai_result['forecast']}

⚠ *Риски:*
{ai_result['risks']}

🎯 *Решение:* {ai_result['decision']}
"""
    else:
        text = f"""
🧠 *AI-анализ (BASE)*

📄 *Краткий отчёт:*
{ai_result['report']}

⚠ Для полного прогноза, рисков и инвестиционного решения — активируйте PREMIUM.
"""

    await update.message.reply_text(text, parse_mode="Markdown")

    # 5) Кнопки экспорта только если премиум
    if premium:
        await update.message.reply_html(
            "Хотите экспортировать анализ?\n"
            "<b>/export_pdf</b> — PDF отчёт\n"
            "<b>/export_excel</b> — Excel файл"
        )
    else:
        await update.message.reply_html(
            "Экспорт в PDF/Excel доступен только для <b>PREMIUM</b>."
        )


# -------------------------------
# Экспорт PDF
# -------------------------------
async def export_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_premium(user_id):
        await update.message.reply_text("PDF доступен только Premium-пользователям.")
        return

    last = get_last_analysis(user_id)
    if not last:
        await update.message.reply_text("Нет сохранённых анализов.")
        return

    table, ai = last

    file_path = f"/tmp/artbazar_{user_id}.pdf"
    generate_pdf(file_path, table, ai)

    await update.message.reply_document(open(file_path, "rb"))
    os.remove(file_path)


# -------------------------------
# Экспорт Excel
# -------------------------------
async def export_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_premium(user_id):
        await update.message.reply_text("Excel доступен только Premium-пользователям.")
        return

    last = get_last_analysis(user_id)
    if not last:
        await update.message.reply_text("Нет сохранённых анализов.")
        return

    table, ai = last

    file_path = f"/tmp/artbazar_{user_id}.xlsx"
    generate_excel(file_path, table, ai)

    await update.message.reply_document(open(file_path, "rb"))
    os.remove(file_path)


# -------------------------------
# Регистрация всех user-хендлеров
# -------------------------------
def register_user_handlers(app):

    app.add_handler(CommandHandler("user", user_command))
    app.add_handler(CommandHandler("analysis", analysis_start))
    app.add_handler(CommandHandler("analyze", analysis_start))

    # Экспорт
    app.add_handler(CommandHandler("export_pdf", export_pdf))
    app.add_handler(CommandHandler("export_excel", export_excel))
