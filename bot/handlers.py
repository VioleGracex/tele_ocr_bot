import logging
from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram import Bot
from aiogram.types import ContentType
from file_processing import process_file, process_image_message  # Updated import
from keyboards import start_keyboard, cancel_keyboard, modes_keyboard  # Updated import
from shared import processing_request  # Import the shared variable

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 МБ

user_modes = {}

async def start(message: types.Message):
    await message.answer('Привет! Я бот для распознавания и анализа документов. Выберите режим:\n'
                         '1. "/OCROnly" - Только OCR\n'
                         '2. "/OCRAndGPT" - OCR и анализ GPT', reply_markup=start_keyboard)

async def handle_document(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    mode = user_modes.get(user_id)
    
    if not mode:
        await message.answer("Пожалуйста, выберите режим и начните анализ с помощью команды /StartAnalysis.")
        return

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
    await process_file(bot, message, document, mode)

async def handle_photo(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    mode = user_modes.get(user_id)
    
    if not mode:
        await message.answer("Пожалуйста, выберите режим и начните анализ с помощью команды /StartAnalysis.")
        return

    photo = message.photo[-1] if message.photo else None
    if not photo:
        await message.answer("Пожалуйста, отправьте изображение.")
        return

    await process_image_message(bot, message, photo, mode)

async def faq_and_help(message: types.Message):
    help_text = (
        "FAQ и помощь:\n"
        "1. Чтобы начать, нажмите '/Start'.\n"
        "2. Чтобы выбрать режим OCR, нажмите '/OCROnly'.\n"
        "3. Чтобы выбрать режим OCR и GPT, нажмите '/OCRAndGPT'.\n"
        "4. Чтобы начать анализ документа, нажмите '/StartAnalysis'.\n"
        "5. Чтобы отменить запрос, нажмите '/CancelRequest'.\n"
        "6. Для получения дополнительной информации или помощи нажмите '/FAQ'."
    )
    await message.answer(help_text)

async def cancel_request(message: types.Message):
    global processing_request
    if not processing_request:
        await message.answer("Нет активных запросов для отмены.", reply_markup=start_keyboard)
    else:
        # Logic to cancel the request if necessary
        await message.answer("Запрос отменен.", reply_markup=start_keyboard)
        processing_request = False  # Reset the processing request flag

async def start_analysis(message: types.Message):
    user_id = message.from_user.id
    mode = user_modes.get(user_id)
    
    if not mode:
        await message.answer("Пожалуйста, выберите режим с помощью команды /Modes.")
    else:
        await message.answer(f"Режим {mode} установлен. Пожалуйста, отправьте файл для анализа.")

async def set_mode_ocr_only(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_modes[user_id] = 'OCROnly'
    await callback_query.message.edit_text("Режим установлен на 'Только OCR'. Теперь используйте команду /StartAnalysis для начала анализа.")

async def set_mode_ocr_and_gpt(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_modes[user_id] = 'OCRAndGPT'
    await callback_query.message.edit_text("Режим установлен на 'OCR и анализ GPT'. Теперь используйте команду /StartAnalysis для начала анализа.")

async def choose_mode(message: types.Message):
    await message.answer("Выберите режим анализа:", reply_markup=modes_keyboard)

async def command_set_mode_ocr_only(message: types.Message):
    user_id = message.from_user.id
    user_modes[user_id] = 'OCROnly'
    await message.answer("Режим установлен на 'Только OCR'. Теперь используйте команду /StartAnalysis для начала анализа.")

async def command_set_mode_ocr_and_gpt(message: types.Message):
    user_id = message.from_user.id
    user_modes[user_id] = 'OCRAndGPT'
    await message.answer("Режим установлен на 'OCR и анализ GPT'. Теперь используйте команду /StartAnalysis для начала анализа.")

def register_handlers(dp: Dispatcher, bot: Bot):
    dp.message.register(start, Command('start'))
    dp.message.register(faq_and_help, Command('FAQ'))
    dp.message.register(cancel_request, Command('CancelRequest'))
    dp.message.register(start_analysis, Command('StartAnalysis'))
    dp.message.register(choose_mode, Command('Modes'))
    dp.message.register(command_set_mode_ocr_only, Command('OCROnly'))
    dp.message.register(command_set_mode_ocr_and_gpt, Command('OCRAndGPT'))
    dp.callback_query.register(set_mode_ocr_only, lambda call: call.data == "set_mode_ocr_only")
    dp.callback_query.register(set_mode_ocr_and_gpt, lambda call: call.data == "set_mode_ocr_and_gpt")
    dp.message.register(handle_document, lambda message: message.content_type == ContentType.DOCUMENT)
    dp.message.register(handle_photo, lambda message: message.content_type == ContentType.PHOTO)