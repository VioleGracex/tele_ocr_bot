import logging
import asyncio
import os
import requests
from aiogram import types
from aiogram.types import FSInputFile
from huggingface import analyze_text
from keyboards import start_keyboard  # Import the start_keyboard

logger = logging.getLogger(__name__)
prompt_queue = []
processing_request = False

async def queue_for_analysis(message: types.Message, text: str):
    global processing_request
    if processing_request:
        await message.answer("Обрабатывается другой запрос. Пожалуйста, подождите.")
        return
    
    prompt_queue.append((message, text))
    logger.info("Текст добавлен в очередь на анализ GPT")
    await process_queue()

async def process_queue():
    global processing_request
    processing_request = True
    while prompt_queue:
        message, text = prompt_queue.pop(0)
        logger.info("Начало анализа GPT")
        
        # Уведомление пользователя о том, что текст отправляется на анализ
        await message.answer("Отправка текста на анализ...")

        try:
            # Анализ текста с использованием Hugging Face API
            logger.info("Отправка текста в Hugging Face API для анализа")
            analysis_result = await asyncio.to_thread(analyze_text, text)
            logger.info("Ответ получен от Hugging Face API")
            
            # Сохранение результата OCR в файл и отправка его пользователю
            logger.info("Сохранение результата OCR в файл")
            file_path = save_text_to_file(text, "ocr_result.txt")
            await message.answer_document(FSInputFile(file_path))
            os.remove(file_path)  # Очистка файла после отправки
            
            # Отправка результата анализа пользователю
            await message.answer(f'Анализ текста:\n{analysis_result}', reply_markup=start_keyboard)
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Ошибка соединения: {e}")
            await message.answer("Ошибка соединения при отправке текста на анализ. Пожалуйста, попробуйте позже.", reply_markup=start_keyboard)
        finally:
            processing_request = False

def save_text_to_file(text: str, filename: str) -> str:
    file_path = os.path.join("temp", filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)
    return file_path