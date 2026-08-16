from playwright.sync_api import sync_playwright

from urllib.parse import urlparse

from io import BytesIO
from PIL import Image
from backend.app.ocr import extract_text_from_image

def is_same_site(base_url: str, target_url: str):
    return urlparse(base_url).netloc == urlparse(target_url).netloc

def crawl_page(url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page(
            viewport={"width": 1280, "height": 900}
        )

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=30000
        )

        page.wait_for_timeout(1500)

        text = page.locator("body").inner_text()

        ocr_text = ""

        # OCR fallback if DOM gives very little useful text
        if len(text.strip()) < 500:
        # if True:
            screenshot = page.screenshot(full_page=False)

            image = Image.open(BytesIO(screenshot))

            ocr_text = extract_text_from_image(image)

            if ocr_text.strip():
                text += "\n\nOCR CONTENT:\n" + ocr_text

        links = page.locator("a").evaluate_all("""
            els => els.map(a => ({
                text: (a.innerText || "").trim(),
                href: a.href
            }))
        """)

        data = {
            "url": url,
            "title": page.title(),
            "text": text,
            "ocr_text": ocr_text,
            "links": links
        }

        browser.close()

        return data
    
def crawl_site(start_url: str, max_pages: int = 5):
    visited = set()
    queue = [start_url]
    pages = []

    while queue and len(pages) < max_pages:
        url = queue.pop(0)

        if url in visited:
            continue

        visited.add(url)

        try:
            data = crawl_page(url)
            pages.append(data)

            for link in data["links"]:
                href = link.get("href")

                if (
                    href
                    and is_same_site(start_url, href)
                    and href not in visited
                    and href not in queue
                ):
                    queue.append(href)

        except Exception as e:
            print("CRAWL FAILED:", url, e)

    return pages