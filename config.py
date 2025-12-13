import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# PostgreSQL (Railway) Database URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Жёсткие ID из ТЗ
OWNER_ID = 1974482384
MANAGER_ID = 571499876
