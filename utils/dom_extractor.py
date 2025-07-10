from playwright.sync_api import sync_playwright

def extract_visible_text(url, scroll_offset=0, viewport_height=900):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": viewport_height})
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # Scroll to match the screenshot
        page.evaluate(f"() => window.scrollTo(0, {scroll_offset})")

        # Collect all visible text nodes within the current viewport
        visible_text_in_viewport = page.evaluate(f"""
            () => {{
                const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                let visibleText = "";

                while (walker.nextNode()) {{
                    const node = walker.currentNode;
                    const parent = node.parentElement;
                    if (!parent) continue;

                    const style = window.getComputedStyle(parent);
                    const rect = parent.getBoundingClientRect();

                    const isVisible = (
                        rect.top >= 0 &&
                        rect.bottom <= window.innerHeight &&
                        style.visibility !== "hidden" &&
                        style.display !== "none"
                    );

                    if (isVisible && node.nodeValue.trim().length > 0) {{
                        visibleText += node.nodeValue.trim() + " ";
                    }}
                }}
                return visibleText.trim();
            }}
        """)

        # Optionally extract visible semantic blocks and links in the viewport
        semantic_tags = page.evaluate("""
            () => {
                const elements = document.querySelectorAll("article, section, nav, header, h1, h2, h3");
                return Array.from(elements).map(el => {
                    const rect = el.getBoundingClientRect();
                    if (
                        rect.top >= 0 &&
                        rect.bottom <= window.innerHeight &&
                        window.getComputedStyle(el).display !== "none"
                    ) {
                        return {
                            tag: el.tagName,
                            text: el.innerText.slice(0, 300)
                        };
                    }
                    return null;
                }).filter(e => e !== null);
            }
        """)

        browser.close()

        return {
            "visible_text": visible_text_in_viewport.strip(),
            "semantic_tags": semantic_tags,
        }
