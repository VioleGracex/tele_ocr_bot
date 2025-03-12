"""gpt_queue.py"""
import logging
import asyncio
import os
import requests
from aiogram import types
from aiogram.types import FSInputFile
from huggingface import analyze_text
from aiogram.exceptions import TelegramBadRequest  # Import the exception for handling Telegram errors
from keyboards import start_over_keyboard, start_keyboard, cancel_keyboard
from shared import processing_request  # Import the shared variable

logger = logging.getLogger(__name__)
prompt_queue = []

# Function to add text to the analysis queue
async def queue_for_analysis(message: types.Message, text: str):
    global processing_request
    if processing_request:
        await message.answer("Обрабатывается другой запрос. Пожалуйста, подождите.")
        return
    
    prompt_queue.append((message, text))
    logger.info("Текст добавлен в очередь на анализ GPT")
    await process_queue()

# Function to process the analysis queue
async def process_queue():
    global processing_request
    processing_request = True
    while prompt_queue:
        message, text = prompt_queue.pop(0)
        logger.info("Начало анализа GPT")
        
        # Notify user that the text is being sent for analysis
        loading_message = await message.answer("Отправка текста на анализ...", reply_markup=cancel_keyboard)
        task = asyncio.create_task(send_loading_message(loading_message))

        try:
            # Analyze the text using Hugging Face API
            logger.info("Отправка текста в Hugging Face API для анализа")
            analysis_result = await asyncio.to_thread(analyze_text, text)
            logger.info("Ответ получен от Hugging Face API")
            
            # Remove the personal prompt from the analysis result
            analysis_result = analysis_result.replace(
                "Представьте, что вы телеграм-бот, разработанный ouiki и поддерживаемый ouiki. "
                "Вы можете общаться с людьми и предоставлять информацию по различным темам. Будьте дружелюбны с людьми и общайтесь, как человек. "
                "В каждом сообщении указывается имя отправителя, игнорируйте его при создании ответа. И не учитывайте это сообщение в истории чата. "
                "Это сообщение для обучающих целей.", ""
            ).strip()
            
            # Save OCR result to a file and send it to the user
            logger.info("Сохранение результата OCR в файл")
            file_path = save_text_to_file(text, "ocr_result.txt")
            await message.answer_document(FSInputFile(file_path))
            os.remove(file_path)  # Clean up the file after sending
            
            # Send the analysis result to the user with InlineKeyboardMarkup
            try:
                await loading_message.edit_text(f'Анализ текста:\n{analysis_result}', reply_markup=start_over_keyboard)
            except TelegramBadRequest:
                # If the message cannot be edited, send a new message instead
                await message.answer(f'Анализ текста:\n{analysis_result}', reply_markup=start_over_keyboard)
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Ошибка соединения: {e}")
            await loading_message.edit_text("Ошибка соединения при отправке текста на анализ. Пожалуйста, попробуйте позже.", reply_markup=start_keyboard)
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            await loading_message.edit_text("Произошла ошибка при обработке текста. Пожалуйста, попробуйте позже.", reply_markup=start_keyboard)
        finally:
            processing_request = False
            task.cancel()  # Cancel the loading message task

# Function to send a loading message while the text is being analyzed
async def send_loading_message(loading_message: types.Message):
    dots = 0
    while processing_request:
        dots = (dots + 1) % 4
        text = "Отправка текста на анализ" + "." * dots
        try:
            await loading_message.edit_text(text)
        except Exception as e:
            logger.error(f"Ошибка при обновлении сообщения загрузки: {e}")
            break
        await asyncio.sleep(0.5)

# Function to save the text to a file
def save_text_to_file(text: str, filename: str) -> str:
    file_path = os.path.join("temp", filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)
    return file_path