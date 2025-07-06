import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SCREENSHOT_DIR = os.path.join(BASE_DIR, "output", "screenshots")
PARSED_OUTPUT_DIR = os.path.join(BASE_DIR, "output", "parsed")
DOM_OUTPUT_DIR = os.path.join(BASE_DIR, "output", "dom_texts")

DONUT_MODEL = "naver-clova-ix/donut-base-finetuned-docvqa"
