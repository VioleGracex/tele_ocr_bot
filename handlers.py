import logging
from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram import Bot
from aiogram.types import ContentType
from file_processing import process_file, process_image_message
from keyboards import start_keyboard, cancel_keyboard

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 МБ

async def start(message: types.Message):
    await message.answer('Привет! Я бот для распознавания и анализа документов. Нажмите "/StartAnalysis", чтобы начать анализ.', reply_markup=start_keyboard)

async def handle_document(message: types.Message, bot: Bot):
    document = message.document
    if not document:
        await message.answer("Пожалуйста, отправьте файл.")
        return

    file_name = document.file_name
    file_size = document.file_size

    logger.info(f"Получен документ: {file_name} размером {file_size} байт")

    # Проверка, превышает ли размер файла лимит
    if file_size > MAX_FILE_SIZE:
        await message.answer("Размер файла превышает допустимый лимит (10 МБ).")
        logger.warning(f"Размер файла превышает лимит: {file_size} байт")
        return

    await message.answer(f"Файл {file_name} загружается...", reply_markup=cancel_keyboard)
    await process_file(bot, message, document)

async def handle_photo(message: types.Message, bot: Bot):
    photo = message.photo[-1] if message.photo else None
    if not photo:
        await message.answer("Пожалуйста, отправьте изображение.")
        return

    await process_image_message(bot, message, photo)

async def faq_and_help(message: types.Message):
    help_text = (
        "FAQ и помощь:\n"
        "1. Чтобы начать, нажмите '/Start'.\n"
        "2. Чтобы начать анализ документа, нажмите '/StartAnalysis' и отправьте документ.\n"
        "3. Чтобы отменить запрос, нажмите '/CancelRequest'.\n"
        "4. Для получения дополнительной информации или помощи нажмите '/FAQ'."
    )
    await message.answer(help_text)

async def cancel_request(message: types.Message):
    await message.answer("Запрос отменен.", reply_markup=start_keyboard)

async def start_analysis(message: types.Message):
    await message.answer("Отправьте файл для анализа.")

def register_handlers(dp: Dispatcher, bot: Bot):
    dp.message.register(start, Command('start'))
    dp.message.register(faq_and_help, Command('FAQ'))
    dp.message.register(cancel_request, Command('CancelRequest'))
    dp.message.register(start_analysis, Command('StartAnalysis'))
    dp.message.register(handle_document, lambda message: message.content_type == ContentType.DOCUMENT)
    dp.message.register(handle_photo, lambda message: message.content_type == ContentType.PHOTO)