import logging
import easyocr
from PIL import Image
import docx

logger = logging.getLogger(__name__)

# Initialize the easyocr reader
reader = easyocr.Reader(['en', 'ru'])  # Specify the languages you want to use

def process_image(file_path):
    logger.info(f"Starting OCR for image: {file_path}")
    results = reader.readtext(file_path)
    text = '\n'.join([text for (bbox, text, prob) in results])
    logger.info(f"OCR completed for image: {file_path}")
    return text

def process_pdf(file_path):
    logger.info(f"Starting OCR for PDF: {file_path}")
    # Extract text from PDF using easyocr
    text = ''
    results = reader.readtext(file_path, detail=0)
    text = '\n'.join(results)
    logger.info(f"OCR completed for PDF: {file_path}")
    return text

def process_docx(file_path):
    logger.info(f"Starting OCR for DOCX: {file_path}")
    doc = docx.Document(file_path)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    logger.info(f"OCR completed for DOCX: {file_path}")
    return text