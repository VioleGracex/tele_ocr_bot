import logging
import asyncio
import os
import requests
from aiogram import types
from aiogram.types import InputFile
from gemini import analyze_text

logger = logging.getLogger(__name__)
prompt_queue = []

async def queue_for_analysis(message: types.Message, text: str):
    prompt_queue.append((message, text))
    logger.info("Text added to GPT analysis queue")
    await process_queue()

async def process_queue():
    while prompt_queue:
        message, text = prompt_queue.pop(0)
        logger.info("Starting GPT analysis")
        
        # Notify the user that the text is being sent for analysis
        await message.answer("Отправка текста на анализ...")
        
        try:
            # Analyze the text
            analysis_result = await asyncio.to_thread(analyze_text, text)
            
            # Save the OCR result to a file and send it to the user
            file_path = save_text_to_file(text, "ocr_result.txt")
            await message.answer_document(InputFile(file_path))
            os.remove(file_path)  # Clean up the file after sending
            
            # Send the analysis result to the user
            await message.answer(f'Анализ текста:\n{analysis_result}')
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            await message.answer("Ошибка соединения при отправке текста на анализ. Пожалуйста, попробуйте позже.")

def save_text_to_file(text: str, filename: str) -> str:
    file_path = os.path.join("temp", filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)
    return file_path