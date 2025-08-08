import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from models import Database

logger = logging.getLogger(__name__)

router = Router()

db = Database()

@router.message(Command("help"))
async def cmd_help(message: Message):
    user_id = message.from_user.id
    language = db.get_language(user_id)
    
    response = (
        "📖 Я @DesignAssistantBot, эксперт по Human Design!\n"
        "Доступные команды:\n"
        "/start\n"
        "/chat\n"
        "/reset\n"
        "/help\n\n"
        "Я отвечаю только на вопросы по Human Design (типы, центры, профили, авторитеты, ворота, линии, каналы)."
        if language == "Русский"
        else
        "📖 I'm @DesignAssistantBot, a Human Design expert!\n"
        "Available commands:\n"
        "/start\n"
        "/chat\n"
        "/reset\n"
        "/help\n\n"
        "I only answer questions about Human Design (types, centers, profiles, authority, gates, lines, channels)."
    )
    await message.answer(response)
    logger.info(f"Пользователь ID {user_id} запросил справку")