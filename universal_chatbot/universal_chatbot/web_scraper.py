from playwright.sync_api import sync_playwright
import os

def scrape_page(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        html = page.content()

        os.makedirs("screenshots", exist_ok=True)
        screenshot_path = f"screenshots/{url.replace('https://','').replace('http://','').replace('/', '_')}.png"
        page.screenshot(path=screenshot_path, full_page=True)

        browser.close()
        return html, screenshot_path