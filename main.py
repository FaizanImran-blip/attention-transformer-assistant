import re
from rapidfuzz import process
import sys

sys.path.append(
    "/Users/Faizanimran/Downloads/clone ai powered univerisity app/new_product"
)

import trans

STOPWORDS = {
    "a",
    "an",
    "the",
    "is",
    "am",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "to",
    "of",
    "in",
    "on",
    "for",
    "and",
    "or",
    "but",
    "if",
    "then",
    "else",
    "when",
    "at",
    "by",
    "from",
    "with",
    "about",
    "as",
    "into",
    "i",
    "you",
    "he",
    "she",
    "it",
    "we",
    "they",
    "me",
    "us",
    "him",
    "her",
    "my",
    "your",
    "our",
    "their",
    "how",
    "what",
    "why",
    "where",
    "when",
    "who",
    "do",
    "does",
    "did",
    "can",
    "could",
    "should",
    "would",
    "hai",
    "hain",
    "ka",
    "ki",
    "ke",
    "ko",
    "se",
    "mein",
    "kya",
    "kyun",
    "kab",
    "kaise",
    "pls",
    "please",
    "bro",
    "bhai",
    "man",
    "yaar",
    "sir",
    "ok",
    "okay",
    "u",
    "are",
}

VOCAB = [
    "love",
    "miss",
    "help",
    "confused",
    "understand",
    "courses",
    "quiz",
    "quizzes",
    "presentations",
    "presentation",
    "final ",
    "mid term ",
    "mid ",
    "assignment",
    "assignments",
    "prepare",
    "preparing",
    "question",
    "answer",
    "topic",
    "lecture",
    "tomorrow",
    "view",
]


def correct_spelling(tokens):
    corrected = []

    for word in tokens:
        if len(word) <= 3:
            corrected.append(word)
            continue

        if word in VOCAB:
            corrected.append(word)
            continue

        match = process.extractOne(word, VOCAB)

        if match and match[1] >= 85:
            corrected.append(match[0])
        else:
            corrected.append(word)

    return corrected


def remove_stopwords(tokens):
    return [word for word in tokens if word not in STOPWORDS]


def clean_text(user_input):
    text = user_input.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"(.)\1{2,}", r"\1", text)
    text = re.sub(r"\b[a-z]+\d+\b", " ", text)
    text = re.sub(r"\b\d+\b", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


while True:
    try:
        user_input = input("Enter please: ")

        # Step 1: Clean text
        clean = clean_text(user_input)

        # Step 2: Tokenize
        tokens = clean.split()

        # Step 3: Correct spelling
        corrected_tokens = correct_spelling(tokens)

        # Step 4: Remove stopwords - BUT keep important words
        filtered_tokens = remove_stopwords(corrected_tokens)

        # Step 5: Reconstruct cleaned text for intent detection
        # IMPORTANT: Use filtered tokens for intent, not original clean text
        intent_text = " ".join(filtered_tokens)

        # If filtered_text is empty, use original clean text as fallback
        if not intent_text.strip():
            intent_text = clean

        print("Clean Output:", clean)
        print("Tokens:", tokens)
        print("Corrected:", corrected_tokens)
        print("After Stopwords:", filtered_tokens)

        results = trans.function_intentlayer(intent_text)

        print("Detected Intents:")
        for intent, score in results:
            print(intent, "->", score)
        print("-" * 50)

    except KeyboardInterrupt:
        print("\nExiting...")
        break
