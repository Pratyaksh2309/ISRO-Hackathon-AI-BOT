from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from langchain.chat_models import ChatOpenAI
import os

# STEP 1: Configure Neo4j
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "aram12345"  # ← Replace with your real Neo4j password

# STEP 2: Setup the Graph
graph = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD
)

# STEP 3: Setup GPT model (you can also use env variable)
os.environ["OPENAI_API_KEY"] = "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"  # ← Replace with your OpenAI key

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

# STEP 4: Create the LangChain Cypher-based chatbot
chain = GraphCypherQAChain.from_llm(llm=llm, graph=graph, verbose=True)

# STEP 5: Ask Questions!
while True:
    question = input("Ask your KG Bot anything (or type 'exit'): ")
    if question.lower() == "exit":
        break
    result = chain.run(question)
    print("🤖:", result)
