from neo4j import GraphDatabase

URI = "neo4j://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "Agentic12345"

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)
driver.verify_connectivity()
with driver.session(database="neo4j") as session:
    result = session.run("RETURN 'NEO4J WORKING' AS message")
    print(result.single()["message"])

driver.close()