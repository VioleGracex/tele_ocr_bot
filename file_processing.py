import logging
import os
import tempfile
from aiogram import Bot, types
from ocr import process_image, process_pdf, process_docx
from gpt_queue import queue_for_analysis
from keyboards import start_keyboard, cancel_keyboard  # Import the keyboards

logger = logging.getLogger(__name__)

async def process_file(bot: Bot, message: types.Message, document: types.Document):
    file_name = document.file_name
    logger.info(f"Начало загрузки файла: {file_name}")
    
    # Создание временного каталога
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, file_name)
        
        file_info = await bot.get_file(document.file_id)
        await bot.download_file(file_info.file_path, file_path)
        
        logger.info(f"Файл загружен: {file_path}")

        # Обработка файла в зависимости от его типа
        if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            text = process_image(file_path)
        elif file_name.lower().endswith('.pdf'):
            text = process_pdf(file_path)
        elif file_name.lower().endswith('.docx'):
            text = process_docx(file_path)
        else:
            await message.answer("Формат файла не поддерживается.", reply_markup=start_keyboard)
            logger.warning(f"Неподдерживаемый формат файла: {file_name}")
            return

        # Логирование прогресса
        logger.info(f"Файл обработан для OCR: {file_name}")

        # Постановка распознанного текста в очередь на анализ
        await queue_for_analysis(message, text)

async def process_image_message(bot: Bot, message: types.Message, photo: types.PhotoSize):
    if photo is None:
        await message.answer("Пожалуйста, отправьте изображение.")
        return

    logger.info("Начало загрузки изображения")
    
    # Создание временного каталога
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "image.jpg")
        
        file_info = await bot.get_file(photo.file_id)
        await bot.download_file(file_info.file_path, file_path)
        
        logger.info(f"Изображение загружено: {file_path}")

        # Обработка изображения
        text = process_image(file_path)

        # Логирование прогресса
        logger.info("Изображение обработано для OCR")

        # Постановка распознанного текста в очередь на анализ
        await queue_for_analysis(message, text)

# Ensure proper cleanup of temporary files.
def safe_remove(file_path):
    try:
        os.remove(file_path)
    except PermissionError as e:
        logger.error(f"Ошибка при удалении файла {file_path}: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при удалении файла {file_path}: {e}")