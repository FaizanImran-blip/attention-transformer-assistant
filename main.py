import sys
import re
from rapidfuzz import process
from pipeline_py import entity_layer, trans

try:
    from test import simple_prompt
except ImportError:
    simple_prompt = []


ACTION_WORDS = {
    "show": {"show", "view", "btao", "batao", "dikhao", "konsa", "kon", "list"},
 "add": {
    "add", "create", "save", "insert", "schedule", "set",
    "rakh", "rakho", "rakhdo", "note"
},
    "delete": {"delete", "remove", "hta", "hata", "hatao", "hatado", "clear", "cancel"},
}

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
    "me",
    "my",
    "your",
    "our",
    "their",
    "how",
    "what",
    "why",
    "where",
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
}

VOCAB = [
    "love",
    "miss",
    "help",
    "confused",
    "understand",
    "course",
    "courses",
    "quiz",
    "quizzes",
    "presentation",
    "presentations",
    "final",
    "midterm",
    "mid",
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

SHOW_PHRASES = [
    "show",
    "view",
    "btao",
    "batao",
    "dikhao",
    "list",
    "kya hai",
    "kab hai",
    "details do",
    "detail do",
    "dekhna hai",
    "check kro",
    "check karo",
    "data dikhao",
    "status",
    "mere wale",
]
ADD_PHRASES = [
    "add kro",
    "add karo",
    "save kro",
    "save karo",
    "create kro",
    "create karo",
    "insert kro",
    "schedule kro",
    "set kro",
    "naya quiz",
    "rakh do",
    "rakhdo",
    "rakho",
    "rakh lo",
    "note kro",
    "note karo",
    "note krdo",
    "note kar do",
    "note karlo"
]
DELETE_PHRASES = [
    "delete kro",
    "delete karo",
    "remove kro",
    "remove karo",
    "hata do",
    "hatao",
    "clear kro",
    "cancel kro",
]


def detect_action_from_text(text):
    text = text.lower()

    reference_phrases = [
        "jo save hain",
        "jo saved hain",
        "jo add kie hain",
        "jo add kiye hain",
        "jo add hain",
        "save hain",
        "add kie hain",
        "add kiye hain",
    ]

    for phrase in reference_phrases:
        if phrase in text:
            return "show"

    for phrase in DELETE_PHRASES:
        if phrase in text:
            return "delete"

    for phrase in ADD_PHRASES:
        if phrase in text:
            return "add"

    for phrase in SHOW_PHRASES:
        if phrase in text:
            return "show"

    # word-level fallback
    words = set(text.split())

    if words & ACTION_WORDS["add"]:
        return "add"

    if words & ACTION_WORDS["delete"]:
        return "delete"

    if words & ACTION_WORDS["show"]:
        return "show"

    return "unknown"


def correct_spelling(tokens):
    corrected = []

    for word in tokens:
        if len(word) <= 3 or word in VOCAB:
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
    text = re.sub(r"\s+", " ", text).strip()
    return text


def process_prompt(user_input):
    print("INPUT:", user_input)

    clean = clean_text(user_input)
    tokens = clean.split()

    corrected_tokens = correct_spelling(tokens)
    filtered_tokens = remove_stopwords(corrected_tokens)
    INTENT_NORMALIZE = {
        "assignments": "assignment",
        "quizzes": "quiz",
        "presentations": "presentation",
        "courses": "course",
        "lectures": "lecture",
    }
    filtered_tokens = [
        INTENT_NORMALIZE.get(word, word)
         for word in filtered_tokens
    ]


    action = detect_action_from_text(" ".join(corrected_tokens))
    intent_text = " ".join(filtered_tokens)

    if not intent_text.strip():
        intent_text = clean

    print("Clean Output:", clean)
    print("Tokens:", tokens)
    print("Corrected:", corrected_tokens)
    print("After Stopwords:", filtered_tokens)
    print("Detected Action:", action)

    results = trans.function_intentlayer(intent_text)

    print("Detected Intents:")
    for intent, score in results:
        print(intent, "->", score)

    final_outputs = entity_layer.handle_entity(user_input, results, action)

    for output in final_outputs:
        print("Final Entity Output:", output)

    print("-" * 50)


def run_tests():
    print("TEST MODE ON")
    print("TOTAL PROMPTS:", len(simple_prompt))

    for prompt in simple_prompt:
        process_prompt(prompt)


def run_single_input():
    while True:
        user_input = input("Enter text: ").strip()

        if user_input.lower() in {"exit", "quit", "q"}:
            print("Program stopped.")
            break

        if not user_input:
            continue

        process_prompt(user_input)


if __name__ == "__main__":
    if "--test" in sys.argv:
        run_tests()
    else:
        run_single_input()
