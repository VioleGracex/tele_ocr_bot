import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GPTUNNEL_API_URL = os.getenv('GPTUNNEL_API_URL')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def analyze_text(text):
    headers = {
        'Authorization': f'Bearer {GEMINI_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        'text': text,
        'model': 'gpt-4'
    }
    
    response = requests.post(GPTUNNEL_API_URL, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json().get('analysis', 'Анализ не удался')
    else:
        return 'Ошибка при анализе текста'