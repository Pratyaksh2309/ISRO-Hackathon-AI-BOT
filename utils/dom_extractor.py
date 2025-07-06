from playwright.sync_api import sync_playwright

def extract_visible_text(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # Main visible text
        full_text = page.evaluate("""
            () => {
                const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                let text = "";
                while (walker.nextNode()) {
                    const node = walker.currentNode;
                    if (node.nodeValue.trim().length > 0) {
                        text += node.nodeValue.trim() + " ";
                    }
                }
                return text;
            }
        """)

        # Semantic elements (article, section, nav, headers)
        semantic_tags = page.evaluate("""
            () => {
                const elements = document.querySelectorAll("article, section, nav, header, h1, h2, h3");
                return Array.from(elements).map(el => ({
                    tag: el.tagName,
                    text: el.innerText.slice(0, 300)  // trim long blocks
                }));
            }
        """)

        # All links
        links = page.evaluate("""
            () => {
                const anchors = Array.from(document.querySelectorAll("a"));
                return anchors
                    .filter(a => a.href && a.innerText.trim().length > 0)
                    .map(a => ({ text: a.innerText.trim().slice(0, 100), href: a.href }));
            }
        """)

        browser.close()

        return {
            "visible_text": full_text.strip(),
            "semantic_tags": semantic_tags,
            "links": links
        }
