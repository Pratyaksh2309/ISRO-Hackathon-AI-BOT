from utils.screenshot_capture import take_multiple_screenshots
# from utils.parser_donut import parse_screenshot
from utils.dom_extractor import extract_visible_text
from utils.crawler import build_site_map
from utils.parse_screenshot_with_layout import analyze_ui_components
import json
from utils.rebel_extractor import extract_triplets
from transformers import pipeline
from utils.parser_tesseract import parse_screenshot


if __name__ == "__main__":
    url = input("Enter a website URL to analyze: ").strip()

    # Take multiple viewport screenshots
    screenshots = take_multiple_screenshots(url, max_scrolls=1000)
    rephraser = pipeline("text2text-generation", model="google/flan-t5-base")
    all_triplets = []

    for img_path in screenshots:
        print(f"\n🔍 Processing {img_path}")
        try:
            # OCR text
            ocr_text = parse_screenshot(img_path).replace("\n", " ").strip()

            # UI layout components from screenshot
            layout_info = analyze_ui_components(img_path)
            layout_texts = []
            for block_type, blocks in layout_info.items():
                for block in blocks:
                    layout_texts.append(f"{block_type[:-1].capitalize()}: {block['text']}")

            layout_text = " | ".join(layout_texts)

            # DOM visible text and semantic tags
            scroll_offset = 0  # Optional: match screenshot scroll if tracked
            dom_result = extract_visible_text(url, scroll_offset=scroll_offset)
            dom_text = dom_result['visible_text']
            semantic_texts = [f"{tag['tag']}: {tag['text']}" for tag in dom_result['semantic_tags']]
            semantic_summary = " | ".join(semantic_texts)

            # 🔀 Merge all parts
            merged_text = f"{ocr_text} | {layout_text} | {dom_text} | {semantic_summary}".strip()


            if merged_text:
                prompt = f"Convert this UI/website text into a clear factual sentence: {merged_text}"
                rephrased = rephraser(prompt, max_length=1200, truncation=True, do_sample=False)[0]['generated_text']
                print("\n📝 Rephrased Text for REBEL:\n", rephrased)
            else:
                rephrased = ""

            triplets = extract_triplets(rephrased)
            for t in triplets:
                print(f"  → ({t['subject']} | {t['relation']} | {t['object']})")

            all_triplets.extend(triplets)

        except Exception as e:
            print(f"❌ Error processing screenshot {img_path}: {e}")

    
    # print("\n🧠 All Triplets Across Screenshots:\n")
    # unique_triplets = []
    # seen = set()
    # for t in all_triplets:
    #     key = (t['subject'].lower(), t['relation'].lower(), t['object'].lower())
    #     if key not in seen:
    #         seen.add(key)
    #         unique_triplets.append(t)

    # print(json.dumps(unique_triplets, indent=2, ensure_ascii=False))



    # Extract DOM-based visible text
    dom_text = extract_visible_text(url)
    print("\n[🌐] Visible DOM Text:\n")
    print(dom_text)
    
    print("\n🧭 Building full site map with titles...\n")
    site_map = build_site_map(url, limit=50)
    
    from kg_builder import KGNeo4j

    kg = KGNeo4j("bolt://localhost:7687", "neo4j", "test123")

    for triplet in all_triplets:
        subj = triplet['subject']
        rel = triplet['relation']
        obj = triplet['object']
        kg.insert_triplet(subj, rel, obj)

    kg.close()



