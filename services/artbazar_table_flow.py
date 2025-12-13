from __future__ import annotations

from typing import Any, Dict, Optional

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, ContextTypes

# Одно состояние для многошагового диалога
ARTBAZAR_TABLE_STATE = 100

# Последовательность вопросов
FIELDS_FLOW = [
    {"key": "niche", "label": "Ниша", "question": "📌 Шаг 1/12\nНапишите нишу:", "type": "text"},
    {"key": "product", "label": "Товар", "question": "📌 Шаг 2/12\nНапишите товар:", "type": "text"},
    {"key": "purchase_price", "label": "Закупочная цена", "question": "💰 Шаг 3/12\nЗакупочная цена за единицу:", "type": "number"},
    {"key": "sale_price", "label": "Цена продажи", "question": "💰 Шаг 4/12\nЦена продажи за единицу:", "type": "number"},
    {"key": "commission_percent", "label": "Комиссия (%)", "question": "💼 Шаг 5/12\nКомиссия площадки (%):", "type": "number"},
    {"key": "logistics", "label": "Логистика", "question": "🚚 Шаг 6/12\nЛогистика на единицу товара:", "type": "number"},
    {"key": "delivery", "label": "Доставка", "question": "📦 Шаг 7/12\nДоставка до клиента:", "type": "number"},
    {"key": "marketing", "label": "Маркетинг", "question": "📣 Шаг 8/12\nРасходы на маркетинг:", "type": "number"},
    {"key": "other_expenses", "label": "Прочие расходы", "question": "📎 Шаг 9/12\nПрочие расходы:", "type": "number"},
    {"key": "competition", "label": "Конкуренция", "question": "⚔ Шаг 10/12\nОпишите конкуренцию:", "type": "text"},
    {"key": "seasonality", "label": "Сезонность", "question": "📆 Шаг 11/12\nЕсть ли сезонность?", "type": "text"},
    {"key": "risks", "label": "Риски", "question": "⚠ Шаг 12/12\nОпишите ключевые риски:", "type": "text"},
]


def _parse_number(text: str) -> float:
    t = text.replace(" ", "").replace(",", ".")
    num = float(t)
    if num < 0:
        raise ValueError
    return num


# ---------------------------------------------------------
# СТАРТ ДИАЛОГА
# ---------------------------------------------------------
async def start_table_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["artbazar_table_data"] = {}
    context.user_data["artbazar_table_step"] = 0

    await update.message.reply_text(FIELDS_FLOW[0]["question"], reply_markup=ReplyKeyboardRemove())
    return ARTBAZAR_TABLE_STATE


# ---------------------------------------------------------
# ОСНОВНОЙ ОБРАБОТЧИК
# ---------------------------------------------------------
async def handle_table_flow_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    table = context.user_data.get("artbazar_table_data", {})
    step = context.user_data.get("artbazar_table_step", 0)

    # Подстраховка
    if step >= len(FIELDS_FLOW):
        return ConversationHandler.END

    field = FIELDS_FLOW[step]
    key = field["key"]

    # Валидация
    if field["type"] == "number":
        try:
            value = _parse_number(text)
        except Exception:
            await update.message.reply_text("Введите число корректно (например: 1200 или 12.5).")
            return ARTBAZAR_TABLE_STATE
        table[key] = value
    else:
        if not text:
            await update.message.reply_text("Ответ не может быть пустым.")
            return ARTBAZAR_TABLE_STATE
        table[key] = text

    # Сохранить
    context.user_data["artbazar_table_data"] = table
    step += 1
    context.user_data["artbazar_table_step"] = step

    # Следующий вопрос
    if step < len(FIELDS_FLOW):
        await update.message.reply_text(FIELDS_FLOW[step]["question"])
        return ARTBAZAR_TABLE_STATE

    # Таблица завершена
    context.user_data["artbazar_table_result"] = {
        "table_data": table
    }

    return ConversationHandler.END


# ---------------------------------------------------------
# CANCEL
# ---------------------------------------------------------
async def cancel_table_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("artbazar_table_data", None)
    context.user_data.pop("artbazar_table_step", None)
    context.user_data.pop("artbazar_table_result", None)

    await update.message.reply_text("Диалог таблицы остановлен.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# ---------------------------------------------------------
# ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ
# ---------------------------------------------------------
def get_table_result_from_context(context: ContextTypes.DEFAULT_TYPE) -> Optional[dict]:
    return context.user_data.get("artbazar_table_result")
