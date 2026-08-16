from io import BytesIO

from PIL import Image
from playwright.sync_api import sync_playwright

from app.ocr import extract_text_from_image


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page(
        viewport={"width": 1280, "height": 900}
    )

    page.goto(
        "https://www.isro.gov.in/",
        wait_until="domcontentloaded",
        timeout=30000
    )

    page.wait_for_timeout(1500)

    screenshot = page.screenshot(full_page=False)

    browser.close()


image = Image.open(BytesIO(screenshot))

text = extract_text_from_image(image)

print("OCR LENGTH:", len(text))

print("\nOCR SAMPLE:")
print(text[:1000])