import logging
import easyocr
import fitz  # PyMuPDF
import os
import docx
import time

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
    text = []

    # Open the PDF file
    document = fitz.open(file_path)

    for page_num in range(len(document)):
        # Get the page
        page = document.load_page(page_num)
        # Convert the page to an image
        pix = page.get_pixmap()
        img_path = f"{file_path}_page_{page_num}.png"
        pix.save(img_path)
        
        # Perform OCR on the image
        page_text = reader.readtext(img_path, detail=0)
        text.extend(page_text)
        
        # Remove the image file after processing
        remove_file_with_retry(img_path)
    
    logger.info(f"OCR completed for PDF: {file_path}")
    return '\n'.join(text)

def process_docx(file_path):
    logger.info(f"Starting OCR for DOCX: {file_path}")
    doc = docx.Document(file_path)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    logger.info(f"OCR completed for DOCX: {file_path}")
    return text

def remove_file_with_retry(file_path, retries=3, delay=1):
    """
    Attempts to remove a file with retries if it is being used by another process.
    
    :param file_path: Path to the file to be removed.
    :param retries: Number of retries to attempt.
    :param delay: Delay between retries in seconds.
    """
    for attempt in range(retries):
        try:
            os.remove(file_path)
            logger.info(f"Successfully removed file: {file_path}")
            return
        except PermissionError as e:
            logger.warning(f"PermissionError when trying to remove file: {file_path}. Retrying in {delay} seconds...")
            time.sleep(delay)
    logger.error(f"Failed to remove file after {retries} attempts: {file_path}")