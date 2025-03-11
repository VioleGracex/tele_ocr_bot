import logging
from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram import Bot
from aiogram.types import ContentType
from file_processing import process_file

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

async def start(message: types.Message):
    await message.answer('Привет! Я бот для распознавания и анализа документов. Отправьте мне файл, и я распознаю текст.')

async def handle_document(message: types.Message, bot: Bot):
    document = message.document
    file_name = document.file_name
    file_size = document.file_size

    logger.info(f"Received document: {file_name} with size {file_size} bytes")

    # Check if the file size exceeds the limit
    if file_size > MAX_FILE_SIZE:
        await message.answer("Размер файла превышает допустимый лимит (10 МБ).")
        logger.warning(f"File size exceeds limit: {file_size} bytes")
        return

    await message.answer(f"Файл {file_name} загружается...")
    await process_file(bot, message, document)
    await message.answer(f"Файл {file_name} успешно загружен.")

def register_handlers(dp: Dispatcher, bot: Bot):
    dp.message.register(start, Command('start'))
    dp.message.register(lambda message: message.content_type == ContentType.DOCUMENT, handle_document)