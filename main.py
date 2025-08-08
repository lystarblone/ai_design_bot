import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import config
from handlers.start import router as start_router
from handlers.chat import router as chat_router
from handlers.reset import router as reset_router
from handlers.help import router as help_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="bot.log"
)
logger = logging.getLogger(__name__)

async def on_startup(bot: Bot):
    """Инициализация команд бота."""
    commands = [
        BotCommand(command="/start", description="start"),
        BotCommand(command="/chat", description="chat"),
        BotCommand(command="/reset", description="reset"),
        BotCommand(command="/help", description="help")
    ]
    await bot.set_my_commands(commands)
    logger.info("Команды бота успешно настроены")

async def main():
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    
    dp.include_router(start_router)
    dp.include_router(chat_router)
    dp.include_router(reset_router)
    dp.include_router(help_router)
    
    try:
        logger.info("Запуск бота...")
        dp.startup.register(on_startup)
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске: {e}")
    finally:
        await bot.session.close()
        logger.info("Сессия бота закрыта")

if __name__ == "__main__":
    asyncio.run(main())