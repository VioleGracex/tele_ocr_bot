import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_API_URL = "https://gemini.example.com/analyze"  # Replace with the actual URL if different

def analyze_text(text):
    headers = {
        'Authorization': f'Bearer {GEMINI_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        'text': text,
        'model': 'gpt-3',  # Adjust the model as needed
        'language': 'ru'  # Specify the language as Russian
    }

    response = requests.post(GEMINI_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json().get('analysis', 'Анализ не удался')
    else:
        return 'Ошибка при анализе текста'