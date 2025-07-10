# Universal Web Knowledge Graph Chatbot

🧠 A LangChain-powered chatbot that can visit any webpage, extract structured knowledge, and answer questions using Neo4j and REBEL.

## Features
- 🕸️ Loads websites using Playwright
- 📸 Extracts text using screenshot + OCR
- 🧠 Extracts knowledge triplets using REBEL
- 🔗 Stores into Neo4j KG
- 💬 Ask questions via Streamlit chat UI

## Setup

```bash
pip install -r requirements.txt
playwright install
streamlit run app.py
```

Make sure Neo4j is running on `bolt://localhost:7687`.

---