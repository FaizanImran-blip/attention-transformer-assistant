from fastapi import FastAPI, Query
from pydantic import BaseModel
import re
import entity_layer
import trans
from rapidfuzz import process

app = FastAPI()


class UserPrompt(BaseModel):
    text: str


STOPWORDS = {
    "a", "an", "the", "is", "am", "are", "was", "were", "be", "been", "being",
    "to", "of", "in", "on", "for", "and", "or", "but", "if", "then", "else",
    "when", "at", "by", "from", "with", "about", "as", "into", "i", "you",
    "he", "she", "it", "we", "they", "me", "us", "him", "her", "my", "your",
    "our", "their", "how", "what", "why", "where", "who", "do", "does", "did",
    "can", "could", "should", "would", "hai", "hain", "ka", "ki", "ke", "ko",
    "se", "mein", "kya", "kyun", "kaise", "pls", "please", "bro", "bhai",
    "man", "yaar", "sir", "ok", "okay", "u"
}

VOCAB = [
    "love", "miss", "help", "confused", "understand", "courses",
    "quiz", "quizzes", "presentations", "presentation", "final",
    "mid term", "mid", "assignment", "assignments", "prepare",
    "preparing", "question", "answer", "topic", "lecture",
    "tomorrow", "view"
]


def clean_text(user_input):
    text = user_input.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"(.)\1{2,}", r"\1", text)
    text = re.sub(r"\b[a-z]+\d+\b", " ", text)
    text = re.sub(r"\b\d+\b", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def correct_spelling(tokens):
    corrected = []

    for word in tokens:
        if len(word) <= 3 or word in VOCAB:
            corrected.append(word)
            continue

        match = process.extractOne(word, VOCAB)
        corrected.append(match[0] if match and match[1] >= 85 else word)

    return corrected


def remove_stopwords(tokens):
    return [word for word in tokens if word not in STOPWORDS]


def make_response(user_input):
    clean = clean_text(user_input)
    tokens = clean.split()
    corrected_tokens = correct_spelling(tokens)
    filtered_tokens = remove_stopwords(corrected_tokens)

    intent_text = " ".join(filtered_tokens)

    if not intent_text.strip():
        intent_text = clean

    results = trans.function_intentlayer(intent_text)
    final_outputs = entity_layer.handle_entity(user_input, results)

    return {
        "success": True,
        "input": user_input,
        "clean_output": clean,
        "tokens": tokens,
        "corrected_tokens": corrected_tokens,
        "filtered_tokens": filtered_tokens,
        "intent_text": intent_text,
        "detected_intents": [
            {"intent": intent, "score": score}
            for intent, score in results
        ],
        "action": entity_layer.detect_action(user_input),
        "entity_output": final_outputs
    }


@app.get("/")
def home():
    return {"message": "Python AI Pipeline API is running"}


# GET API
@app.get("/api/intent")
def api_intent_get(text: str = Query(...)):
    return make_response(text)


# POST API
@app.post("/api/intent")
def api_intent_post(prompt: UserPrompt):
    return make_response(prompt.text)