# kg_builder.py
from neo4j import GraphDatabase

class KGNeo4j:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def insert_triplet(self, subject, relation, object_):
        with self.driver.session() as session:
            session.write_transaction(self._create_triplet, subject, relation, object_)

    @staticmethod
    def _create_triplet(tx, subject, relation, object_):
        query = (
            "MERGE (s:Entity {name: $subject}) "
            "MERGE (o:Entity {name: $object}) "
            "MERGE (s)-[r:RELATION {type: $relation}]->(o)"
        )
        tx.run(query, subject=subject, relation=relation, object=object_)
