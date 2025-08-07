import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from models import Database

logger = logging.getLogger(__name__)

router = Router()

db = Database()

@router.message(Command("reset"))
async def cmd_reset(message: Message, state: FSMContext):
    user_id = message.from_user.id
    language = db.get_language(user_id)
    
    await state.clear()
    response = (
        "🔄 Контекст диалога сброшен. Начни новый диалог с /chat."
        if language == "Русский"
        else "🔄 Conversation context reset. Start a new conversation with /chat."
    )
    await message.answer(response)
    logger.info(f"Контекст сброшен для user_id {user_id}")