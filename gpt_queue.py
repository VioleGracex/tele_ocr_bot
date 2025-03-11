from aiogram import types
from gemini import analyze_text

prompt_queue = []

async def queue_for_analysis(message: types.Message, text: str):
    prompt_queue.append((message, text))
    await process_queue()

async def process_queue():
    while prompt_queue:
        message, text = prompt_queue.pop(0)
        analysis_result = analyze_text(text)
        await message.answer(f'Распознанный текст:\n{text}')
        await message.answer(f'Анализ текста:\n{analysis_result}')