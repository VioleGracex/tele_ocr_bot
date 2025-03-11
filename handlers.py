from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ContentType
from file_processing import process_file

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

async def start(message: types.Message):
    await message.answer('Привет! Я бот для распознавания и анализа документов. Отправьте мне файл, и я распознаю текст.')

async def handle_document(message: types.Message, bot):
    document = message.document
    file_name = document.file_name
    file_size = document.file_size

    # Check if the file size exceeds the limit
    if file_size > MAX_FILE_SIZE:
        await message.answer("Размер файла превышает допустимый лимит (10 МБ).")
        return

    await process_file(bot, message, document)

def register_handlers(dp: Dispatcher, bot):
    dp.message(Command('start'))(start)
    dp.message(lambda message: message.content_type == ContentType.DOCUMENT)(lambda message: handle_document(message, bot))