import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def ask_openai(prompt: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Ты бизнес-ассистент для предпринимателей СНГ."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.6,
    )

    return response.choices[0].message.content.strip()
