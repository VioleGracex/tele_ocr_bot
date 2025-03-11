import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile, ContentType
from dotenv import load_dotenv
from ocr import process_image, process_pdf, process_docx
from gemini import analyze_text

# Load environment variables from .env file
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера с токеном
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = Bot(token=TELEGRAM_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Define the maximum file size (in bytes)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Queue to handle prompts
prompt_queue = []

@dp.message(Command('start'))
async def start(message: types.Message):
    await message.answer('Привет! Я бот для распознавания и анализа документов. Отправьте мне файл, и я распознаю текст.')

@dp.message(lambda message: message.content_type == ContentType.DOCUMENT)
async def handle_document(message: types.Message):
    document = message.document
    file_name = document.file_name
    file_size = document.file_size

    # Check if the file size exceeds the limit
    if file_size > MAX_FILE_SIZE:
        await message.answer("Размер файла превышает допустимый лимит (10 МБ).")
        return

    file = await bot.download_file_by_id(document.file_id)
    file_path = f'downloads/{file_name}'
    with open(file_path, 'wb') as f:
        f.write(file.getvalue())

    # Process the file based on its type
    if file_name.endswith(('.jpg', '.jpeg', '.png')):
        text = process_image(file_path)
    elif file_name.endswith('.pdf'):
        text = process_pdf(file_path)
    elif file_name.endswith('.docx'):
        text = process_docx(file_path)
    else:
        await message.answer("Формат файла не поддерживается.")
        return

    # Add the recognized text to the queue
    prompt_queue.append((message, text))

    # Process the queue
    await process_queue()

async def process_queue():
    while prompt_queue:
        message, text = prompt_queue.pop(0)
        analysis_result = analyze_text(text)
        await message.answer(f'Распознанный текст:\n{text}')
        await message.answer(f'Анализ текста:\n{analysis_result}')

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())