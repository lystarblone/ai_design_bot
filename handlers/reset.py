import logging
import json
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from models import Database
from states import HumanDesignStates
from keyboards import get_save_chat_keyboard

logger = logging.getLogger(__name__)

router = Router()

db = Database()

@router.message(Command("reset"))
async def cmd_reset(message: Message, state: FSMContext):
    user_id = message.from_user.id
    language = db.get_language(user_id)
    
    response = (
        "Хотите сохранить текущий чат перед сбросом контекста? 📜"
        if language == "Русский"
        else "Would you like to save the current chat before resetting the context? 📜"
    )
    
    await state.set_state(HumanDesignStates.CONFIRM_SAVE_CHAT)
    await message.answer(response, reply_markup=get_save_chat_keyboard(language))
    logger.info(f"Пользователь ID {user_id} запросил сброс контекста, ожидается подтверждение сохранения")

@router.message(HumanDesignStates.CONFIRM_SAVE_CHAT)
async def process_save_confirmation(message: Message, state: FSMContext):
    user_id = message.from_user.id
    language = db.get_language(user_id)
    choice = message.text.strip().lower()

    if choice not in ["да", "yes", "нет", "no"]:
        response = (
            "Пожалуйста, выберите 'Да' или 'Нет'."
            if language == "Русский"
            else "Please select 'Yes' or 'No'."
        )
        await message.answer(response, reply_markup=get_save_chat_keyboard(language))
        logger.warning(f"Некорректный выбор сохранения от user_id {user_id}: {choice}")
        return

    if choice in ["да", "yes"]:
        response = (
            "Пожалуйста, введите название для вашего чата."
            if language == "Русский"
            else "Please enter a name for your chat."
        )
        await state.set_state(HumanDesignStates.NAME_CHAT)
        await message.answer(response, reply_markup=ReplyKeyboardRemove())
        logger.info(f"Пользователь ID {user_id} подтвердил сохранение, ожидается ввод названия чата")
    else:
        await state.clear()
        await state.set_state(HumanDesignStates.MAIN_CONVERSATION)
        response = (
            "Чат не сохранен. Контекст сброшен. 😊"
            if language == "Русский"
            else "Chat not saved. Context reset. 😊"
        )
        await message.answer(response, reply_markup=ReplyKeyboardRemove())
        logger.info(f"Контекст сброшен для user_id {user_id}, чат не сохранен")

@router.message(HumanDesignStates.NAME_CHAT)
async def process_chat_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    language = db.get_language(user_id)
    chat_name = message.text.strip()

    if not chat_name or len(chat_name) > 100:
        response = (
            "Название чата должно быть не пустым и не длиннее 100 символов. Попробуйте снова."
            if language == "Русский"
            else "Chat name must not be empty and should be less than 100 characters. Try again."
        )
        await message.answer(response)
        logger.warning(f"Некорректное название чата от user_id {user_id}: {chat_name}")
        return

    data = await state.get_data()
    conversation_history = data.get("conversation_history", [])
    
    if conversation_history:
        db.save_conversation(user_id, chat_name, json.dumps(conversation_history))
        response = (
            f"Чат '{chat_name}' сохранен! Задай свой вопрос по Human Design! 😊"
            if language == "Русский"
            else f"Chat '{chat_name}' saved! Ask your question about Human Design! 😊"
        )
    else:
        response = (
            "История чата пуста, ничего не сохранено. Задай свой вопрос по Human Design! 😊"
            if language == "Русский"
            else "Chat history is empty, nothing saved. Ask your question about Human Design! 😊"
        )

    await state.clear()
    await state.set_state(HumanDesignStates.MAIN_CONVERSATION)
    await message.answer(response, reply_markup=ReplyKeyboardRemove())
    logger.info(f"Контекст сброшен для user_id {user_id}, чат сохранен с названием '{chat_name}'" if conversation_history else f"Контекст сброшен для user_id {user_id}, чат не сохранен (пустая история)")