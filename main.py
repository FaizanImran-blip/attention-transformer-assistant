import re
from rapidfuzz import process


STOPWORDS = {
    # English grammar
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
    # pronouns
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
    # question words
    "how",
    "what",
    "why",
    "where",
    "when",
    "who",
    # modals
    "do",
    "does",
    "did",
    "can",
    "could",
    "should",
    "would",
    # Hindi/Urdu filler
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
    # fillers
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
    "love", "miss", "help", "confused", "understand",
    "prepare", "preparing", "question", "answer", "topic",
    "lecture", "tomorrow"
]

def correct_spelling(tokens):
    corrected = []

    for word in tokens:
        if word in VOCAB:
            corrected.append(word)
        else:
            match = process.extractOne(word, VOCAB)

            if match and match[1] >= 94:
                corrected.append(match[0])
            else:
                corrected.append(word)

    return corrected


def remove_stopwords(tokens):
    return [word for word in tokens if word not in STOPWORDS]


def function_tokenize(text):
    tokens = text.split()
    print(tokens)


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

    user_input = input("Enter please: ")

    clean = clean_text(user_input)

    tokens = clean.split()

    corrected_tokens = correct_spelling(tokens)

    filtered_tokens = remove_stopwords(corrected_tokens)

    print("Clean Output:", clean)
    print("Tokens:", tokens)
    print("Corrected:", corrected_tokens)
    print("After Stopwords:", filtered_tokens)
