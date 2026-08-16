import ollama


def search_current_page(query: str) -> str:
    return "INSAT-3D is used for meteorological observations and weather monitoring."


messages = [
    {
        "role": "user",
        "content": "Use the available tool to find what INSAT-3D is used for."
    }
]

response = ollama.chat(
    model="qwen3:4b",
    messages=messages,
    tools=[search_current_page]
)

messages.append(response.message)

if response.message.tool_calls:
    for call in response.message.tool_calls:
        if call.function.name == "search_current_page":
            result = search_current_page(**call.function.arguments)

            messages.append({
                "role": "tool",
                "tool_name": call.function.name,
                "content": result
            })

final_response = ollama.chat(
    model="qwen3:4b",
    messages=messages,
    tools=[search_current_page]
)

print(final_response.message.content)