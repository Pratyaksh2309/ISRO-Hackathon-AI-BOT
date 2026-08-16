import ollama

from app.agent_tools import (
    search_knowledge_graph,
    search_indexed_site
)


messages = [
    {
        "role": "system",
        "content": """
You are an agent that answers questions about a website.

You have tools for:
1. searching structured knowledge graph facts
2. searching indexed website pages

Use a tool whenever needed.
"""
    },
    {
        "role": "user",
        "content": "What is ISRO's vision?"
    }
]


response = ollama.chat(
    model="qwen3:1.7b",
    think=False,
    messages=messages,
    tools=[
        search_knowledge_graph,
        search_indexed_site
    ]
)

print("TOOL CALLS:", response.message.tool_calls)

if response.message.tool_calls:

    messages.append(response.message)

    for call in response.message.tool_calls:

        if call.function.name == "search_knowledge_graph":
            result = search_knowledge_graph(
                **call.function.arguments
            )

        elif call.function.name == "search_indexed_site":
            result = search_indexed_site(
                **call.function.arguments
            )

        else:
            continue

        print("\nTOOL:", call.function.name)
        print("RESULT:", result[:500])

        messages.append({
            "role": "tool",
            "tool_name": call.function.name,
            "content": result
        })

    final = ollama.chat(
        model="qwen3:1.7b",
        think=False,
        messages=messages,
        tools=[
            search_knowledge_graph,
            search_indexed_site
        ]
    )

    print("\nFINAL ANSWER:")
    print(final.message.content)