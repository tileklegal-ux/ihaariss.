# -*- coding: utf-8 -*-

import logging
from openai import AsyncOpenAI
from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

_client = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    return _client


async def ask_openai(prompt: str) -> str:
    """
    ЕДИНСТВЕННАЯ точка вызова OpenAI.
    Возвращает текст или нейтральную заглушку.
    """
    try:
        client = get_client()
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты спокойный аналитик. "
                        "Запрещено: советы, обещания, прогнозы. "
                        "Формат: наблюдения / риски / варианты проверки. "
                        "Всегда добавляй фразу: "
                        "«это ориентир, а не рекомендация; решение за пользователем»."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.exception("OpenAI error")
        return (
            "Сейчас невозможно получить аналитический разбор.\n"
            "Это ориентир, а не рекомендация; решение за пользователем."
        )
