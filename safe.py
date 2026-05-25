from collections import Counter
import math
import re
from difflib import get_close_matches

prompts = [
    "hello ai mera assignment hai kal ai",
    "ai mera parso assignment hai",
    "parso",
    "day after tommorow",
    "day after tomorrow",
    "parso tommorow",
    "parso",
    "ai mera monday ko assignment hai",
    "ai mera tuesday ko assignment hai",
    "ai mera wednesday ko assignment hai",
    "ai mera thursday ko assignment hai",
    "ai mera friday ko assignment hai",
    "ai mera satruday ko assignment hai",
    "ai mera saturday ko assignment hai ai",
    "ai mera sunday ko assignment hai ai",
    "mera is sunday ko assignment hai ai",
    "mera next sunday ko assignment hai ai",
    "ai mera kal quiz hai",
    "ai mera parso quiz hai",
    "mera quiz day after tomorrow hai",
    "ai mera Monday ko quiz hai",
    "mera Tuesday ko quiz hai",
    "mera quiz chhoot gaya",
    "quiz mein marks kam aaye",
    "quiz ka result kab aayega",
    "urdu: ai mera quiz hai kal subah",
    "urdu: mera parso quiz hai dopahar ko",
    "assignment ki deadline kal hai",
    "assignment file corrupt ho gayi",
    "assignment mein plagiarism aa gaya",
    "mere assignment kuch pages missing hain",
    "assignment ka format kya hai",
    "urdu: mera assignment kal tak submit karna hai",
    "urdu: assignment parso hai lekin main beemar hun",
    "urdu: assignment group project hai ek member ne kuch nahi kiya",
    "final exam kal hai",
    "final exam parso hai",
    "final exam day after tomorrow hai",
    "final exam Monday ko hai",
    "final exam next week hai",
    "final exam online hoga ya offline",
    "final exam mein kya syllabus ayega",
    "final exam mein passing marks kitne hain",
    "urdu: final exam kal hai aur mene abhi start kiya hai",
    "urdu: final exam parso hai mujhe fever hai",
    "mid exam kal hai",
    "mid exam parso hai",
    "mid exam mein calculator allowed hai?",
    "mid exam ka center kahan hai",
    "mid exam postpone ho sakta hai?",
    "mid exam mein cheat sheet allowed hai?",
    "urdu: mid exam kal hai mera abhi bhi doubt clear nahi hue",
    "presentation kal hai",
    "presentation parso hai",
    "presentation day after tomorrow hai",
    "presentation Monday ko hai",
    "presentation ki slides kahan upload karun",
    "presentation ke liye dress code kya hai",
    "presentation group mein hai ek member absent hai",
    "presentation record ho rahi hai kya",
    "urdu: presentation kal hai mujhe nervous ho raha hai",
    "urdu: presentation parso hai laptop kharab ho gaya",
    "quiz attempt karte waqt page refresh ho gaya",
    "mere answers save nahi hue quiz mein",
    "assignment duplicate submission ho gaya",
    "ai mera kal quiz hai aur parso assignment deadline hai dono manage kaise karun",
    "ai mera same day quiz bhi hai aur presentation bhi hai",
    "kal mera final exam hai",
    "parso mera presentation hai",
    "ai mera friday ko quiz hai",
    "day after tomorrow mera quiz hai",
    "next week Monday ko mid exam hai",
    "next week Wednesday ko assignment hai",
    "agale hafte Tuesday ko final exam hai",
    "ai mera day after tomorrow dopahar ko presentation hai",
]


def tokenize(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    return text.split()


prompt_tokens_list = [tokenize(p) for p in prompts]

word_doc_count = Counter()

for tokens in prompt_tokens_list:
    for word in set(tokens):
        word_doc_count[word] += 1

total_prompts = len(prompts)


def word_weight(word):
    return math.log((total_prompts + 1) / (word_doc_count[word] + 1)) + 1


all_words = set(word_doc_count.keys())
INTENTS = {"quiz", "assignment", "presentation", "final", "mid"}
DAYS = {
    "monday", "tuesday", "wednesday", "thursday",
    "friday", "saturday", "sunday",
    "kal", "parso"
}

def get_day(tokens):
    for word in tokens:
        if word in DAYS:
            return word
    return None


def get_intent(tokens):
    for word in tokens:
        if word in INTENTS:
            return word
    return None


def fix_spelling(tokens):
    fixed = []
    for token in tokens:
        if token in all_words:
            fixed.append(token)
        else:
            match = get_close_matches(token, all_words, n=1, cutoff=0.78)
            fixed.append(match[0] if match else token)
    return fixed

def score_prompt(user_tokens, prompt_tokens):
    user_intent = get_intent(user_tokens)
    prompt_intent = get_intent(prompt_tokens)

    if user_intent and prompt_intent and user_intent != prompt_intent:
        return -999

    user_day = get_day(user_tokens)
    prompt_day = get_day(prompt_tokens)

    # hard reject: friday input monday prompt se match na ho
    if user_day and prompt_day and user_day != prompt_day:
        return -999

    score = 0
    for word in user_tokens:
        if word in prompt_tokens:
            score += word_weight(word)
        else:
            score -= 1.5

    return score

def find_best_prompt(user_input):
    user_tokens = fix_spelling(tokenize(user_input))

    best_prompt = None
    best_score = -999

    for prompt, prompt_tokens in zip(prompts, prompt_tokens_list):
        score = score_prompt(user_tokens, prompt_tokens)

        if score > best_score:
            best_score = score
            best_prompt = prompt

    if best_score < 6:
        return "UNKNOWN", best_score, user_tokens

    return best_prompt, best_score, user_tokens


def catch_words(user_input):
    best_prompt, score, user_tokens = find_best_prompt(user_input)

    if best_prompt == "UNKNOWN":
        return "UNKNOWN", score, [], user_tokens

    best_prompt_tokens = tokenize(best_prompt)

    caught = []
    removed = []

    for word in user_tokens:
        if word in best_prompt_tokens:
            caught.append(word)
        else:
            removed.append(word)

    return best_prompt, score, caught, removed


while True:
    user_input = input("\nEnter input: ")

    if user_input.lower() in ["exit", "quit", "stop"]:
        print("System stopped.")
        break

    matched_prompt, score, caught, removed = catch_words(user_input)

    print("Matched prompt:", matched_prompt)
    print("Match score:", round(score, 2))
    print("Caught words:", caught)
    print("Removed words:", removed)
    print("Clean sentence:", " ".join(caught))
