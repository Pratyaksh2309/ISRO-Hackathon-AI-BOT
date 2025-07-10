# utils/rebel_extractor.py

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import re

# Load REBEL model and tokenizer once
tokenizer = AutoTokenizer.from_pretrained("Babelscape/rebel-large")
model = AutoModelForSeq2SeqLM.from_pretrained("Babelscape/rebel-large")

def extract_triplets(text, max_length=512):
    if not text.strip():
        return []

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=max_length)
    outputs = model.generate(**inputs, max_length=256)
    decoded = tokenizer.batch_decode(outputs, skip_special_tokens=False)[0]

    print("\n[🧾] Raw REBEL Output:\n", decoded)

    triplets = []
    current = {"subject": "", "relation": "", "object": ""}
    mode = None

    for token in decoded.split():
        if token == "<triplet>":
            if any(current.values()):
                triplets.append(current.copy())
            current = {"subject": "", "relation": "", "object": ""}
            mode = None
        elif token == "<subj>":
            mode = "subject"
        elif token == "<rel>":
            mode = "relation"
        elif token == "<obj>":
            mode = "object"
        else:
            if mode:
                # Append token with space handling
                current[mode] += token.replace("▁", " ") if "▁" in token else " " + token

    # Append last triplet
    if any(current.values()):
        triplets.append(current)

    # Clean whitespace
    for t in triplets:
        for k in t:
            t[k] = t[k].strip()

    return triplets
