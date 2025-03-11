import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import docx

def process_image(file_path):
    image = Image.open(file_path)
    return pytesseract.image_to_string(image)

def process_pdf(file_path):
    images = convert_from_path(file_path)
    text = ''
    for image in images:
        text += pytesseract.image_to_string(image)
    return text

def process_docx(file_path):
    doc = docx.Document(file_path)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text