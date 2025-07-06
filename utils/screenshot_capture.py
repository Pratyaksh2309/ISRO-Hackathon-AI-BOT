import os
import time
import uuid
from playwright.sync_api import sync_playwright
from PIL import Image

OUTPUT_DIR = "output/screenshots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def take_multiple_screenshots(url, max_scrolls=10, scroll_pause=1.5):
    screenshots = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        previous_height = 0
        for i in range(max_scrolls):
            time.sleep(scroll_pause)
            screenshot_path = os.path.join(OUTPUT_DIR, f"{uuid.uuid4()}.png")
            page.screenshot(path=screenshot_path, full_page=False)
            screenshots.append(screenshot_path)
            print(f"[📸] Screenshot {i+1} saved to: {screenshot_path}")

            # Scroll down by 1 viewport height
            page.evaluate("window.scrollBy(0, window.innerHeight);")
            new_height = page.evaluate("document.documentElement.scrollTop")
            if new_height == previous_height:
                print("✅ Reached bottom of page.")
                break
            previous_height = new_height

        browser.close()
    return screenshots
