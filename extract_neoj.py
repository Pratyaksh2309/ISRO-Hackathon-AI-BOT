from neo4j import GraphDatabase

# === CONFIG ===
uri = "bolt://localhost:7687"
user = "neo4j"
password = "test123"
output_file = "RENET_DATA/train.txt"

driver = GraphDatabase.driver(uri, auth=(user, password))

def fetch_triples(tx):
    query = """
    MATCH (s)-[r]->(o)
    RETURN s.name AS subject, type(r) AS relation, o.name AS object, 
           COALESCE(r.timestamp, "0") AS timestamp
    """
    return tx.run(query)

with driver.session() as session, open(output_file, "w", encoding="utf-8") as f:
    result = session.read_transaction(fetch_triples)
    for record in result:
        line = f"{record['subject']}\t{record['relation']}\t{record['object']}\t{record['timestamp']}\n"
        f.write(line)

print(f"✅ Triples exported to {output_file}")
