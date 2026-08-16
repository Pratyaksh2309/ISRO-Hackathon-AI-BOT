import json
import ollama


def extract_triplets(text: str, max_chars: int = 3500):
    text = text[:max_chars]

    response = ollama.chat(
        model="qwen3:1.7b",
        think=False,
        format="json",
        messages=[
            {
                "role": "system",
                "content": """
Extract factual knowledge graph triplets from webpage text.

Return JSON only in this format:

{
  "triplets": [
    {
      "subject": "...",
      "relation": "...",
      "object": "..."
    }
  ]
}

Rules:
- Extract only facts explicitly present in the text.
- Keep subjects and objects concise.
- Maximum 10 triplets.
"""
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    data = json.loads(response.message.content)

    return data.get("triplets", [])