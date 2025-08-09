import logging
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
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
            "✨ Привет! Я — твой личный эксперт по Human Design.\n\n"
            "Я создан, чтобы помочь тебе разобраться в уникальной системе самопознания, "
            "которая раскрывает твою истинную природу и жизненный путь. "
            "Я могу ответить на любой вопрос по Human Design, помочь расшифровать твою бодиграфию, "
            "дать практичные советы, как применять Human Design в повседневной жизни, "
            "чтобы жить в гармонии со своей энергией.\n\n"
            "Задавай свой вопрос прямо сейчас, и я помогу разобраться! 📚\n\n"
            "Если нужна помощь с командами, используй /help."
        )
    else:
        welcome_text = (
            "✨ Hello! I am your personal Human Design expert.\n\n"
            "I was created to help you understand the unique system of self-discovery "
            "that reveals your true nature and life path. "
            "I can answer any question about Human Design, help you decipher your bodygraph, "
            "and provide practical tips on how to apply Human Design in everyday life "
            "to live in harmony with your energy.\n\n"
            "Ask your question right now, and I'll help you figure it out! 📚\n\n"
            "If you need help with commands, use /help."
        )
    
    await message.answer(welcome_text, reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")
    await state.set_state(HumanDesignStates.MAIN_CONVERSATION)
    logger.info(f"Пользователь ID {user_id} выбрал язык: {cleaned_language}")