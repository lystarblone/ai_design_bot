import logging
import json
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from models import Database
from states import HumanDesignStates

logger = logging.getLogger(__name__)

router = Router()

db = Database()

save_chat_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True,
    keyboard=[
        [KeyboardButton(text="Да / Yes"), KeyboardButton(text="Нет / No")]
    ]
)

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
    await message.answer(response, reply_markup=save_chat_keyboard)
    logger.info(f"Пользователь ID {user_id} запросил сброс контекста, ожидается подтверждение сохранения")

@router.message(HumanDesignStates.CONFIRM_SAVE_CHAT)
async def process_save_confirmation(message: Message, state: FSMContext):
    user_id = message.from_user.id
    language = db.get_language(user_id)
    choice = message.text.strip().lower()

    cleaned_choice = choice.replace("🇷🇺", "").replace("🇺🇸", "").strip().lower()

    if cleaned_choice not in ["да", "yes", "нет", "no"]:
        response = (
            "Пожалуйста, выберите 'Да / Yes' или 'Нет / No'."
            if language == "Русский"
            else "Please select 'Yes' or 'No'."
        )
        await message.answer(response, reply_markup=save_chat_keyboard)
        logger.warning(f"Некорректный выбор сохранения от user_id {user_id}: {cleaned_choice}")
        return

    if cleaned_choice in ["да", "yes"]:
        data = await state.get_data()
        conversation_history = data.get("conversation_history", [])
        if conversation_history:
            db.save_conversation(user_id, json.dumps(conversation_history))
            response = (
                "Чат сохранен! Контекст сброшен. Начни новый диалог с /chat. 😊"
                if language == "Русский"
                else "Chat saved! Context reset. Start a new conversation with /chat. 😊"
            )
        else:
            response = (
                "История чата пуста, ничего не сохранено. Контекст сброшен. Начни новый диалог с /chat."
                if language == "Русский"
                else "Chat history is empty, nothing saved. Context reset. Start a new conversation with /chat."
            )
    else:
        response = (
            "Чат не сохранен. Контекст сброшен. Начни новый диалог с /chat."
            if language == "Русский"
            else "Chat not saved. Context reset. Start a new conversation with /chat."
        )

    await state.clear()
    await message.answer(response)
    logger.info(f"Контекст сброшен для user_id {user_id}, чат {'сохранен' if cleaned_choice in ['да', 'yes'] else 'не сохранен'}")