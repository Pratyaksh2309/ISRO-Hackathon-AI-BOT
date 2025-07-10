import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tokenizer = AutoTokenizer.from_pretrained("Babelscape/rebel-large")
model = AutoModelForSeq2SeqLM.from_pretrained("Babelscape/rebel-large")

def extract_triplets(text):
    inputs = tokenizer([text], return_tensors="pt", truncation=True, max_length=1024)
    outputs = model.generate(**inputs, max_new_tokens=200)
    decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)

    triplets = []
    for line in decoded:
        parts = line.split(" | ")
        for p in parts:
            try:
                subj, rel, obj = p.split(" [SEP] ")
                triplets.append((subj.strip(), rel.strip(), obj.strip()))
            except:
                continue
    return triplets