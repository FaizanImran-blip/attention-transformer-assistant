def detect_action(user_input):
    text = user_input.lower()

    delete_words = ["delete", "remove", "nikalo", "hatao", "khtm", "finish"]

    add_words = [
        "add",
        "insert",
        "dal",
        "dalo",
        "daldo",
        "create",
        "new",
        "izafa",
    ]

    show_words = [
        "show",
        "view",
        "btao",
        "dikhao",
        "kab",
        "date",
        "schedule",
        "kon",
        "konsa",
    ]

    if any(word in text for word in delete_words):
        return "DELETE"

    if any(word in text for word in add_words):
        return "ADD"

    if any(word in text for word in show_words):
        return "SHOW"

    return "UNKNOWN"


def handle_entity(user_input, results):
    action = detect_action(user_input)

    if not results:
        return ["NO_INTENT_FOUND"]

    final_outputs = []

    for intent, score in results:
        if score < 0.55:
            continue

        if action == "SHOW":
            final_outputs.append(f"SHOW DATA for {intent}")

        elif action == "ADD":
            final_outputs.append(f"ADD DATA in {intent}")

        elif action == "DELETE":
            final_outputs.append(f"DELETE DATA from {intent}")

        else:
            final_outputs.append(f"Intent found: {intent}, but action unknown")

    if not final_outputs:
        return ["NO_DATA"]

    return final_outputs
