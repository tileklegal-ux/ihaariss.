from typing import Literal, Optional, Dict, Any
from openai import OpenAI

from database.db import is_user_premium

# Инициализируем клиента один раз на модуль
client = OpenAI()

# --- Сезонная «золотая база» ниш ---

SPRING_SUMMER_NICHES = [
    "велосипеды",
    "электросамокаты",
    "электровелосипеды",
    "уголь и брикеты",
    "теплицы",
    "инструменты для ремонта",
    "качели и скамейки для дачи",
    "игровые кресла",
    "смарт-часы",
    "чехлы и стекла для телефонов",
    "аксессуары для красоты",
    "техника для красоты",
    "мелкая бытовая техника",
    "наборы инструментов",
    "наручные часы",
    "бассейны",
    "портативные колонки",
    "видеорегистраторы",
    "мангалы",
]

AUTUMN_WINTER_NICHES = [
    "шубы, эко-шубы и парки с мехом",
    "женская обувь",
    "мужская обувь",
    "искусственные ёлки",
    "спортивная экипировка",
    "обогреватели",
    "электрокамины",
    "рециркуляторы",
    "техника для уборки снега",
    "новогодние аксессуары и декор",
    "матрасы",
    "мебель для дома",
    "детские игровые комплексы",
    "автоинструменты и автоаксессуары",
    "товары для салонов красоты",
    "музыкальные инструменты",
]

ALL_YEAR_NICHES = list(dict.fromkeys(SPRING_SUMMER_NICHES + AUTUMN_WINTER_NICHES))

SeasonType = Literal["spring_summer", "autumn_winter", "all_year", "unknown"]
BusinessFormatType = Literal["marketplace", "social", "offline", "self_employed"]
BudgetLevelType = Literal["low", "medium", "high"]
ExperienceLevelType = Literal["no_experience", "some_experience", "pro"]
AudienceType = Literal["women", "men", "parents_kids", "autolovers", "universal"]


# ---------------------------------------------------------------------
# Маппинг сезонности
# ---------------------------------------------------------------------
def _map_season_to_internal(season_button: str) -> SeasonType:
    t = season_button.lower()
    if "весна" in t or "лето" in t:
        return "spring_summer"
    if "осень" in t or "зима" in t:
        return "autumn_winter"
    if "круглый" in t:
        return "all_year"
    return "unknown"


def _get_season_context(season: SeasonType) -> str:
    if season == "spring_summer":
        niches = SPRING_SUMMER_NICHES
        label = "Весна–Лето"
    elif season == "autumn_winter":
        niches = AUTUMN_WINTER_NICHES
        label = "Осень–Зима"
    elif season == "all_year":
        niches = ALL_YEAR_NICHES
        label = "Круглый год (комбинация сезонных ниш)"
    else:
        niches = ALL_YEAR_NICHES
        label = "Сезон не определён (комбинированный режим)"

    niches_bullets = "\n".join(f"- {n}" for n in niches)
    return f"""Сезон: {label}

Опорный список ниш с высоким спросом в этот период:

{niches_bullets}
"""


def _get_season_label(season: SeasonType) -> str:
    if season == "spring_summer":
        return "Весна–Лето"
    if season == "autumn_winter":
        return "Осень–Зима"
    if season == "all_year":
        return "Круглый год"
    return "Не указан"


# ---------------------------------------------------------------------
# Описание параметров
# ---------------------------------------------------------------------
def _describe_business_format(business_format: BusinessFormatType) -> str:
    if business_format == "marketplace":
        return "Маркетплейс (Kaspi / Ozon / Wildberries)"
    if business_format == "social":
        return "Instagram / Telegram-магазин"
    if business_format == "offline":
        return "Оффлайн точка"
    return "Самозанятый / мелкая торговля"


def _describe_budget_level(budget: BudgetLevelType) -> str:
    if budget == "low":
        return "Низкий бюджет"
    if budget == "medium":
        return "Средний бюджет"
    return "Высокий бюджет"


def _describe_experience_level(experience: ExperienceLevelType) -> str:
    if experience == "no_experience":
        return "Нет опыта"
    if experience == "some_experience":
        return "Базовый опыт"
    return "Опытный предприниматель"


def _describe_audience(audience: AudienceType) -> str:
    if audience == "women":
        return "Женская аудитория"
    if audience == "men":
        return "Мужская аудитория"
    if audience == "parents_kids":
        return "Родители и дети"
    if audience == "autolovers":
        return "Автовладельцы"
    return "Универсальные товары"


# ---------------------------------------------------------------------
# PROMPT — Base (без Markdown, только текст + эмодзи)
# ---------------------------------------------------------------------
def _build_base_prompt(
    season: SeasonType,
    business_format: BusinessFormatType,
    budget: BudgetLevelType,
    experience: ExperienceLevelType,
    audience: AudienceType,
    interests: Optional[str],
) -> str:
    season_context = _get_season_context(season)

    return f"""
Ты — Artbazar AI.

Твоя задача: сформировать 3–5 ниш под параметры пользователя.
Ответ должен быть удобен для чтения в Telegram, БЕЗ Markdown-разметки.
НЕЛЬЗЯ использовать символы *, _, #, ~, `, а также конструкции вроде *текст*.
Используй только обычный текст, нумерованные списки, переносы строк и эмодзи.

Сезонный контекст:
{season_context}

Параметры пользователя:
- Формат: {_describe_business_format(business_format)}
- Бюджет: {_describe_budget_level(budget)}
- Опыт: {_describe_experience_level(experience)}
- Аудитория: {_describe_audience(audience)}
- Интересы: {interests}

Формат ответа:

Подбор ниши (Base)

Возможные ниши:

1) Название ниши 1
Краткое описание ниши в 1–2 предложениях.

2) Название ниши 2
Краткое описание.

3) Название ниши 3
Краткое описание.

4) Название ниши 4 (по желанию)
Краткое описание.

Вывод:
Один короткий совет, на какой нише лучше сфокусироваться в первую очередь.
"""


# ---------------------------------------------------------------------
# PROMPT — Premium (Variant C, BI-досье, без Markdown)
# ---------------------------------------------------------------------
def _build_premium_prompt(
    season: SeasonType,
    business_format: BusinessFormatType,
    budget: BudgetLevelType,
    experience: ExperienceLevelType,
    audience: AudienceType,
    interests: Optional[str],
) -> str:
    season_context = _get_season_context(season)
    season_label = _get_season_label(season)

    return f"""
Ты — Artbazar AI, эксперт по BI-аналитике для предпринимателей Казахстана и Кыргызстана.

Сформируй Premium-отчёт формата Business Intelligence Dossier (Variant C).
Текст должен быть читабельным в Telegram, БЕЗ Markdown-разметки.
НЕЛЬЗЯ использовать символы *, _, #, ~, `, а также конструкции вроде *заголовок*.
Используй заголовки через эмодзи и обычный текст.

Сезонный контекст:
{season_context}

Структура ответа:

1. Заголовок отчёта
Напиши строку:
Artbazar Premium Report

2. Профиль пользователя
Блок с перечислением параметров:
Сезон: {season_label}
Формат: {_describe_business_format(business_format)}
Бюджет: {_describe_budget_level(budget)}
Опыт: {_describe_experience_level(experience)}
Аудитория: {_describe_audience(audience)}
Интересы: {interests}

3. Обзор рынка
Краткий анализ с учётом параметров пользователя:
- общий спрос;
- уровень конкуренции;
- сезонные влияния;
- примерные ценовые коридоры.
Не более 4–5 предложений.

4. Лучшие ниши (рейтинг 1–3)
Перечисли от 2 до 3 ниш. Для каждой ниши укажи:

1) Название ниши
   KPI: спрос, маржа, конкуренция (очень коротко, в одном предложении).
   Почему ниша подходит именно этому пользователю.
   На что обратить внимание при запуске.

Каждую нишу отделяй пустой строкой.

5. Риски
Перечисли реальные риски:
- рыночные;
- финансовые;
- логистические;
- операционные.
Не более 4–5 пунктов, без воды.

6. AI-вывод
Сформулируй итог:
- какая ниша номер один для старта;
- почему именно она;
- краткий прогноз результата (в качественных формулировках).
Один абзац.

7. Checklist на 7 дней
Дай список из 5 практических шагов:
1) ...
2) ...
3) ...
4) ...
5) ...

Каждый шаг должен быть конкретным и понятным предпринимателю.
Не используй общие фразы уровня "изучить рынок", давай прикладные действия.
Не добавляй ничего сверх этой структуры.
"""


# ---------------------------------------------------------------------
# Вызов OpenAI
# ---------------------------------------------------------------------
def _call_openai(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.7,
        messages=[
            {
                "role": "system",
                "content": "Ты — Artbazar AI, помогаешь предпринимателям Казахстана и Кыргызстана принимать решения по нишам и товарам.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content.strip()


# ---------------------------------------------------------------------
# Основная функция генерации
# ---------------------------------------------------------------------
def generate_niche_recommendations(
    user_id: int,
    season: SeasonType,
    business_format: BusinessFormatType,
    budget: BudgetLevelType,
    experience: ExperienceLevelType,
    audience: AudienceType,
    interests: Optional[str],
) -> str:
    if is_user_premium(user_id):
        prompt = _build_premium_prompt(
            season, business_format, budget, experience, audience, interests
        )
    else:
        prompt = _build_base_prompt(
            season, business_format, budget, experience, audience, interests
        )

    return _call_openai(prompt)


# ---------------------------------------------------------------------
# Маппинг из Telegram → внутренние значения
# ---------------------------------------------------------------------
def map_telegram_answers_to_internal(
    season_text: str,
    business_format_text: str,
    budget_text: str,
    experience_text: str,
    audience_text: str,
) -> Dict[str, Any]:
    season = _map_season_to_internal(season_text)

    # Формат
    bf = business_format_text.lower()
    if "kaspi" in bf or "ozon" in bf or "wb" in bf or "market" in bf:
        business_format: BusinessFormatType = "marketplace"
    elif "instagram" in bf or "telegram" in bf or "соц" in bf:
        business_format = "social"
    elif "офф" in bf or "офлайн" in bf or "павильон" in bf:
        business_format = "offline"
    else:
        business_format = "self_employed"

    # Бюджет
    bd = budget_text.lower()
    if "низ" in bd:
        budget: BudgetLevelType = "low"
    elif "сред" in bd:
        budget = "medium"
    elif "выс" in bd:
        budget = "high"
    else:
        budget = "medium"

    # Опыт
    ex = experience_text.lower()
    if "нет" in ex or "нович" in ex:
        experience: ExperienceLevelType = "no_experience"
    elif "баз" in ex or ("есть" in ex and "опыт" in ex):
        experience = "some_experience"
    else:
        experience = "pro"

    # Аудитория
    aud = audience_text.lower()
    if "жен" in aud:
        audience: AudienceType = "women"
    elif "муж" in aud:
        audience = "men"
    elif "род" in aud or "дет" in aud:
        audience = "parents_kids"
    elif "авто" in aud:
        audience = "autolovers"
    else:
        audience = "universal"

    return {
        "season": season,
        "business_format": business_format,
        "budget": budget,
        "experience": experience,
        "audience": audience,
    }
