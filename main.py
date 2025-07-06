from utils.screenshot_capture import take_multiple_screenshots
from utils.parser_donut import parse_screenshot
from utils.dom_extractor import extract_visible_text
from utils.crawler import build_site_map
from utils.parse_screenshot_with_layout import analyze_ui_components
import json

if __name__ == "__main__":
    url = input("Enter a website URL to analyze: ").strip()

    # Take multiple viewport screenshots
    screenshots = take_multiple_screenshots(url, max_scrolls=3)

    for img_path in screenshots:
        print(f"\n🔍 Processing {img_path}")
        try:
            parsed_text = parse_screenshot(img_path)
            print("\n[🧠] Parsed Content from Donut / OCR:\n")
            print(parsed_text[:1000])

            ui_components = analyze_ui_components(img_path)
            print("\n🧩 UI Components Detected:")
            print(json.dumps(ui_components, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"❌ Error processing screenshot {img_path}: {e}")


    # Extract DOM-based visible text
    dom_text = extract_visible_text(url)
    print("\n[🌐] Visible DOM Text:\n")
    print(dom_text)
    
    print("\n🧭 Building full site map with titles...\n")
    site_map = build_site_map(url, limit=20)


