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
        "Команды:\n"
        "/start — Начать работу\n"
        "/chat — Задать вопрос по Human Design\n"
        "/reset — Сбросить контекст диалога\n"
        "/help — Показать это сообщение\n\n"
        "Я отвечаю только на вопросы по Human Design (типы, центры, профили, авторитеты, ворота, линии, каналы)."
        if language == "Русский"
        else
        "📖 I'm @DesignAssistantBot, a Human Design expert!\n"
        "Commands:\n"
        "/start — Start the bot\n"
        "/chat — Ask a question about Human Design\n"
        "/reset — Reset conversation context\n"
        "/help — Show this message\n\n"
        "I only answer questions about Human Design (types, centers, profiles, authority, gates, lines, channels)."
    )
    await message.answer(response)
    logger.info(f"Пользователь ID {user_id} запросил справку")