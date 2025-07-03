# utils/renderer.py

import os
import uuid
from config import SCREENSHOT_DIR, PAGE_WIDTH, PAGE_HEIGHT, WAIT_TIME
from playwright.async_api import async_playwright
import asyncio

async def _render_page(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": PAGE_WIDTH, "height": PAGE_HEIGHT})
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
        except:
            await page.goto(url, wait_until="load", timeout=30000)

        # Scroll to bottom to trigger lazy load
        await page.evaluate("""window.scrollBy(0, document.body.scrollHeight);""")
        await page.wait_for_timeout(WAIT_TIME)

        # Remove common cookie popups
        await page.evaluate("""
            document.querySelectorAll('[id*="cookie"],[class*="cookie"]').forEach(e => e.remove());
        """)

        html = await page.content()

        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"{uuid.uuid4()}.png")
        await page.screenshot(path=screenshot_path, full_page=True)

        await browser.close()
        return html, screenshot_path

def render_website(url):
    return asyncio.run(_render_page(url))
