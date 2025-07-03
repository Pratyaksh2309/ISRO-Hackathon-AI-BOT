# utils/parser_donut.py

from transformers import DonutProcessor, VisionEncoderDecoderModel
from PIL import Image
from config import DONUT_MODEL, PARSED_OUTPUT_DIR
import os
import uuid

# Load Donut model once
processor = DonutProcessor.from_pretrained(DONUT_MODEL)
model = VisionEncoderDecoderModel.from_pretrained(DONUT_MODEL)

def parse_screenshot(image_path: str) -> str:
    image = Image.open(image_path).convert("RGB")
    inputs = processor(image, return_tensors="pt")
    outputs = model.generate(**inputs)
    result = processor.batch_decode(outputs, skip_special_tokens=True)[0]

    # Save output
    os.makedirs(PARSED_OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(PARSED_OUTPUT_DIR, f"{uuid.uuid4()}.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)

    return result
