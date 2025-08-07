import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import config

logger = logging.getLogger(__name__)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    language = Column(String, default="Русский")
    created_at = Column(DateTime, default=datetime.utcnow)

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