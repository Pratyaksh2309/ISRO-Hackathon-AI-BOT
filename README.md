# Universal Chatbot - Agentic Web Copilot

A **local, browser-integrated AI assistant for websites** that can read the current webpage, build/query a knowledge graph, autonomously discover relevant internal pages, and answer questions using only website evidence.

The assistant appears directly on webpages as a **floating draggable cat chatbot**. It can ingest the current page, search previously indexed knowledge, crawl relevant pages with Playwright when required, open the source used for an answer, and scroll/highlight supporting content.

> **Privacy / cost:** The core stack runs locally. No paid LLM API is required.

---

## Features

- Floating draggable chatbot injected directly into webpages
- Q&A about the website currently open in Chrome
- Automatic ingestion of the current page before a question
- Local LLM using **Ollama + Qwen3 1.7B**
- Autonomous tool-calling agent for multi-step website research
- **Neo4j knowledge graph** for entities, relations, pages, and links
- Internal-link discovery and autonomous page crawling
- **Playwright** extraction for rendered / JavaScript-heavy webpages
- **Tesseract OCR** fallback when DOM text is insufficient
- **REBEL** relation extraction using `Babelscape/rebel-large`
- Additional Qwen-based triplet extraction
- Source-page navigation and supporting-section highlighting
- Navigation commands such as “Take me to Careers”
- Optional local cat meow sound
- Website/domain-scoped retrieval to prevent knowledge from unrelated sites mixing

---

## Architecture

```text
Chrome webpage
    │
    ▼
Floating Cat Extension (content.js)
    │
    ├── Current URL
    ├── DOM text
    └── Internal links
    │
    ▼
FastAPI backend :8000
    │
    ├── /ingest
    │     ├── Page + links → Neo4j
    │     ├── Qwen triplets
    │     └── REBEL triplets
    │
    └── /ask
          │
          ▼
      Agent Tool Loop
          ├── Search knowledge graph
          ├── Search indexed pages
          ├── Find internal links
          ├── Crawl/index relevant page
          └── Navigate browser
                 │
                 ▼
          Playwright + DOM
                 │
                 └── Tesseract OCR fallback

Local models:
  Ollama qwen3:1.7b
  Ollama qwen3-embedding:0.6b
  Hugging Face Babelscape/rebel-large
```

---

## Project Structure

```text
Universal-chatbot/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── agent_tools.py
│   │   ├── knowledge_graph.py
│   │   ├── crawler.py
│   │   ├── ocr.py
│   │   ├── triplet_extractor.py
│   │   ├── rebel_extractor.py
│   │   └── site_indexer.py
│   └── tests/
│       ├── test_*.py
│
├── extension/
│   ├── manifest.json
│   ├── content.js
│   ├── background.js
│   └── assets/
│       └── meow.mp3
│
├── requirements.txt
└── README.md
```

---

# Setup — Windows

The current project has been developed and tested on **Windows**.

## 1. Install prerequisites

Install the following before starting:

### Python

Python 3.x is required. The current development environment uses Python 3.13.

Check:

```powershell
python --version
```

### Google Chrome

The extension is loaded as an unpacked Chrome extension.

### Ollama

Install Ollama for Windows, then verify:

```powershell
ollama --version
```

If `ollama` is not available in PATH but Ollama is installed, the executable is commonly located at:

```text
C:\Users\<USERNAME>\AppData\Local\Programs\Ollama\ollama.exe
```

### Neo4j Desktop

Install **Neo4j Desktop** and create a local database instance.

The backend currently expects:

```text
URI: bolt://127.0.0.1:7687
Username: neo4j
```

Set the password in:

```text
backend/app/knowledge_graph.py
```

> Do not commit your real Neo4j password to a public repository. Moving these values to environment variables is recommended before publishing the project.

### Tesseract OCR

Install Tesseract OCR for Windows.

The current code expects it at:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

If your installation is elsewhere, update this line in:

```text
backend/app/ocr.py
```

---

## 2. Clone / open the project

```powershell
git clone <YOUR_REPOSITORY_URL>
cd Universal-chatbot
```

If you already have the source locally, simply open PowerShell in the project root.

---

## 3. Create a virtual environment

From the project root:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

and activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## 4. Install Python dependencies

```powershell
pip install -r requirements.txt
```

Then install Playwright's Chromium browser:

```powershell
python -m playwright install chromium
```

### Windows long-path note

Large PyTorch / Transformers installations can fail on Windows if long paths are disabled.

If you encounter `WinError 206` or path-length errors, enable **Win32 long paths** in Windows and retry the install.

---

## 5. Download the local Ollama models

Make sure Ollama is running, then pull:

```powershell
ollama pull qwen3:1.7b
```

and:

```powershell
ollama pull qwen3-embedding:0.6b
```

Check installed models:

```powershell
ollama list
```

The project intentionally uses the smaller `qwen3:1.7b` model so it can run locally on machines without a dedicated NVIDIA GPU.

---

## 6. REBEL model

The relation extractor uses:

```text
Babelscape/rebel-large
```

You do **not** need to download it manually. `transformers` downloads the model automatically the first time the backend imports `rebel_extractor.py`.

The first launch therefore requires internet access and may take longer.

You may see:

```text
Warning: You are sending unauthenticated requests to the HF Hub...
```

An HF token is optional for this project; it mainly increases Hugging Face rate limits.

---

## 7. Start Neo4j

Open **Neo4j Desktop** and start the database used by the project.

Verify that Bolt is listening on port `7687`:

```powershell
netstat -ano | findstr :7687
```

You should see a `LISTENING` entry.

If Neo4j is stopped, website questions that use the knowledge graph will fail with a connection error such as:

```text
Couldn't connect to 127.0.0.1:7687
```

---

## 8. Start the FastAPI backend

Use one PowerShell window for the backend and keep it running.

### PowerShell 1 — backend

From the project root with `.venv` activated:

```powershell
python -m uvicorn backend.app.main:app
```

Expected output:

```text
INFO: Uvicorn running on http://127.0.0.1:8000
```

Test it in a browser:

```text
http://127.0.0.1:8000/
```

Expected response:

```json
{"status":"Agentic Web Copilot backend working"}
```

> Keep this PowerShell window running while using the extension.

---

# Chrome Extension Setup

## 9. Load the extension

Open Chrome and visit:

```text
chrome://extensions
```

Then:

1. Enable **Developer mode**.
2. Click **Load unpacked**.
3. Select the project's `extension` folder.
4. Refresh any website tab that was already open.

The cat should appear directly on the webpage.

---

## 10. Using the assistant

### Open the chatbot

Click the floating cat.

### Ask a question

For example:

```text
What does IIT Bombay say about this research?
```

The extension automatically sends the current page to `/ingest` before asking the backend.

### While thinking

The cat animates while the local agent is working.

### Source evidence

When a source is available, click:

```text
📍 Show Source
```

The browser navigates to the supporting page and attempts to scroll/highlight the relevant section.

### Navigation

You can also use commands such as:

```text
Take me to Careers
```

The agent can select a relevant internal link and navigate the current tab.

### Hide/show the cat

Click the Chrome toolbar icon for the extension to hide or show the floating assistant.

---

# What Happens When You Ask a Question?

A typical factual request follows this flow:

```text
1. Current webpage is ingested
2. Agent searches existing Neo4j facts
3. Agent searches indexed pages from the current website
4. If evidence is insufficient, it finds a relevant internal link
5. Playwright opens/crawls that page
6. DOM text is extracted
7. Tesseract OCR is used as fallback when DOM text is sparse
8. Qwen + REBEL can extract knowledge-graph triplets
9. The page/facts are stored in Neo4j
10. Qwen generates an answer using retrieved website evidence
11. Source URL is returned to the extension
```

Retrieval is scoped to the current website/domain so knowledge indexed from unrelated sites should not be mixed into the answer.

---

# Testing

Use a second PowerShell window for one-off tests.

### PowerShell 2 — tests

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Examples:

```powershell
python backend/test_neo4j.py
```

```powershell
python backend/test_crawler.py
```

```powershell
python backend/test_ocr.py
```

```powershell
python backend/test_rebel.py
```

```powershell
python backend/test_embedding.py
```

Exact test behavior depends on the current contents of each test script.

---

# Recommended Demo Flow

For a reliable demo, verify these cases before presenting:

### 1. Current-page ingestion

Open a normal HTML page and ask a question.

Backend should log an `/ingest` request before `/ask`.

### 2. Existing knowledge retrieval

Ask about information that has already been indexed.

Expected tool examples:

```text
search_knowledge_graph
search_indexed_site
```

### 3. Autonomous page discovery

Ask a question whose answer exists on another internal page.

Expected log pattern:

```text
AGENT CRAWLING: https://current-domain/...relevant-page...
```

### 4. Browser navigation

Ask:

```text
Take me to Careers
```

The current browser tab should navigate to the selected internal page.

### 5. Source navigation

Ask a factual question and click **Show Source**.

### 6. Multi-site isolation

Test on two unrelated websites and verify that crawling/source URLs remain on the current domain.

---

# Important Current Limitations

## PDFs

Normal HTML pages are supported by the current DOM/Playwright pipeline.

Chrome's built-in PDF viewer does not expose PDF contents in the same way as an ordinary webpage, so direct PDF text extraction requires a dedicated PDF ingestion path. PDF support should therefore be treated as separate from normal website ingestion in the current build.

## Local-model latency

The project intentionally avoids paid APIs. On CPU-only machines, Qwen and especially REBEL extraction can take noticeable time.

## OCR fallback

Tesseract OCR is currently used when extracted DOM text is below a threshold. It is not run on every page.

## Knowledge quality

REBEL and LLM-generated triplets can occasionally be noisy. Answers should therefore rely on retrieved source content and source URLs rather than treating every generated relationship as guaranteed ground truth.

---

## Extension changes are not appearing

After changing `content.js`, `background.js`, or `manifest.json`:

1. Open `chrome://extensions`.
2. Click **Reload** on the extension.
3. Refresh the target webpage.

You do **not** need to restart Uvicorn for extension-only changes.

---

# Technology Stack

| Layer | Technology |
|---|---|
| Browser UI | Chrome Extension Manifest V3, JavaScript |
| Local API | FastAPI + Uvicorn |
| Local LLM | Ollama / Qwen3 1.7B |
| Embeddings | qwen3-embedding 0.6B |
| Knowledge Graph | Neo4j |
| Relation Extraction | Babelscape REBEL |
| Web Rendering | Playwright Chromium |
| OCR | Tesseract + pytesseract |
| ML Runtime | PyTorch + Transformers |

---

# Privacy and Cost

The project is designed to run with local components:

- Ollama models run locally
- Neo4j runs locally
- Tesseract runs locally
- FastAPI runs locally
- Chrome extension runs locally

The Hugging Face REBEL model must be downloaded initially, and live websites naturally require internet access to be crawled, but no paid inference API is required for the core system.

---

## Project Origin

Originally developed around the **Bhartiya Antariksh Hackathon / ISRO** concept of an AI assistant capable of extracting knowledge from complex websites and answering questions directly within the browsing experience. The current implementation extends that idea into an agentic, local-first browser copilot with autonomous page discovery, knowledge-graph retrieval, OCR/DOM extraction, and an interactive floating assistant.
