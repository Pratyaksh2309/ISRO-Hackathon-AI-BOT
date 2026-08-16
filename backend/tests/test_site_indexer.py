from app.site_indexer import index_site

results = index_site(
    "https://www.isro.gov.in/",
    max_pages=3
)

for result in results:
    print(result)