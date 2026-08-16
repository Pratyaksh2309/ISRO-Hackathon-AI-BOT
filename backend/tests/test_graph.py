from app.knowledge_graph import store_page, store_triplet

store_page(
    "https://example.com",
    "Example Website"
)

store_triplet(
    "INSAT-3D",
    "used for",
    "meteorological observations",
    "https://example.com"
)

print("GRAPH DATA STORED")