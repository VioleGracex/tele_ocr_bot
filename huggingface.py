import os
import requests
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/gpt3"

logger = logging.getLogger(__name__)

def analyze_text(text):
    headers = {
        'Authorization': f'Bearer {HUGGINGFACE_API_KEY}',  # Authentication using the Hugging Face API Key
        'Content-Type': 'application/json',
    }
    
    # The payload format required by Hugging Face inference API
    data = {
        "inputs": text  # Sending only the text for analysis
    }

    logger.info("Sending text to Hugging Face API for analysis")
    response = requests.post(HUGGINGFACE_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        try:
            logger.info("Received successful response from Hugging Face API")
            # Get the generated text from the response
            analysis_result = response.json()[0]['generated_text']
            return analysis_result
        except (IndexError, KeyError):
            logger.error("Error parsing response from Hugging Face API")
            return 'Analysis failed.'
    else:
        logger.error(f"Error from Hugging Face API: {response.status_code} {response.text}")
        return 'Error during text analysis.'