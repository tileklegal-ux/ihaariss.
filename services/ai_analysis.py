import os
import json
from typing import Dict, Any

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---------------------------------------------------------
#  PROMPT BUILDER
# ---------------------------------------------------------

def _build_prompt(table_data: Dict[str, Any], metrics: Dict[str, Any], raw_summary: str, is_premium: bool) -> str:
    """
    Генерация PROMPT для BASE и PREMIUM версий анализа.
    """

    base_info = {
        "table": table_data,
        "metrics": metrics,
    }

    if is_premium:
        prompt_type = "PREMIUM"
        instructions = """
Ты — эксперт по юнит-экономике, маркетплейсам и малому бизнесу в Кыргызстане и Казахстане.

Составь полный профессиональный анализ:
- подробный отчёт
- прогноз спроса, продаж и рисков
- конкурентный анализ
- рекомендации по улучшению модели
- ключевые угрозы
- вывод: стоит / есть смысл протестировать / не стоит заходить
"""
    else:
        prompt_type = "BASE"
        instructions = """
Ты — бизнес-аналитик. Составь короткий, упрощённый отчёт.
Без прогноза, без глубокого анализа рисков, без решения.

Формат ответа:
- краткое описание ситуации
- важные моменты, которые стоит учесть
"""

    prompt = f"""
Тип анализа: {prompt_type}

Данные пользователя (JSON):
{json.dumps(base_info, ensure_ascii=False, indent=2)}

Сводная таблица:
\"\"\"
{raw_summary}
\"\"\"

{instructions}

Верни строго JSON:

Если PREMIUM:
{{
  "report": "...",
  "forecast": "...",
  "risks": "...",
  "decision": "стоит заходить" | "есть смысл протестировать" | "не стоит заходить"
}}

Если BASE:
{{
  "report": "краткий текст"
}}

Не используй markdown. Не пиши ничего вне JSON.
"""

    return prompt


# ---------------------------------------------------------
#  OPENAI CALLER
# ---------------------------------------------------------

def _call_openai(prompt: str, is_premium: bool) -> Dict[str, Any]:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты бизнес-аналитик Artbazar AI."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=1000 if is_premium else 300,
        )

        content = response.choices[0].message.content
        data = json.loads(content)

        if is_premium:
            return {
                "report": data.get("report", "").strip(),
                "forecast": data.get("forecast", "").strip(),
                "risks": data.get("risks", "").strip(),
                "decision": data.get("decision", "").strip(),
            }
        else:
            return {
                "report": data.get("report", "").strip(),
                "forecast": "",
                "risks": "",
                "decision": "",
            }

    except Exception as e:
        return {
            "report": f"AI-анализ временно недоступен (ошибка: {e})",
            "forecast": "",
            "risks": "",
            "decision": "",
        }


# ---------------------------------------------------------
#  MAIN FUNCTION → used by handlers
# ---------------------------------------------------------

async def analyze_artbazar_table(
    table_data: Dict[str, Any],
    metrics: Dict[str, Any],
    raw_summary: str,
    is_premium: bool
) -> Dict[str, Any]:

    prompt = _build_prompt(table_data, metrics, raw_summary, is_premium)
    return _call_openai(prompt, is_premium)
