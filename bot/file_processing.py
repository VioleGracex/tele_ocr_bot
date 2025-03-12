import logging
import os
import tempfile
import asyncio
import time
from aiogram import Bot, types
from aiogram.exceptions import TelegramBadRequest
from ocr import process_image, process_pdf, process_docx
from gpt_queue import queue_for_analysis
from keyboards import cancel_keyboard, start_over_keyboard

logger = logging.getLogger(__name__)

async def process_file(bot: Bot, message: types.Message, document: types.Document, mode: str):
    file_name = document.file_name
    logger.info(f"Начало загрузки файла: {file_name}")

    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, file_name)

        file_info = await bot.get_file(document.file_id)
        await bot.download_file(file_info.file_path, file_path)
        logger.info(f"Файл загружен: {file_path}")

        try:
            # Start processing and measure time
            start_time = time.time()
            loading_message = await message.answer("Обработка файла...", reply_markup=cancel_keyboard)
            task = asyncio.create_task(send_loading_message(loading_message, "Обработка файла"))

            text = await asyncio.wait_for(asyncio.to_thread(process_document, file_path, file_name), timeout=60)

            elapsed_time = time.time() - start_time
            task.cancel()  # Stop animation

            if len(text) < 10:
                await safe_edit_message(loading_message, "Результат OCR содержит менее 10 символов. Анализ не будет выполнен.")
            else:
                if mode == 'OCRAndGPT':
                    await queue_for_analysis(message, text)
                else:
                    await send_result_as_file(bot, message, text, loading_message, elapsed_time)
        except asyncio.TimeoutError:
            await safe_edit_message(loading_message, "Время обработки файла истекло. Пожалуйста, попробуйте еще раз.")
        except Exception as e:
            logger.error(f"Ошибка при обработке файла: {e}")
            await safe_edit_message(loading_message, "Произошла ошибка при обработке файла. Пожалуйста, попробуйте еще раз.")
        finally:
            safe_remove(file_path)

async def process_image_message(bot: Bot, message: types.Message, photo: types.PhotoSize, mode: str):
    if photo is None:
        await message.answer("Пожалуйста, отправьте изображение.")
        return

    logger.info("Начало загрузки изображения")

    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "image.jpg")

        file_info = await bot.get_file(photo.file_id)
        await bot.download_file(file_info.file_path, file_path)

        logger.info(f"Изображение загружено: {file_path}")

        try:
            start_time = time.time()
            loading_message = await message.answer("Обработка изображения...", reply_markup=cancel_keyboard)
            task = asyncio.create_task(send_loading_message(loading_message, "Обработка изображения"))

            text = await asyncio.wait_for(process_image(file_path), timeout=60)

            elapsed_time = time.time() - start_time
            task.cancel()  # Stop animation

            if len(text) < 10:
                await safe_edit_message(loading_message, "Результат OCR содержит менее 10 символов. Анализ не будет выполнен.")
            else:
                if mode == 'OCRAndGPT':
                    await queue_for_analysis(message, text)
                else:
                    await send_result_as_file(bot, message, text, loading_message, elapsed_time)
        except asyncio.TimeoutError:
            await safe_edit_message(loading_message, "Время обработки изображения истекло. Пожалуйста, попробуйте еще раз.")
        except Exception as e:
            logger.error(f"Ошибка при обработке изображения: {e}")
            await safe_edit_message(loading_message, "Произошла ошибка при обработке изображения. Пожалуйста, попробуйте еще раз.")
        finally:
            safe_remove(file_path)

async def send_result_as_file(bot: Bot, message: types.Message, text: str, loading_message: types.Message, elapsed_time: float):
    """ Отправка результата в виде файла, если OCR завершился быстро, удаляем сообщение загрузки. """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as temp_file:
        temp_file.write(text)
        temp_file_path = temp_file.name  

    try:
        with open(temp_file_path, "rb") as file_to_send:
            await bot.send_document(chat_id=message.chat.id, document=types.BufferedInputFile(file_to_send.read(), filename="OCR_Result.txt"), caption="Результат OCR")

        # Удаляем сообщение загрузки, если обработка заняла мало времени
        if elapsed_time > 2:  # Если OCR длился долго, удаляем сообщение загрузки
            await loading_message.delete()
    except Exception as e:
        logger.error(f"Ошибка при отправке файла с результатом: {e}")
        await safe_edit_message(loading_message, "Произошла ошибка при отправке файла с результатом. Пожалуйста, попробуйте еще раз.")
    finally:
        os.remove(temp_file_path)

async def safe_edit_message(message: types.Message, text: str):
    """Безопасное редактирование сообщения с обработкой ошибок."""
    try:
        await message.edit_text(text, reply_markup=start_over_keyboard)
    except TelegramBadRequest as e:
        logger.warning(f"Ошибка при обновлении сообщения: {e}. Отправляю новое сообщение.")
        await message.answer(text, reply_markup=start_over_keyboard)

async def send_loading_message(loading_message: types.Message, base_text: str):
    """Анимация загрузки, которая прерывается, если OCR выполняется быстро."""
    dots = 0
    try:
        while True:
            dots = (dots + 1) % 4
            text = base_text + "." * dots
            await loading_message.edit_text(text, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[]]))
            await asyncio.sleep(0.5)
    except asyncio.CancelledError:
        pass  # Безопасное завершение при отмене
    except TelegramBadRequest as e:
        logger.warning(f"Ошибка при обновлении сообщения загрузки: {e}. Останавливаю обновление.")

def safe_remove(file_path):
    """Безопасное удаление файла с обработкой ошибок."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except PermissionError as e:
        logger.error(f"Ошибка при удалении файла {file_path}: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при удалении файла {file_path}: {e}")

async def process_document(file_path: str, file_name: str) -> str:
    """Определяет тип файла и вызывает соответствующую обработку."""
    if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
        return await process_image(file_path)
    elif file_name.lower().endswith('.pdf'):
        return await process_pdf(file_path)
    elif file_name.lower().endswith('.docx'):
        return await process_docx(file_path)
    else:
        raise ValueError("Формат файла не поддерживается.")
