import ollama

response = ollama.embed(
    model="qwen3-embedding:0.6b",
    input="Agentic browser assistant for website question answering"
)

print(len(response.embeddings[0]))
print(response.embeddings[0][:5])