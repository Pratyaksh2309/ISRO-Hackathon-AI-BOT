from transformers import DonutProcessor, VisionEncoderDecoderModel
from PIL import Image
import torch
import os
from config import DONUT_MODEL

# Load model and processor once
processor = DonutProcessor.from_pretrained(DONUT_MODEL)
model = VisionEncoderDecoderModel.from_pretrained(DONUT_MODEL)
model.eval()

if torch.cuda.is_available():
    model.to("cuda")

def parse_screenshot(image_path):
    """
    Uses Donut model to extract structured content from screenshot image.
    Returns predicted text.
    """
    image = Image.open(image_path).convert("RGB")
    pixel_values = processor(images=image, return_tensors="pt").pixel_values

    if torch.cuda.is_available():
        pixel_values = pixel_values.to("cuda")

    task_prompt = "<s_docvqa><s_question>What is the structured content in this document?<s_answer>"
    decoder_input_ids = processor.tokenizer(task_prompt, add_special_tokens=False, return_tensors="pt").input_ids

    if torch.cuda.is_available():
        decoder_input_ids = decoder_input_ids.to("cuda")

    outputs = model.generate(
        pixel_values,
        decoder_input_ids=decoder_input_ids,
        max_length=512,
        early_stopping=True,
        pad_token_id=processor.tokenizer.pad_token_id,
        eos_token_id=processor.tokenizer.eos_token_id,
        use_cache=True,
        num_beams=2,
    )

    result = processor.batch_decode(outputs, skip_special_tokens=True)[0]
    result = result.replace("<s_answer>", "").strip()
    return result
