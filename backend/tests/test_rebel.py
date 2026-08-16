from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "Babelscape/rebel-large"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

print("Loading model...")
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

text = """
ISRO's vision is to harness, sustain and augment space technology
for national development while pursuing space science research
and planetary exploration.
"""

inputs = tokenizer(
    text,
    return_tensors="pt",
    truncation=True,
    max_length=256
)

outputs = model.generate(
    **inputs,
    max_length=128
)

decoded = tokenizer.batch_decode(
    outputs,
    skip_special_tokens=False
)[0]

print("\nREBEL OUTPUT:")
print(decoded)