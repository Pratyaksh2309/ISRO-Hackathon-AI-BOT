import pytesseract
from PIL import Image
import os

# Only needed if you're on Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def parse_screenshot(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        print(f"❌ Tesseract OCR failed on {image_path}: {e}")
        return ""
