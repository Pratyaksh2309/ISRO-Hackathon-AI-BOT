from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.vectorstores import Neo4jVector
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.graphs import Neo4jGraph

graph = Neo4jGraph(url="bolt://localhost:7687", username="neo4j", password="yourStrongPass123")

def ask_question(query):
    # Naive version: keyword search from KG
    try:
        results = graph.query(f'''
            MATCH (s:Entity)-[r]->(o:Entity)
            WHERE toLower(s.name) CONTAINS toLower("{query}") OR toLower(o.name) CONTAINS toLower("{query}")
            RETURN s.name + " --[" + type(r) + "]--> " + o.name AS triplet
            LIMIT 5
        ''')
        if results:
            return "\n".join([r['triplet'] for r in results])
        else:
            return "🤔 I couldn't find a direct answer in the KG."
    except Exception as e:
        return str(e)