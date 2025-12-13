import logging
from openai import OpenAI
from database.db import is_user_premium
from services.history_service import save_analysis_history

logger = logging.getLogger(__name__)

client = OpenAI()

# =========================
# BASE PROMPT
# =========================
def build_base_prompt(data: dict) -> str:
    return (
        "Вы — Artbazar AI.\n"
        "Ниже данные товара. Сформируйте простой, понятный и честный анализ.\n\n"
        f"Ниша: {data['niche']}\n"
        f"Товар: {data['product']}\n"
        f"Закупочная цена: {data['price_buy']}\n"
        f"Цена продажи: {data['price_sell']}\n"
        f"Комиссия: {data['commission_percent']}%\n"
        f"Логистика: {data['logistics']}\n"
        f"Доставка: {data['delivery']}\n"
        f"Маркетинг: {data['marketing']}\n"
        f"Прочие расходы: {data['other']}\n"
        f"Конкуренция: {data['competition']}\n"
        f"Сезонность: {data['seasonality']}\n"
        f"Риски: {data['risks']}\n\n"
        "Сформируйте:\n"
        "1) Короткий разбор расходов.\n"
        "2) Прогноз маржи.\n"
        "3) Основные риски.\n"
        "4) Рекомендации по улучшению.\n"
    )


# =========================
# PREMIUM PROMPT
# =========================
def build_premium_prompt(data: dict) -> str:
    return (
        "Вы — Artbazar AI Premium. Дайте глубокую аналитику.\n\n"
        "Используйте структуру Variant C.\n\n"
        f"Ниша: {data['niche']}\n"
        f"Товар: {data['product']}\n"
        f"Закупочная цена: {data['price_buy']}\n"
        f"Цена продажи: {data['price_sell']}\n"
        f"Комиссия: {data['commission_percent']}%\n"
        f"Логистика: {data['logistics']}\n"
        f"Доставка: {data['delivery']}\n"
        f"Маркетинг: {data['marketing']}\n"
        f"Прочие расходы: {data['other']}\n"
        f"Конкуренция: {data['competition']}\n"
        f"Сезонность: {data['seasonality']}\n"
        f"Риски: {data['risks']}\n\n"
        "Структура:\n"
        "📊 Полный разбор товара\n"
        "💰 Финансовый расчёт\n"
        "📈 Потенциал товара\n"
        "⚠ Риски и сезонность\n"
        "🧠 AI-выводы\n"
        "🔧 Рекомендации на 7 дней\n"
    )


# =========================
# Запрос к OpenAI
# =========================
def call_openai(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.4,
            messages=[
                {"role": "system", "content": "Вы — аналитик Artbazar AI."},
                {"role": "user", "content": prompt},
            ]
        )

        text = response.choices[0].message.content.strip()
        return text.replace("*", "")  # убираем markdown-символы телеграма

    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return "Ошибка при обращении к AI. Попробуйте позже."


# =========================
# Финальная функция анализа
# =========================
async def finalize_analysis(update, context, data: dict):

    user_id = update.effective_user.id
    premium = is_user_premium(user_id)

    if premium:
        prompt = build_premium_prompt(data)
    else:
        prompt = build_base_prompt(data)

    await update.message.reply_text("AI анализирует данные… ⚙️")

    result = call_openai(prompt)

    # сохраняем в историю
    save_analysis_history(user_id, data, result)

    await update.message.reply_text(result)
