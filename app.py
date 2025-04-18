from flask import Flask, request, jsonify
from rapidfuzz import fuzz
import re

app = Flask(__name__)

# Load your verses once
verses = []
with open("quran-simple.txt", "r", encoding="utf-8") as file:
    for line in file:
        parts = line.strip().split("|")
        if len(parts) == 3:
            surah, ayah, text = parts
        elif len(parts) == 2:
            surah, text = parts
            ayah = "1"
        verses.append({"surah": int(surah), "ayah": int(ayah), "text": text})

# Normalization helper
def normalize_arabic(text):
    text = re.sub(r'[\u064B-\u0652]', '', text)  # Remove diacritics
    text = re.sub(r'[^\u0600-\u06FF\s]', '', text)  # Remove non-Arabic characters
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    text = text.replace("ة", "ه").replace("ى", "ي")
    return text.strip()

@app.route("/search", methods=["POST"])
def search_verse():
    data = request.json
    query = data.get("speech", "")
    if not query:
        return jsonify({"error": "No speech query provided"}), 400

    normalized_query = normalize_arabic(query)

    results = []
    for verse in verses:
        norm_verse = normalize_arabic(verse['text'])
        score = fuzz.partial_ratio(norm_verse, normalized_query)
        if score >= 80:
            results.append({
                "score": score,
                "surah": verse["surah"],
                "ayah": verse["ayah"],
                "text": verse["text"]
            })

    results.sort(key=lambda x: x["score"], reverse=True)

    if not results:
        return jsonify({"message": "No matching verses found"}), 404

    return jsonify(results)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
