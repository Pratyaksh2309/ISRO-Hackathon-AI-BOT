from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load the REBEL model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("Babelscape/rebel-large")
model = AutoModelForSeq2SeqLM.from_pretrained("Babelscape/rebel-large")

def extract_triples(text):
    # Tokenize input text
    inputs = tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(**inputs, max_length=512)
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Parse output into triples
    triples = []
    for triple in decoded.split("<triplet>")[1:]:
        try:
            subj = triple.split("<subj>")[1].split("<obj>")[0].strip()
            obj = triple.split("<obj>")[1].split("<rel>")[0].strip()
            rel = triple.split("<rel>")[1].strip()
            triples.append((subj, rel, obj))
        except:
            continue
    return triples

# Test the function
if __name__ == "__main__":
    sample_text = "Elon Musk founded SpaceX in 2002 and later became CEO of Tesla."
    triples = extract_triples(sample_text)
    print("Extracted Triples:")
    for t in triples:
        print(t)
