from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
import json
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

data_path = "/Users/Faizanimran/Downloads/clone ai powered univerisity app/new_product/data.json"

with open(data_path, "r") as file:
    data = json.load(file)


for item in data["intents"]:
    patterns = item["patterns"]
    if isinstance(patterns, list):
        emb = model.encode(patterns)
    else:
        emb = model.encode([patterns])

    item["pattern_embeddings"] = normalize(np.array(emb))

def function_intentlayer(userinput):
    if not userinput or not userinput.strip():
        return [("UNKNOWN", 0.0)]

    userinput = userinput.lower()
    words = userinput.split()

    matched_intents = []

    for item in data["intents"]:
        keyword_score = 0

        for keyword in item.get("keywords", []):
            keyword = keyword.lower()

            if " " in keyword:
                if keyword in userinput:
                    keyword_score += 1
            else:
                if keyword in words:
                    keyword_score += 1

        if keyword_score > 0:
            score = min(1.0, 0.95 + keyword_score * 0.05)
            matched_intents.append((item["intent"], score))

    if matched_intents:
        matched_intents = sorted(matched_intents, key=lambda x: x[1], reverse=True)

        final = []
        seen = set()

        for intent, score in matched_intents:
            if intent not in seen:
                final.append((intent, round(score, 3)))
                seen.add(intent)

        return final

    user_embedding = normalize(model.encode([userinput]))

    best_intent = None
    best_score = 0

    for item in data["intents"]:
        scores = cosine_similarity(user_embedding, item["pattern_embeddings"])[0]
        max_score = float(max(scores))

        if max_score > best_score:
            best_score = max_score
            best_intent = item["intent"]

    if best_score < 0.65:
        return [("UNKNOWN", 0.0)]

    return [(best_intent, round(best_score, 3))]