from playwright.sync_api import sync_playwright

def get_rendered_html(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Use headless=False to see the browser open
        page = browser.new_page()
        print(f"Visiting: {url}")
        page.goto(url, wait_until="networkidle")      # Wait for JS to load
        html = page.content()
        browser.close()
        return html

if __name__ == "__main__":
    test_url = input("Enter website URL: ")
    html_content = get_rendered_html(test_url)

    # Save output for inspection
    with open("output_test.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("✅ HTML content saved to output_test.html")
