# utils/dom_helper.py

from bs4 import BeautifulSoup

def extract_visible_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Filter out script/style
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)
