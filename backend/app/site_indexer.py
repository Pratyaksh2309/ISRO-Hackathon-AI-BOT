import hashlib

from app.crawler import crawl_site
from app.knowledge_graph import (
    get_page,
    store_page,
    store_links,
    store_triplet,
)
from app.triplet_extractor import extract_triplets
from backend.app.rebel_extractor import extract_rebel_triplets

def index_site(start_url: str, max_pages: int = 3):
    pages = crawl_site(start_url, max_pages=max_pages)

    results = []

    for page in pages:
        content_hash = hashlib.sha256(
            page["text"].encode("utf-8")
        ).hexdigest()

        existing = get_page(page["url"])

        if (
            existing
            and existing.get("content_hash") == content_hash
        ):
            print("SKIPPING:", page["url"])
            results.append((page["url"], "skipped"))
            continue

        print("INDEXING:", page["url"])

        store_page(
            page["url"],
            page["title"],
            page["text"],
            content_hash
        )

        store_links(
            page["url"],
            page["links"]
        )

        triplets = extract_triplets(page["text"])
        rebel_triplets = extract_rebel_triplets(
            page["text"][:2500]
        )

        for t in triplets:
            store_triplet(
                t["subject"],
                t["relation"],
                t["object"],
                page["url"]
            )

        for t in rebel_triplets:
            store_triplet(
                t["subject"],
                t["relation"],
                t["object"],
                page["url"]
            )

        results.append(
            (
                page["url"],
                f"{len(triplets)} LLM triplets + "
                f"{len(rebel_triplets)} REBEL triplets"
            )
        )

    return results