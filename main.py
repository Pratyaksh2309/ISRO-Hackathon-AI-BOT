# main.py

from utils.renderer import render_website
from utils.parser_donut import parse_screenshot
from utils.dom_helper import extract_visible_text  # Optional

url = input("Enter a website URL to analyze: ").strip()

# Step 1A: Render page & screenshot
html, screenshot_path = render_website(url)
print(f"[✔] Screenshot saved to: {screenshot_path}")

# Step 1B: Parse screenshot with Donut
parsed = parse_screenshot(screenshot_path)
print("\n[🧠] Parsed Content from Donut:\n")
print(parsed[:1000])  # Truncate for readability

# (Optional) Print visible HTML text
print("\n[🌐] Visible DOM Text:\n")
print(extract_visible_text(html)[:1000])
