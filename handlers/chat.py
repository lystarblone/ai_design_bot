import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from models import Database
from states import HumanDesignStates
from ai import query_ai

logger = logging.getLogger(__name__)

router = Router()

db = Database()

@router.message(Command("chat"))
async def cmd_chat(message: Message, state: FSMContext):
    user_id = message.from_user.id
    language = db.get_language(user_id)
    
    await state.set_state(HumanDesignStates.MAIN_CONVERSATION)
    response = (
        "💬 Задай свой вопрос по Human Design, и я отвечу! 😊"
        if language == "Русский"
        else "💬 Ask your question about Human Design, and I'll answer! 😊"
    )
    await message.answer(response)
    logger.info(f"Пользователь ID {user_id} начал диалог с /chat")

@router.message(HumanDesignStates.MAIN_CONVERSATION, ~Command(commands=["start", "chat", "reset", "help"]))
async def process_message(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text.strip()
    language = db.get_language(user_id)
    
    data = await state.get_data()
    conversation_history = data.get("conversation_history", [])
    
    try:
        response = await query_ai(text, language, conversation_history)
        
        conversation_history.append({"role": "user", "content": text})
        conversation_history.append({"role": "assistant", "content": response})
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]
        await state.update_data(conversation_history=conversation_history)
        
        await message.answer(f"{response}")
        logger.info(f"Ответ для user_id {user_id}: {response[:100]}...")
        
        if any(phrase in text.lower() for phrase in ["пока", "до свидания", "bye", "goodbye"]):
            goodbye_message = "До встречи! 😊" if language == "Русский" else "See you later! 😊"
            await message.answer(goodbye_message)
            await state.clear()
            logger.info(f"Пользователь ID {user_id} завершил диалог")
            
    except Exception as e:
        error_message = (
            f"❌ Ошибка при обработке сообщения: {str(e)}"
            if language == "Русский"
            else f"❌ Error processing message: {str(e)}"
        )
        await message.answer(error_message)
        await state.clear()
        logger.error(f"Ошибка обработки сообщения для user_id {user_id}: {str(e)}")