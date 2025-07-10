import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import json
import time 

OUTPUT_DIR = "output/sitemap"
os.makedirs(OUTPUT_DIR, exist_ok=True)

from playwright.sync_api import sync_playwright
from urllib.parse import urljoin, urlparse

def get_internal_links_playwright(base_url, max_scrolls=1000, scroll_pause=1.5):
    internal_links = set()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(base_url, wait_until="domcontentloaded", timeout=60000)

        previous_height = 0
        for _ in range(max_scrolls):
            page.evaluate("window.scrollBy(0, window.innerHeight);")
            time.sleep(scroll_pause)
            new_height = page.evaluate("document.documentElement.scrollTop")
            if new_height == previous_height:
                break
            previous_height = new_height

        anchors = page.eval_on_selector_all("a", "els => els.map(a => a.href)")
        domain = urlparse(base_url).netloc

        for href in anchors:
            parsed = urlparse(href)
            if parsed.netloc == domain:
                clean_url = parsed.scheme + "://" + parsed.netloc + parsed.path
                internal_links.add(clean_url)

        browser.close()
    return list(internal_links)




def extract_page_title_or_header(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"⚠️ Failed to fetch {url}: {e}")
        return "⚠️ Error loading page"

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else None
    if title:
        return title

    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        return h1.get_text(strip=True)

    return "No title or header found"


def build_site_map(base_url, limit=25):
    internal_links = get_internal_links_playwright(base_url, max_scrolls=1000)

    site_map = {}

    for link in internal_links[:limit]:  # Limit to avoid deep crawling
        print(f"🔗 Crawling: {link}")
        label = extract_page_title_or_header(link)
        path = urlparse(link).path or "/"
        site_map[path] = {
            "title": label,
            "url": link
        }

    # Save to JSON
    output_path = os.path.join(OUTPUT_DIR, "site_map.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(site_map, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Site map saved to {output_path}")
    return site_map
