import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from models import Database
from states import HumanDesignStates
from keyboards import language_keyboard

logger = logging.getLogger(__name__)

router = Router()

db = Database()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or f"user_{user_id}"
    
    db.add_user(user_id, username)
    
    await state.set_state(HumanDesignStates.SELECT_LANGUAGE)
    await message.answer(
        "🌟 Добрый день! Hello!\n\nПожалуйста, выберите язык / Please choose your language:",
        reply_markup=language_keyboard
    )
    logger.info(f"Пользователь ID {user_id} запустил команду /start")

@router.message(HumanDesignStates.SELECT_LANGUAGE)
async def handle_language_selection(message: Message, state: FSMContext):
    user_id = message.from_user.id
    language = message.text.strip()

    cleaned_language = language.replace("🇷🇺", "").replace("🇺🇸", "").strip()

    if cleaned_language not in ["Русский", "English"]:
        await message.answer(
            "Пожалуйста, выберите язык из предложенных / Please select a language from the options.",
            reply_markup=language_keyboard
        )
        logger.warning(f"Некорректный выбор языка от user_id {user_id}: {language} (очищено: {cleaned_language})")
        return

    db.set_language(user_id, cleaned_language)
    
    if cleaned_language == "Русский":
        welcome_text = (
            "✨Привет! Я @DesignAssistantBot — эксперт по Human Design.\n"
            "Знаю все о типах, центрах, профилях, авторитетах, воротах и каналах.\n\n"
            "Задавай свой вопрос прямо сейчас, и я помогу разобраться! 📚"
        )
    else:
        welcome_text = (
            "Hi! I'm @DesignAssistantBot, a Human Design expert. "
            "I can answer questions about types, centers, profiles, authority, gates, lines, and channels. "
            "Ask away, and I'll help you understand! 😊\n\n"
            "Use /chat to ask questions or /reset to clear context."
        )
    
    await message.answer(welcome_text)
    await state.set_state(HumanDesignStates.MAIN_CONVERSATION)
    logger.info(f"Пользователь ID {user_id} выбрал язык: {cleaned_language}")