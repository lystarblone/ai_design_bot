import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import config
import json

logger = logging.getLogger(__name__)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    language = Column(String, default="Русский")
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    chat_name = Column(String, nullable=False)
    conversation = Column(Text, nullable=False)
    saved_at = Column(DateTime, default=datetime.utcnow)

class Database:
    def __init__(self):
        self.engine = create_engine(f"sqlite:///{config.DB_PATH}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_user(self, user_id: int, username: str):
        """Добавление или обновление пользователя."""
        with self.Session() as session:
            try:
                user = session.query(User).filter_by(user_id=user_id).first()
                if not user:
                    user = User(user_id=user_id, username=username)
                    session.add(user)
                else:
                    user.username = username
                session.commit()
                logger.info(f"Пользователь {username} (ID: {user_id}) добавлен/обновлен")
            except Exception as e:
                logger.error(f"Ошибка добавления пользователя {user_id}: {str(e)}")
                session.rollback()

    def set_language(self, user_id: int, language: str):
        """Установка языка пользователя."""
        with self.Session() as session:
            try:
                user = session.query(User).filter_by(user_id=user_id).first()
                if user:
                    user.language = language
                    session.commit()
                    logger.info(f"Язык для user_id {user_id} установлен: {language}")
            except Exception as e:
                logger.error(f"Ошибка установки языка для user_id {user_id}: {str(e)}")
                session.rollback()

    def get_language(self, user_id: int) -> str:
        """Получение языка пользователя."""
        with self.Session() as session:
            try:
                user = session.query(User).filter_by(user_id=user_id).first()
                return user.language if user else "Русский"
            except Exception as e:
                logger.error(f"Ошибка получения языка для user_id {user_id}: {str(e)}")
                return "Русский"

    def save_conversation(self, user_id: int, chat_name: str, conversation: str):
        """Сохранение нового чата с проверкой уникальности названия."""
        with self.Session() as session:
            try:
                if session.query(ChatHistory).filter_by(user_id=user_id, chat_name=chat_name).first():
                    raise ValueError(f"Чат с названием '{chat_name}' уже существует")
                chat = ChatHistory(user_id=user_id, chat_name=chat_name, conversation=conversation)
                session.add(chat)
                session.commit()
                logger.info(f"История чата '{chat_name}' сохранена для user_id {user_id}")
            except Exception as e:
                logger.error(f"Ошибка сохранения истории чата для user_id {user_id}: {str(e)}")
                session.rollback()
                raise

    def update_conversation(self, user_id: int, chat_name: str, new_conversation: str):
        """Дополнение существующего чата."""
        with self.Session() as session:
            try:
                chat = session.query(ChatHistory).filter_by(user_id=user_id, chat_name=chat_name).first()
                if chat:
                    existing_history = json.loads(chat.conversation)
                    new_history = json.loads(new_conversation)
                    chat.conversation = json.dumps(existing_history + new_history)
                    chat.saved_at = datetime.utcnow()
                    session.commit()
                    logger.info(f"История чата '{chat_name}' дополнена для user_id {user_id}")
                else:
                    logger.warning(f"Чат '{chat_name}' не найден для user_id {user_id}, создается новый")
                    self.save_conversation(user_id, chat_name, new_conversation)
            except Exception as e:
                logger.error(f"Ошибка дополнения истории чата для user_id {user_id}: {str(e)}")
                session.rollback()
                raise

    def rename_conversation(self, user_id: int, old_name: str, new_name: str):
        """Переименование чата с проверкой уникальности нового названия."""
        with self.Session() as session:
            try:
                if session.query(ChatHistory).filter_by(user_id=user_id, chat_name=new_name).first():
                    raise ValueError(f"Чат с названием '{new_name}' уже существует")
                chat = session.query(ChatHistory).filter_by(user_id=user_id, chat_name=old_name).first()
                if chat:
                    chat.chat_name = new_name
                    chat.saved_at = datetime.utcnow()
                    session.commit()
                    logger.info(f"Чат '{old_name}' переименован в '{new_name}' для user_id {user_id}")
                else:
                    logger.warning(f"Чат '{old_name}' не найден для user_id {user_id}")
                    raise ValueError(f"Чат '{old_name}' не найден")
            except Exception as e:
                logger.error(f"Ошибка переименования чата для user_id {user_id}: {str(e)}")
                session.rollback()
                raise

    def delete_conversation(self, user_id: int, chat_name: str):
        """Удаление чата."""
        with self.Session() as session:
            try:
                chat = session.query(ChatHistory).filter_by(user_id=user_id, chat_name=chat_name).first()
                if chat:
                    session.delete(chat)
                    session.commit()
                    logger.info(f"Чат '{chat_name}' удален для user_id {user_id}")
                else:
                    logger.warning(f"Чат '{chat_name}' не найден для user_id {user_id}")
                    raise ValueError(f"Чат '{chat_name}' не найден")
            except Exception as e:
                logger.error(f"Ошибка удаления чата для user_id {user_id}: {str(e)}")
                session.rollback()
                raise

    def get_conversation(self, user_id: int, chat_name: str = None):
        """Получение сохраненной истории чата."""
        with self.Session() as session:
            try:
                if chat_name:
                    chat = session.query(ChatHistory).filter_by(user_id=user_id, chat_name=chat_name).first()
                else:
                    chat = session.query(ChatHistory).filter_by(user_id=user_id).order_by(ChatHistory.saved_at.desc()).first()
                return chat if chat else None
            except Exception as e:
                logger.error(f"Ошибка получения истории чата для user_id {user_id}: {str(e)}")
                return None