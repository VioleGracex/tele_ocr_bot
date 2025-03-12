""" main.py """
import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from handlers import register_handlers
from utils import initialize_services

# Загрузка переменных окружения из файла .env
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Use English field names
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера с токеном
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = Bot(token=TELEGRAM_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Регистрация обработчиков
register_handlers(dp, bot)

# Инициализация OCR и GPT сервисов
initialize_services()

async def help_command(message: types.Message):
    help_text = (
        "Команды бота:\n"
        "/start - Запуск бота\n"
        "/StartAnalysis - Начать анализ документа\n"
        "/CancelRequest - Отменить запрос\n"
        "/FAQ - Часто задаваемые вопросы\n"
        "/help - Помощь"
    )
    await message.answer(help_text)

dp.message.register(help_command, lambda message: message.text == "/help")

async def main():
    logger.info("Запуск бота...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())