from neo4j import GraphDatabase
import json

# Load extracted triples from JSON file
with open("triples.json", "r", encoding="utf-8") as f:
    triples = json.load(f)

# Neo4j connection info
uri = "bolt://localhost:7687"  # default
username = "neo4j"
password = "aram12345"  # change if you set a custom password

# Connect to Neo4j
driver = GraphDatabase.driver(uri, auth=(username, password))

def insert_triples(tx, subject, relation, obj):
    tx.run("""
        MERGE (s:Entity {name: $subject})
        MERGE (o:Entity {name: $object})
        MERGE (s)-[:%s]->(o)
    """ % relation.replace(" ", "_"), subject=subject, object=obj)

with driver.session() as session:
    for triple in triples:
        subject, relation, obj = triple
        session.write_transaction(insert_triples, subject, relation, obj)

driver.close()
print("✅ Triples inserted into Neo4j!")
