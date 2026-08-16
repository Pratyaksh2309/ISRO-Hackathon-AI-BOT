from backend.app.knowledge_graph import search_graph, search_links, search_pages
import hashlib

from backend.app.crawler import crawl_page
from backend.app.knowledge_graph import (
    search_graph,
    search_pages,
    search_links,
    get_page,
    store_page,
    store_links,
    store_triplet
)
from backend.app.triplet_extractor import extract_triplets
from backend.app.rebel_extractor import extract_rebel_triplets

def search_knowledge_graph(query: str, current_url=None) -> str:
    """Search structured knowledge graph facts from the website."""

    results = search_graph(
        query,
        current_url=current_url,
        limit=8
    )

    if not results:
        return "NO_RELEVANT_KG_FACTS"

    return "\n".join(
        f"{x['subject']} --{x['relation']}--> {x['object']} "
        f"| Source: {x['source']}"
        for x in results
    )

def find_relevant_links(query: str, current_url=None) -> str:
    """Find relevant internal website links that the browser can navigate to."""

    results = search_links(
        query,
        current_url=current_url,
        limit=8
    )

    if not results:
        return "No relevant internal links found."

    return "\n".join(
        f"TITLE: {x.get('title')}\n"
        f"LINK TEXT: {x.get('link_text')}\n"
        f"URL: {x['url']}"
        for x in results
    )
    
def search_indexed_site(query: str, current_url=None) -> str:
    """Search already indexed website pages."""

    results = search_pages(
        query,
        current_url=current_url,
        limit=5
    )

    if not results:
        return "NO_RELEVANT_INDEXED_PAGE"

    query_words = {
        w.strip("?!.,").lower()
        for w in query.split()
        if len(w.strip("?!.,"))
        > 3
    }

    useful = []

    for x in results:
        text = (
            str(x.get("title", "")) + " " +
            str(x.get("text", ""))
        ).lower()

        score = sum(
            1 for w in query_words
            if w in text
        )

        if score >= 2:
            useful.append(x)

    if not useful:
        return "NO_RELEVANT_INDEXED_PAGE"

    return "\n\n".join(
        f"TITLE: {x['title']}\n"
        f"URL: {x['url']}\n"
        f"TEXT:\n{x['text'][:2200]}"
        for x in useful[:1]
    )
    
def navigate_to_page(query: str, current_url=None) -> str:
    """
    Find the best internal page for a navigation request.
    """

    results = search_links(
        query,
        current_url=current_url,
        limit=10
    )

    if not results:
        return "NO_NAVIGATION_TARGET"

    query_lower = query.lower()

    for result in results:
        text = (
            str(result.get("title", "")) + " " +
            str(result.get("link_text", "")) + " " +
            str(result.get("url", ""))
        ).lower()

        if "career" in query_lower and "career" in text:
            return result["url"]

    return results[0]["url"]


def crawl_and_index_page(query: str, current_url=None) -> str:
    """
    Find a relevant internal unindexed page, crawl it,
    build KG facts, and return its content.
    """

    links = search_links(
        query,
        current_url=current_url,
        limit=10
    )

    if not links:
        return "NO_RELEVANT_PAGE_FOUND"

    target = None

    for link in links:
        url = link["url"]

        existing = get_page(url)

        if not existing or not existing.get("text"):
            target = url
            break

    if target is None:
        target = links[0]["url"]

    print("AGENT CRAWLING:", target, flush=True)

    page = crawl_page(target)

    content_hash = hashlib.sha256(
        page["text"].encode("utf-8")
    ).hexdigest()

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

    llm_triplets = extract_triplets(page["text"])

    rebel_triplets = extract_rebel_triplets(
        page["text"][:2500]
    )

    for t in llm_triplets + rebel_triplets:
        store_triplet(
            t["subject"],
            t["relation"],
            t["object"],
            page["url"]
        )

    return (
        f"INDEXED PAGE: {page['title']}\n"
        f"URL: {page['url']}\n"
        f"CONTENT:\n{page['text'][:3000]}"
    )