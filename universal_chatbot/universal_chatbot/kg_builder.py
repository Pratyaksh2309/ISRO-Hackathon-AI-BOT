from py2neo import Graph
import json

graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))

def store_triplets(triplets, source=None):
    for subj, rel, obj in triplets:
        query = f"""
        MERGE (s:Entity {{name: $subj}})
        MERGE (o:Entity {{name: $obj}})
        MERGE (s)-[r:{rel.replace(" ", "_").upper()}]->(o)
        """
        graph.run(query, subj=subj, obj=obj)

def page_already_processed(url):
    try:
        with open("universal_chatbot/visited_pages.json", "r") as f:
            pages = json.load(f)
    except:
        return False
    return url in pages

def mark_page_processed(url):
    try:
        with open("universal_chatbot/visited_pages.json", "r") as f:
            pages = json.load(f)
    except:
        pages = []
    pages.append(url)
    with open("universal_chatbot/visited_pages.json", "w") as f:
        json.dump(list(set(pages)), f, indent=2)