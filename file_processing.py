import logging
import os
import tempfile
from aiogram import Bot, types
from ocr import process_image, process_pdf, process_docx
from gpt_queue import queue_for_analysis

logger = logging.getLogger(__name__)

async def process_file(bot: Bot, message: types.Message, document: types.Document):
    file_name = document.file_name
    logger.info(f"Starting file download: {file_name}")
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, file_name)
        
        file_info = await bot.get_file(document.file_id)
        await bot.download_file(file_info.file_path, file_path)
        
        logger.info(f"File downloaded: {file_path}")

        # Process the file based on its type
        if file_name.endswith(('.jpg', '.jpeg', '.png')):
            text = process_image(file_path)
        elif file_name.endswith('.pdf'):
            text = process_pdf(file_path)
        elif file_name.endswith('.docx'):
            text = process_docx(file_path)
        else:
            await message.answer("Формат файла не поддерживается.")
            logger.warning(f"Unsupported file format: {file_name}")
            return

        # Log progress
        logger.info(f"File processed for OCR: {file_name}")

        # Queue the recognized text for analysis
        await queue_for_analysis(message, text)