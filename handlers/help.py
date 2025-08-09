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
    
    if language == "Русский":
        response = (
            "📚 *Список команд бота:*\n\n"
            "👋 */start* - Запустить бота и начать новый диалог.\n"
            "💬 */chat* - Начать новый чат или продолжить текущий.\n"
            "🔄 */reset* - Сбросить текущий контекст чата. Вы можете сохранить текущий чат перед сбросом.\n"
            "📜 */history* - Просмотреть список сохранённых чатов. Выберите чат для открытия, переименования или удаления:\n"
            "   - 🟢 *Открыть*: Загружает чат, и вы можете продолжить диалог.\n"
            "   - ✏️ *Переименовать*: Запрашивает новое название для чата.\n"
            "   - 🗑️ *Удалить*: Удаляет чат.\n"
            "   - ⬅️ *Назад*: Возвращает к списку чатов.\n\n"
            "   После переименования или удаления вы можете сразу продолжить диалог без вызова /chat."
        )
    else:
        response = (
            "📚 *List of bot commands:*\n\n"
            "👋 */start* - Start the bot and begin a new conversation.\n"
            "💬 */chat* - Start a new chat or continue the current one.\n"
            "🔄 */reset* - Reset the current chat context. You can save the current chat before resetting.\n"
            "📜 */history* - View the list of saved chats. Select a chat to open, rename, or delete:\n"
            "   - 🟢 *Open*: Loads the chat, and you can continue the conversation.\n"
            "   - ✏️ *Rename*: Prompts for a new chat name.\n"
            "   - 🗑️ *Delete*: Deletes the chat.\n"
            "   - ⬅️ *Back*: Returns to the chat list.\n\n"
            "   After renaming or deleting, you can continue the conversation without calling /chat."
        )
    
    await message.answer(response, parse_mode="Markdown")
    logger.info(f"Пользователь ID {user_id} запросил справку (язык: {language})")