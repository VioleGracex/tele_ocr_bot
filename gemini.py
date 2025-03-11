import os
import requests
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

logger = logging.getLogger(__name__)

def analyze_text(text):
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": text}
                ]
            }
        ]
    }

    logger.info("Sending text to Gemini API for analysis")
    response = requests.post(GEMINI_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        try:
            logger.info("Received successful response from Gemini API")
            return response.json().get('candidates', [])[0].get('content', {}).get('parts', [])[0].get('text', 'Анализ не удался')
        except (IndexError, KeyError):
            logger.error("Error parsing response from Gemini API")
            return 'Анализ не удался'
    else:
        logger.error(f"Error from Gemini API: {response.status_code} {response.text}")
        return 'Ошибка при анализе текста'