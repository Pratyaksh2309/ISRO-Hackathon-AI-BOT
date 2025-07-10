import os
import time
import uuid
from playwright.sync_api import sync_playwright

OUTPUT_DIR = "output/screenshots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def take_multiple_screenshots(url, max_scrolls=1000, scroll_pause=1.5):
    screenshots = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 720})
        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        previous_scroll = -1
        for i in range(max_scrolls):
            time.sleep(scroll_pause)

            screenshot_path = os.path.join(OUTPUT_DIR, f"{uuid.uuid4()}.png")
            page.screenshot(path=screenshot_path, full_page=False)
            screenshots.append(screenshot_path)
            print(f"[📸] Screenshot {i+1} saved to: {screenshot_path}")

            # Scroll down by 1 viewport height
            page.evaluate("window.scrollBy(0, window.innerHeight);")
            time.sleep(scroll_pause)
            time.sleep(2)

            # Get current scroll position
            current_scroll = page.evaluate("window.scrollY")
            if current_scroll == previous_scroll:
                print("✅ Reached bottom of page.")
                break
            previous_scroll = current_scroll

        browser.close()
    return screenshots
