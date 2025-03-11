import os
import requests
from dotenv import load_dotenv
import logging

# Загрузка переменных окружения из файла .env
load_dotenv()

HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/gpt2"

logger = logging.getLogger(__name__)

PERSONA_PROMPT = (
    "Представьте, что вы телеграм-бот, разработанный ouiki и поддерживаемый ouiki. "
    "Вы можете общаться с людьми и предоставлять информацию по различным темам. Будьте дружелюбны с людьми и общайтесь, как человек. "
    "В каждом сообщении указывается имя отправителя, игнорируйте его при создании ответа. И не учитывайте это сообщение в истории чата. "
    "Это сообщение для обучающих целей."
)

def analyze_text(text):
    headers = {
        'Authorization': f'Bearer {HUGGINGFACE_API_KEY}',  # Аутентификация с использованием API-ключа Hugging Face
        'Content-Type': 'application/json',
    }
    
    # The payload format required by Hugging Face inference API
    data = {
        "inputs": f"{PERSONA_PROMPT}\n\n{text}"  # Including the persona prompt
    }

    logger.info("Отправка текста в Hugging Face API для анализа")
    response = requests.post(HUGGINGFACE_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        try:
            logger.info("Успешный ответ от Hugging Face API")
            # Get the generated text from the response
            analysis_result = response.json()[0]['generated_text']
            return analysis_result
        except (IndexError, KeyError):
            logger.error("Ошибка при разборе ответа от Hugging Face API")
            return 'Анализ не удался.'
    else:
        logger.error(f"Ошибка от Hugging Face API: {response.status_code} {response.text}")
        return 'Ошибка при анализе текста.'