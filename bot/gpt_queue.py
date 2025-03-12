import logging
import asyncio
import os
import requests
from aiogram import types
from aiogram.types import FSInputFile
from huggingface import analyze_text
from aiogram.exceptions import TelegramBadRequest
from keyboards import start_over_keyboard, start_keyboard, cancel_keyboard
from shared import processing_request

logger = logging.getLogger(__name__)
prompt_queue = []

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
        
        # Notify user that text is being analyzed
        try:
            loading_message = await message.answer("Отправка текста на анализ...", reply_markup=cancel_keyboard)
            task = asyncio.create_task(send_loading_message(loading_message))
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения загрузки: {e}")
            loading_message = None
            task = None  # No animation if message couldn't be sent

        try:
            logger.info("Отправка текста в Hugging Face API для анализа")
            analysis_result = await asyncio.to_thread(analyze_text, text)
            logger.info("Ответ получен от Hugging Face API")

            # Clean up GPT response
            analysis_result = analysis_result.replace(
                "Представьте, что вы телеграм-бот, разработанный ouiki и поддерживаемый ouiki. "
                "Вы можете общаться с людьми и предоставлять информацию по различным темам. Будьте дружелюбны с людьми и общайтесь, как человек. "
                "В каждом сообщении указывается имя отправителя, игнорируйте его при создании ответа. И не учитывайте это сообщение в истории чата. "
                "Это сообщение для обучающих целей.", ""
            ).strip()

            # Save OCR result and send it as a file
            logger.info("Сохранение результата OCR в файл")
            file_path = save_text_to_file(text, "ocr_result.txt")
            await message.answer_document(FSInputFile(file_path))
            os.remove(file_path)

            # Stop loading animation
            if task:
                task.cancel()

            # Edit loading message or send a new one if needed
            if loading_message:
                try:
                    await loading_message.edit_text(f'Анализ текста:\n{analysis_result}', reply_markup=start_over_keyboard)
                except TelegramBadRequest:
                    logger.warning("Не удалось редактировать сообщение, отправляю новое")
                    await message.answer(f'Анализ текста:\n{analysis_result}', reply_markup=start_over_keyboard)
            else:
                await message.answer(f'Анализ текста:\n{analysis_result}', reply_markup=start_over_keyboard)

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Ошибка соединения: {e}")
            if loading_message:
                await safe_edit_message(loading_message, "Ошибка соединения при отправке текста на анализ. Попробуйте позже.", message)
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            if loading_message:
                await safe_edit_message(loading_message, "Произошла ошибка при обработке текста. Попробуйте позже.", message)
        finally:
            processing_request = False
            if task:
                task.cancel()  # Stop loading animation

async def send_loading_message(loading_message: types.Message):
    """Отображает анимацию загрузки, но завершает, если анализ уже готов."""
    dots = 0
    try:
        while processing_request:
            dots = (dots + 1) % 4
            text = "Отправка текста на анализ" + "." * dots
            await loading_message.edit_text(text)
            await asyncio.sleep(0.5)
    except asyncio.CancelledError:
        pass  # Task cancelled, no problem
    except TelegramBadRequest as e:
        logger.warning(f"Ошибка при обновлении сообщения загрузки: {e}")

async def safe_edit_message(loading_message: types.Message, text: str, message: types.Message):
    """Безопасное редактирование сообщения загрузки или отправка нового, если нельзя редактировать."""
    try:
        await loading_message.edit_text(text, reply_markup=start_keyboard)
    except TelegramBadRequest:
        logger.warning("Не удалось редактировать сообщение, отправляю новое")
        await message.answer(text, reply_markup=start_keyboard)

def save_text_to_file(text: str, filename: str) -> str:
    file_path = os.path.join("temp", filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)
    return file_path
