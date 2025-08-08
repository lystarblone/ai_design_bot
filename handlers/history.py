import logging
import json
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from models import Database, ChatHistory
from states import HumanDesignStates

logger = logging.getLogger(__name__)

router = Router()

db = Database()

@router.message(Command("history"))
async def cmd_history(message: Message, state: FSMContext):
    user_id = message.from_user.id
    language = db.get_language(user_id)
    
    with db.Session() as session:
        try:
            chats = session.query(ChatHistory).filter_by(user_id=user_id).order_by(ChatHistory.saved_at.desc()).all()
            if not chats:
                response = (
                    "У вас нет сохраненных чатов. Начни новый диалог с /chat! 😊"
                    if language == "Русский"
                    else "You have no saved chats. Start a new conversation with /chat! 😊"
                )
                await message.answer(response)
                logger.info(f"Пользователь ID {user_id} запросил историю чатов, но она пуста")
                return

            keyboard = ReplyKeyboardMarkup(
                resize_keyboard=True,
                one_time_keyboard=True,
                keyboard=[[KeyboardButton(text=f"{chat.chat_name} ({chat.saved_at.strftime('%Y-%m-%d %H:%M:%S')} UTC)")] for chat in chats]
            )
            response = (
                "Выберите чат для продолжения:"
                if language == "Русский"
                else "Select a chat to continue:"
            )
            await state.set_state(HumanDesignStates.SELECT_CHAT)
            await message.answer(response, reply_markup=keyboard)
            logger.info(f"Пользователь ID {user_id} запросил историю чатов")
        except Exception as e:
            response = (
                f"❌ Ошибка при получении истории: {str(e)}"
                if language == "Русский"
                else f"❌ Error retrieving history: {str(e)}"
            )
            await message.answer(response)
            logger.error(f"Ошибка получения истории чатов для user_id {user_id}: {str(e)}")

@router.message(HumanDesignStates.SELECT_CHAT)
async def process_chat_selection(message: Message, state: FSMContext):
    user_id = message.from_user.id
    language = db.get_language(user_id)
    selected_chat = message.text.strip()

    with db.Session() as session:
        try:
            chat_name = selected_chat.split(" (")[0]
            chat = session.query(ChatHistory).filter_by(user_id=user_id, chat_name=chat_name).first()
            if not chat:
                response = (
                    "Выбранный чат не найден. Попробуйте снова или начните новый диалог с /chat."
                    if language == "Русский"
                    else "Selected chat not found. Try again or start a new conversation with /chat."
                )
                await message.answer(response, reply_markup=ReplyKeyboardRemove())
                logger.warning(f"Пользователь ID {user_id} выбрал несуществующий чат: {selected_chat}")
                return

            conversation_history = json.loads(chat.conversation)
            await state.update_data(conversation_history=conversation_history)
            await state.set_state(HumanDesignStates.MAIN_CONVERSATION)
            response = (
                f"Чат '{chat.chat_name}' загружен! Задай свой вопрос по Human Design! 😊"
                if language == "Русский"
                else f"Chat '{chat.chat_name}' loaded! Ask your question about Human Design! 😊"
            )
            await message.answer(response, reply_markup=ReplyKeyboardRemove())
            logger.info(f"Пользователь ID {user_id} загрузил чат '{chat.chat_name}'")
        except Exception as e:
            response = (
                f"❌ Ошибка при загрузке чата: {str(e)}"
                if language == "Русский"
                else f"❌ Error loading chat: {str(e)}"
            )
            await message.answer(response, reply_markup=ReplyKeyboardRemove())
            logger.error(f"Ошибка загрузки чата для user_id {user_id}: {str(e)}")