import logging
import json
from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
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

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=f"{chat.chat_name} ({chat.saved_at.strftime('%Y-%m-%d %H:%M:%S')} UTC)",
                    callback_data=f"select_chat:{chat.chat_name}"
                )] for chat in chats
            ])
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

@router.callback_query(lambda c: c.data.startswith("select_chat:"))
async def process_chat_selection(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    language = db.get_language(user_id)
    chat_name = callback.data.split(":", 1)[1]

    with db.Session() as session:
        try:
            chat = session.query(ChatHistory).filter_by(user_id=user_id, chat_name=chat_name).first()
            if not chat:
                response = (
                    "Выбранный чат не найден. Попробуйте снова или начните новый диалог с /chat."
                    if language == "Русский"
                    else "Selected chat not found. Try again or start a new conversation with /chat."
                )
                await callback.message.edit_text(response)
                logger.warning(f"Пользователь ID {user_id} выбрал несуществующий чат: {chat_name}")
                return

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=f"🟢 Открыть" if language == "Русский" else "🟢 Open",
                    callback_data=f"open_chat:{chat_name}"
                )],
                [InlineKeyboardButton(
                    text=f"✏️ Переименовать" if language == "Русский" else "✏️ Rename",
                    callback_data=f"rename_chat:{chat_name}"
                )],
                [InlineKeyboardButton(
                    text=f"🗑️ Удалить" if language == "Русский" else "🗑️ Delete",
                    callback_data=f"delete_chat:{chat_name}"
                )],
                [InlineKeyboardButton(
                    text=f"⬅️ Назад" if language == "Русский" else "⬅️ Back",
                    callback_data="back_to_history"
                )]
            ])
            response = (
                f"Выбранный чат: {chat_name}"
                if language == "Русский"
                else f"Selected chat: {chat_name}"
            )
            await state.update_data(selected_chat_name=chat_name)
            await state.set_state(HumanDesignStates.CHAT_ACTIONS)
            await callback.message.edit_text(response, reply_markup=keyboard)
            logger.info(f"Пользователь ID {user_id} выбрал чат '{chat_name}'")
        except Exception as e:
            response = (
                f"❌ Ошибка при выборе чата: {str(e)}"
                if language == "Русский"
                else f"❌ Error selecting chat: {str(e)}"
            )
            await callback.message.edit_text(response)
            logger.error(f"Ошибка выбора чата для user_id {user_id}: {str(e)}")

@router.callback_query(lambda c: c.data.startswith("open_chat:"))
async def open_chat(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    language = db.get_language(user_id)
    chat_name = callback.data.split(":", 1)[1]

    with db.Session() as session:
        try:
            chat = session.query(ChatHistory).filter_by(user_id=user_id, chat_name=chat_name).first()
            if not chat:
                response = (
                    "Чат не найден. Попробуйте снова или начните новый диалог с /chat."
                    if language == "Русский"
                    else "Chat not found. Try again or start a new conversation with /chat."
                )
                await callback.message.edit_text(response)
                logger.warning(f"Пользователь ID {user_id} попытался открыть несуществующий чат: {chat_name}")
                return

            conversation_history = json.loads(chat.conversation)
            await state.update_data(conversation_history=conversation_history, conversation_name=chat_name)
            await state.set_state(HumanDesignStates.MAIN_CONVERSATION)
            response = (
                f"Чат '{chat_name}' загружен! Задай свой вопрос! 😊"
                if language == "Русский"
                else f"Chat '{chat_name}' loaded! Ask your question! 😊"
            )
            await callback.message.edit_text(response)
            logger.info(f"Пользователь ID {user_id} открыл чат '{chat_name}'")
        except Exception as e:
            response = (
                f"❌ Ошибка при загрузке чата: {str(e)}"
                if language == "Русский"
                else f"❌ Error loading chat: {str(e)}"
            )
            await callback.message.edit_text(response)
            logger.error(f"Ошибка загрузки чата для user_id {user_id}: {str(e)}")

@router.callback_query(lambda c: c.data.startswith("rename_chat:"))
async def rename_chat(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    language = db.get_language(user_id)
    chat_name = callback.data.split(":", 1)[1]

    response = (
        f"Введите новое название для чата '{chat_name}':"
        if language == "Русский"
        else f"Enter a new name for chat '{chat_name}':"
    )
    await state.set_state(HumanDesignStates.RENAME_CHAT)
    await state.update_data(old_chat_name=chat_name)
    await callback.message.answer(response)
    logger.info(f"Пользователь ID {user_id} запросил переименование чата '{chat_name}'")

@router.message(HumanDesignStates.RENAME_CHAT)
async def process_rename_chat(message: Message, state: FSMContext):
    user_id = message.from_user.id
    language = db.get_language(user_id)
    new_name = message.text.strip()

    if not new_name or len(new_name) > 100:
        response = (
            "Название чата должно быть не пустым и не длиннее 100 символов. Попробуйте снова."
            if language == "Русский"
            else "Chat name must not be empty and should be less than 100 characters. Try again."
        )
        await message.answer(response)
        logger.warning(f"Некорректное новое название чата от user_id {user_id}: {new_name}")
        return

    data = await state.get_data()
    old_name = data.get("old_chat_name")

    try:
        db.rename_conversation(user_id, old_name, new_name)
        response = (
            f"Чат успешно переименован из '{old_name}' в '{new_name}'! Выберите действие:"
            if language == "Русский"
            else f"Chat successfully renamed from '{old_name}' to '{new_name}'! Select an action:"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=f"🟢 Открыть" if language == "Русский" else "🟢 Open",
                callback_data=f"open_chat:{new_name}"
            )],
            [InlineKeyboardButton(
                text=f"✏️ Переименовать" if language == "Русский" else "✏️ Rename",
                callback_data=f"rename_chat:{new_name}"
            )],
            [InlineKeyboardButton(
                text=f"🗑️ Удалить" if language == "Русский" else "🗑️ Delete",
                callback_data=f"delete_chat:{new_name}"
            )],
            [InlineKeyboardButton(
                text=f"⬅️ Назад" if language == "Русский" else "⬅️ Back",
                callback_data="back_to_history"
            )]
        ])
        await state.update_data(selected_chat_name=new_name)
        await state.set_state(HumanDesignStates.CHAT_ACTIONS)
        await message.answer(response, reply_markup=keyboard)
        logger.info(f"Пользователь ID {user_id} переименовал чат из '{old_name}' в '{new_name}'")
    except Exception as e:
        response = (
            f"❌ Ошибка при переименовании чата: {str(e)}"
            if language == "Русский"
            else f"❌ Error renaming chat: {str(e)}"
        )
        await message.answer(response)
        logger.error(f"Ошибка переименования чата для user_id {user_id}: {str(e)}")

@router.callback_query(lambda c: c.data == "back_to_history")
async def back_to_history(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
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
                await callback.message.edit_text(response)
                logger.info(f"Пользователь ID {user_id} вернулся к истории чатов, но она пуста")
                return

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=f"{chat.chat_name} ({chat.saved_at.strftime('%Y-%m-%d %H:%M:%S')} UTC)",
                    callback_data=f"select_chat:{chat.chat_name}"
                )] for chat in chats
            ])
            response = (
                "Выберите чат для продолжения:"
                if language == "Русский"
                else "Select a chat to continue:"
            )
            await state.set_state(HumanDesignStates.SELECT_CHAT)
            await callback.message.edit_text(response, reply_markup=keyboard)
            logger.info(f"Пользователь ID {user_id} вернулся к истории чатов")
        except Exception as e:
            response = (
                f"❌ Ошибка при получении истории: {str(e)}"
                if language == "Русский"
                else f"❌ Error retrieving history: {str(e)}"
            )
            await callback.message.edit_text(response)
            logger.error(f"Ошибка получения истории чатов для user_id {user_id}: {str(e)}")

@router.callback_query(lambda c: c.data.startswith("delete_chat:"))
async def delete_chat(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    language = db.get_language(user_id)
    chat_name = callback.data.split(":", 1)[1]

    try:
        db.delete_conversation(user_id, chat_name)
        response = (
            f"Чат '{chat_name}' успешно удален! Начни новый диалог с /chat."
            if language == "Русский"
            else f"Chat '{chat_name}' successfully deleted! Start a new conversation with /chat."
        )
        await callback.message.edit_text(response)
        await state.clear()
        logger.info(f"Пользователь ID {user_id} удалил чат '{chat_name}'")
    except Exception as e:
        response = (
            f"❌ Ошибка при удалении чата: {str(e)}"
            if language == "Русский"
            else f"❌ Error deleting chat: {str(e)}"
        )
        await callback.message.edit_text(response)
        logger.error(f"Ошибка удаления чата для user_id {user_id}: {str(e)}")