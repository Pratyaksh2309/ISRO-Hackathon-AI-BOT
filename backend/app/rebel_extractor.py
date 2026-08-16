from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "Babelscape/rebel-large"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

def extract_rebel_triplets(text, max_length=512):
    if not text.strip():
        return []

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=max_length
    )

    outputs = model.generate(
        **inputs,
        max_length=256
    )

    decoded = tokenizer.batch_decode(
        outputs,
        skip_special_tokens=False
    )[0]

    print("RAW REBEL:", decoded)

    triplets = []

    subject = ""
    object_ = ""
    relation = ""
    mode = None

    for token in decoded.split():

        if token == "<triplet>":
            if subject and object_ and relation:
                triplets.append({
                    "subject": subject.strip(),
                    "relation": relation.strip(),
                    "object": object_.strip()
                })

            subject = ""
            object_ = ""
            relation = ""
            mode = "subject"

        elif token == "<subj>":
            mode = "object"

        elif token == "<obj>":
            mode = "relation"

        elif token in ["<s>", "</s>", "<pad>"]:
            continue

        else:
            token = token.replace("▁", " ")

            if mode == "subject":
                subject += " " + token

            elif mode == "object":
                object_ += " " + token

            elif mode == "relation":
                relation += " " + token

    if subject and object_ and relation:
        triplets.append({
            "subject": subject.strip(),
            "relation": relation.strip(),
            "object": object_.replace("</s>", "").strip()
        })

    return triplets