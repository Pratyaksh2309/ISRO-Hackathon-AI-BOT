from app.crawler import crawl_page

data = crawl_page(
    "https://www.isro.gov.in/Vision-Mission-Objectives.html"
)

print("TITLE:", data["title"])
print("CHARACTERS:", len(data["text"]))
print("LINKS:", len(data["links"]))
print(data["text"][:500])