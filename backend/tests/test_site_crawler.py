from app.crawler import crawl_site

pages = crawl_site(
    "https://www.isro.gov.in/",
    max_pages=3
)

for p in pages:
    print(p["title"], "-", p["url"])