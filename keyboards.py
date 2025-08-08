from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

language_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True,
    keyboard=[
        [KeyboardButton(text="Русский 🇷🇺"), KeyboardButton(text="English 🇺🇸")]
    ]
)

def get_save_chat_keyboard(language: str) -> ReplyKeyboardMarkup:
    buttons = (
        [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
        if language == "Русский"
        else [KeyboardButton(text="Yes"), KeyboardButton(text="No")]
    )
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
        keyboard=[buttons]
    )