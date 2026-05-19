from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
import json
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

data_path = "/Users/Faizanimran/Downloads/ai powered assistant uninveristy/data.json"

with open(data_path, "r") as file:
    data = json.load(file)

# precompute embeddings
for item in data["intents"]:
    patterns = item["patterns"]
    if isinstance(patterns, list):
        emb = model.encode(patterns)
    else:
        emb = model.encode([patterns])

    item["pattern_embeddings"] = normalize(np.array(emb))


def function_intentlayer(userinput):
    # If input is empty, return UNKNOWN
    if not userinput or not userinput.strip():
        return "UNKNOWN", 0.0

    userinput = userinput.lower()

    # For very short inputs (1-2 words), do simple keyword matching first
    words = userinput.split()
    if len(words) <= 2:
        for item in data["intents"]:
            patterns = item["patterns"]
            if isinstance(patterns, list):
                for pattern in patterns:
                    if userinput == pattern.lower() or userinput in pattern.lower():
                        return item["intent"], 0.95
            else:
                if userinput == patterns.lower() or userinput in patterns.lower():
                    return item["intent"], 0.95

    # Normal embedding similarity
    user_embedding = normalize(model.encode([userinput]))

    best_intent = None
    best_score = 0

    for item in data["intents"]:
        scores = cosine_similarity(user_embedding, item["pattern_embeddings"])[0]
        max_score = max(scores)

        # Keyword boost (more generous)
        intent_keywords = item["intent"].split("_")
        for keyword in intent_keywords:
            if keyword in userinput:
                max_score += 0.15

        if max_score > best_score:
            best_score = max_score
            best_intent = item["intent"]

    # Lower threshold for better detection
    if best_score < 0.50:
        return "UNKNOWN", best_score

    return best_intent, best_score
