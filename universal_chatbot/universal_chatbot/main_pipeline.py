from web_scraper import scrape_page
from screenshot_ocr import extract_text_from_screenshot
from rebel_extractor import extract_triplets
from kg_builder import store_triplets, page_already_processed, mark_page_processed

def process_url(url):
    if page_already_processed(url):
        return

    html, screenshot_path = scrape_page(url)
    visual_text = extract_text_from_screenshot(screenshot_path)
    full_text = html + "\n" + visual_text

    triplets = extract_triplets(full_text)
    store_triplets(triplets, source=url)
    mark_page_processed(url)