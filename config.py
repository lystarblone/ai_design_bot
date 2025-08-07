import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    AI_API_KEY = os.getenv("AI_API_KEY")
    DB_PATH = "bot_database.db"

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не установлен в .env")
    if not AI_API_KEY:
        raise ValueError("OPENAI_API_KEY не установлен в .env")

config = Config()