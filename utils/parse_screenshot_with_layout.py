import pytesseract
from PIL import Image
import os
import uuid
import json
from pytesseract import Output
from config import PARSED_OUTPUT_DIR

os.makedirs(PARSED_OUTPUT_DIR, exist_ok=True)

def analyze_ui_components(image_path):
    image = Image.open(image_path)

    # Run OCR with layout info
    data = pytesseract.image_to_data(image, output_type=Output.DICT)

    results = {
        "headings": [],
        "buttons": [],
        "menu_items": [],
        "raw_text_blocks": [],
    }

    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        if not text:
            continue

        conf = int(data['conf'][i])
        if conf < 50:
            continue  # skip low confidence

        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
        block = {
            "text": text,
            "bbox": [x, y, x + w, y + h],
            "conf": conf
        }

        # Heuristic classification
        if text.lower() in {"home", "about", "services", "contact", "login", "sign in"} or w > 100 and h < 50:
            results["menu_items"].append(block)
        elif text.lower() in {"submit", "apply", "read more", "download"} or (w > 60 and h > 30 and w < 200):
            results["buttons"].append(block)
        elif text.isupper() or (len(text.split()) <= 5 and h > 30):
            results["headings"].append(block)
        else:
            results["raw_text_blocks"].append(block)

    # Save
    output_path = os.path.join(PARSED_OUTPUT_DIR, f"layout_{uuid.uuid4()}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    return results
