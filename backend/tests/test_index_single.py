import hashlib

from app.crawler import crawl_page
from app.knowledge_graph import (
    get_page,
    store_page,
    store_links,
    store_triplet,
)
from app.triplet_extractor import extract_triplets


url = "https://www.isro.gov.in/Vision-Mission-Objectives.html"

page = crawl_page(url)

content_hash = hashlib.sha256(
    page["text"].encode("utf-8")
).hexdigest()

existing = get_page(url)

if existing and existing.get("content_hash") == content_hash:
    print("ALREADY INDEXED")
else:
    store_page(
        page["url"],
        page["title"],
        page["text"],
        content_hash
    )

    store_links(page["url"], page["links"])

    triplets = extract_triplets(page["text"])

    for t in triplets:
        store_triplet(
            t["subject"],
            t["relation"],
            t["object"],
            page["url"]
        )

    print("INDEXED:", len(triplets), "triplets")