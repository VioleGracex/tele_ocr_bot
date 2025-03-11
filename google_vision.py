import os
from google.cloud import vision

def recognize_text(file_path):
    client = vision.ImageAnnotatorClient()
    
    with open(file_path, 'rb') as image_file:
        content = image_file.read()
    
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    if response.error.message:
        raise Exception(f'{response.error.message}')
    
    if texts:
        return texts[0].description
    else:
        return 'Текст не распознан'