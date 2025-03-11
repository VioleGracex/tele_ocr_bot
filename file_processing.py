import os
from aiogram import Bot, types
from aiogram.types import InputFile
from ocr import process_image, process_pdf, process_docx
from gpt_queue import queue_for_analysis

async def process_file(bot: Bot, message: types.Message, document: types.Document):
    file_name = document.file_name
    file = await bot.download(document.file_id)
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

    # Queue the recognized text for analysis
    await queue_for_analysis(message, text)