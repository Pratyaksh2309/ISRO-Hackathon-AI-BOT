from app.rebel_extractor import extract_rebel_triplets

text = """
Bharatiya Antariksh Hackathon 2026 will be held
on 6th and 7th August 2026.
ISRO headquarters is located in Bengaluru.
"""

triplets = extract_rebel_triplets(text)

for t in triplets:
    print(t)