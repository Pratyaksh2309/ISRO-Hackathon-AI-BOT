from fastapi import FastAPI
from pydantic import BaseModel
import ollama
import numpy as np
from backend.app.triplet_extractor import extract_triplets
from backend.app.knowledge_graph import (
    store_page,
    store_triplet,
    search_graph,
    get_page,
    store_links,
    search_pages,
    search_links
)

from fastapi.middleware.cors import CORSMiddleware

from backend.app.rebel_extractor import extract_rebel_triplets
from backend.app.agent_tools import (
    search_knowledge_graph,
    search_indexed_site,
    find_relevant_links,
    navigate_to_page,
    crawl_and_index_page
)
import hashlib

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LinkData(BaseModel):
    text: str
    href: str


class PageData(BaseModel):
    url: str
    title: str
    text: str
    links: list[LinkData] = []

class Question(BaseModel):
    question: str
    current_url: str | None = None

CURRENT_PAGE = {}

@app.get("/")
def root():
    return {"status": "Agentic Web Copilot backend working"}

@app.post("/ingest")
def ingest_page(page: PageData):
    global CURRENT_PAGE
    
    content_hash = hashlib.sha256(page.text.encode("utf-8")).hexdigest()

    existing_page = get_page(page.url)

    if (existing_page and existing_page.get("content_hash") == content_hash):
        CURRENT_PAGE = existing_page
        
        print("PAGE UNCHANGED - SKIPPING EXTRACTION", flush=True)

        return {
            "status": "already indexed",
            "title": existing_page["title"],
            "characters": len(existing_page["text"]),
            "triplets_stored": 0
        }

    CURRENT_PAGE = page.model_dump()

    store_page(page.url, page.title, page.text,content_hash)
    
    store_links(
        page.url,
        [link.model_dump() for link in page.links]
    )

    triplets = extract_triplets(page.text)
    rebel_triplets = extract_rebel_triplets(
        page.text[:2500]
    )

    for t in triplets:
        store_triplet(
            t["subject"],
            t["relation"],
            t["object"],
            page.url
        )
    for t in rebel_triplets:
        store_triplet(
            t["subject"],
            t["relation"],
            t["object"],
            page.url
        )
    print("NEW PAGE - INDEXING AND EXTRACTING TRIPLETS", flush=True)
    return {
        "status": "indexed",
        "title": page.title,
        "characters": len(page.text),
        "llm_triplets": len(triplets),
        "rebel_triplets": len(rebel_triplets)
    }
    
import re


def chunk_text(text, chunk_size=2000):
    paragraphs = text.split("\n")

    chunks = []
    current = ""

    for paragraph in paragraphs:
        if len(current) + len(paragraph) > chunk_size:
            if current.strip():
                chunks.append(current.strip())
            current = paragraph
        else:
            current += "\n" + paragraph

    if current.strip():
        chunks.append(current.strip())

    return chunks


def retrieve_chunks(text, question, top_k=3):
    chunks = chunk_text(text)

    chunk_embeddings = ollama.embed(
        model="qwen3-embedding:0.6b",
        input=chunks
    ).embeddings

    question_embedding = ollama.embed(
        model="qwen3-embedding:0.6b",
        input=question
    ).embeddings[0]

    q = np.array(question_embedding)

    scored = []

    for chunk, emb in zip(chunks, chunk_embeddings):
        e = np.array(emb)

        similarity = np.dot(q, e) / (
            np.linalg.norm(q) * np.linalg.norm(e)
        )

        scored.append((similarity, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [chunk for score, chunk in scored[:top_k]]

import re

@app.post("/ask")
def ask(question: Question):
    print("ASK HIT:", question.question, flush=True)
    print("CURRENT WEBSITE:", question.current_url, flush=True)

    navigation_url = None
    source_url = None
    
    q_lower = question.question.lower()

    navigation_intent = any(
        phrase in q_lower
        for phrase in [
            "take me to",
            "open ",
            "go to",
            "navigate to"
        ]
    )
    
    if navigation_intent:
        tools = [
            find_relevant_links,
            navigate_to_page
        ]
    else:
        tools = [
            search_knowledge_graph,
            search_indexed_site,
            crawl_and_index_page
        ]

    # tools = [
    #     search_knowledge_graph,
    #     search_indexed_site,
    #     find_relevant_links,
    #     navigate_to_page,
    #     crawl_and_index_page
    # ]

    messages = [
        {
            "role": "system",
            "content": """
You are an autonomous website research agent.

You MUST answer only using website evidence obtained through tools.

Available tools:
- search_knowledge_graph: search structured facts already extracted
- search_indexed_site: search pages already indexed
- find_relevant_links: find internal website links
- crawl_and_index_page: crawl and index a relevant page when existing knowledge is insufficient
- navigate_to_page: navigate the user's browser

Behavior:
1. For factual questions, search existing knowledge first.
2. If the returned information does NOT directly answer the user's question,
   continue using another tool.
3. Search indexed pages if KG results are insufficient.
4. If the answer is still missing, use crawl_and_index_page.
5. You may make multiple tool calls before answering.
6. For "open", "take me to", "navigate", or "go to", use navigate_to_page.
7. Never substitute unrelated facts.
8. Never use your own factual knowledge.
9. If a tool returns NO_RELEVANT_INDEXED_PAGE, do not answer. Use crawl_and_index_page next.
10. If retrieved evidence does not explicitly mention the requested entity/topic, continue searching instead of guessing.
11. If search_knowledge_graph returns NO_RELEVANT_KG_FACTS, do NOT answer. Search indexed pages next.
12. If search_indexed_site returns NO_RELEVANT_INDEXED_PAGE,do NOT answer. Use crawl_and_index_page next.
"""
        },
        {
            "role": "user",
            "content": question.question
        }
    ]

    # Maximum 4 agent/tool rounds
    for step in range(4):

        response = ollama.chat(
            model="qwen3:1.7b",
            think=False,
            messages=messages,
            tools=tools,
            options={"temperature": 0}
        )

        messages.append(response.message)

        # Agent has finished
        if not response.message.tool_calls:

            # Navigation command can finish normally
            if navigation_intent:
                print("AGENT FINISHED AFTER", step + 1, "ROUNDS", flush=True)

                return {
                    "answer": response.message.content,
                    "navigate_url": navigation_url,
                    "source_url": source_url
                }

            # For factual questions, NEVER allow the model to answer
            # before using retrieval tools.
            print("MODEL SKIPPED TOOL - FORCING RETRIEVAL", flush=True)

            if step == 0:
                tool_name = "search_knowledge_graph"
                result = search_knowledge_graph(
                            question.question,
                            current_url=question.current_url
                        )

            elif step == 1:
                tool_name = "search_indexed_site"
                result = search_indexed_site(
                    question.question,
                    current_url=question.current_url
                )

            else:
                tool_name = "crawl_and_index_page"
                result = crawl_and_index_page(
                    question.question,
                    current_url=question.current_url
                )

                print(
                    f"AGENT STEP {step + 1} FORCED TOOL:",
                    tool_name,
                    flush=True
                )

                urls = re.findall(r'https?://[^\s\]\)]+', str(result))
                if urls:
                    source_url = urls[0]

                messages.append({
                    "role": "tool",
                    "tool_name": tool_name,
                    "content": result
                })

                # IMPORTANT: after crawling once, answer immediately
                final = ollama.chat(
                    model="qwen3:1.7b",
                    think=False,
                    messages=messages + [
                        {
                            "role": "system",
                            "content": """
            Answer the user's question using ONLY the retrieved tool evidence.
            Do not call more tools.
            Do not invent facts.
            If a source URL exists, mention it briefly.
            Keep the answer concise.
            """
                        }
                    ],
                    options={"temperature": 0}
                )

                return {
                    "answer": final.message.content,
                    "navigate_url": navigation_url,
                    "source_url": source_url
                }

            print(
                f"AGENT STEP {step + 1} FORCED TOOL:",
                tool_name,
                flush=True
            )

            # capture source URL
            urls = re.findall(r'https?://[^\s\]\)]+', str(result))

            if urls:
                source_url = urls[0]

            messages.append({
                "role": "tool",
                "tool_name": tool_name,
                "content": result
            })

            continue

        for call in response.message.tool_calls:
            
            query_arg = call.function.arguments.get(
                            "query",
                            question.question
                        )

            print(
                f"AGENT STEP {step + 1} TOOL:",
                call.function.name,
                flush=True
            )

            if call.function.name == "search_knowledge_graph":
                result = search_knowledge_graph(
                            query_arg,
                            current_url=question.current_url
                        )

            elif call.function.name == "search_indexed_site":
                result = search_indexed_site(
                    query_arg,
                    current_url=question.current_url
                )

            elif call.function.name == "find_relevant_links":
                result = find_relevant_links(
                    query_arg,
                    current_url=question.current_url
                )

            elif call.function.name == "crawl_and_index_page":
                result = crawl_and_index_page(
                    query_arg,
                    current_url=question.current_url
                )

                urls = re.findall(r'https?://[^\s\]\)]+', str(result))
                if urls:
                    source_url = urls[0]

                messages.append({
                    "role": "tool",
                    "tool_name": call.function.name,
                    "content": result
                })

                print("CRAWL COMPLETE - GENERATING FINAL ANSWER", flush=True)

                final = ollama.chat(
                    model="qwen3:1.7b",
                    think=False,
                    messages=messages + [
                        {
                            "role": "system",
                            "content": """
            Answer using ONLY the retrieved website evidence.
            Do not call any more tools.
            Do not invent facts.
            Keep the answer concise.
            """
                        }
                    ],
                    options={"temperature": 0}
                )

                print("SOURCE URL:", source_url, flush=True)

                return {
                    "answer": final.message.content,
                    "navigate_url": navigation_url,
                    "source_url": source_url
                }

            elif call.function.name == "navigate_to_page":
                result = navigate_to_page(
                    query_arg,
                    current_url=question.current_url
                )

                if result != "NO_NAVIGATION_TARGET":
                    navigation_url = result

            else:
                result = "Unknown tool."

            urls = re.findall(r'https?://[^\s\]\)]+', str(result))

            if urls:
                source_url = urls[0]

            messages.append({
                "role": "tool",
                "tool_name": call.function.name,
                "content": result
            })

    # Safety fallback after max rounds
    final = ollama.chat(
        model="qwen3:1.7b",
        think=False,
        messages=messages + [
            {
                "role": "system",
                "content": """
Give the best concise answer supported ONLY by the tool evidence.
If the requested information was not found, explicitly say so.
Include the source URL when available.
"""
            }
        ],
        options={"temperature": 0}
    )
    print("SOURCE URL:", source_url, flush=True)
    return {
        "answer": final.message.content,
        "navigate_url": navigation_url,
        "source_url": source_url
    }   