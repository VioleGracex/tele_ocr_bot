import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

def analyze_text(text):
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        "input": {
            "contents": [{
                "parts": [{"text": text}]
            }]
        }
    }

    response = requests.post(GEMINI_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json().get('contents', [])[0].get('parts', [])[0].get('text', 'Анализ не удался')
    else:
        return 'Ошибка при анализе текста'