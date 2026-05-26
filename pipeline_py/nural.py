import re
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras import Input
from tensorflow.keras.layers import (
    TextVectorization,
    Embedding,
    GlobalAveragePooling1D,
    Dense,
    Dropout,
)
from tensorflow.keras.models import Model

DATA_PATH = "data.csv"

INTENT_COLS = [
    "quiz",
    "assignment",
    "presentation",
    "midterm",
    "final_exam",
    "lecture",
    "course",
]

ALIASES = {
    "quiz": ["quiz", "quizz"],
    "assignment": ["assignment", "assingment", "assingmnt", "assignmnt", "homework"],
    "presentation": ["presentation", "present"],
    "midterm": ["mid", "midterm", "mid term", "mid exam"],
    "final_exam": ["final", "final exam"],
    "lecture": ["lecture", "class"],
    "course": ["course", "courses"],
}
ACTION_ALIASES = {
    "delete": ["delete", "remove", "hata", "hatao", "clear","khtm"],
    "add": ["add new","add kro", "add krdo", "save kro", "save krdo", "insert kro", "schedule kro", "naya", "new"],
    "show": ["show", "dikhao", "btao", "batao", "kab", "show list","when","shown"],
}


def normalize(text):
    text = str(text).lower().strip()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def keyword_intents(text):
    text = normalize(text)

    if any(w in text.split() for w in ["sb", "sab", "all"]):
        return INTENT_COLS.copy()

    found = []
    for intent, words in ALIASES.items():
        for word in words:
            if word in text:
                found.append(intent)
                break

    return found

def keyword_action(text):
    text = normalize(text)

    # delete highest priority
    if any(word in text for word in ACTION_ALIASES["delete"]):
        return "delete"

    # show command has priority over "add kia hai"
    if any(word in text for word in ACTION_ALIASES["show"]):
        return "show"

    # add only when user wants to add/save/schedule
    add_phrases = [
        "add kro", "add krdo", "save kro", "save krdo",
        "insert kro", "schedule kro", "naya", "new"
    ]

    if any(phrase in text for phrase in add_phrases):
        return "add"

    return None

df = pd.read_csv(DATA_PATH)
df = df.dropna()
df["text"] = df["text"].apply(normalize)
df["action"] = df["action"].astype(str).str.lower().str.strip()

for col in INTENT_COLS:
    df[col] = df[col].astype(int)

X = df["text"].values
y_intent = df[INTENT_COLS].values.astype("float32")

action_encoder = LabelEncoder()
y_action = action_encoder.fit_transform(df["action"])
y_action = tf.keras.utils.to_categorical(y_action)

X_train, X_test, yi_train, yi_test, ya_train, ya_test = train_test_split(
    X,
    y_intent,
    y_action,
    test_size=0.20,
    random_state=42,
    shuffle=True,
)

vectorizer = TextVectorization(
    max_tokens=3000,
    output_sequence_length=25,
    standardize=None,
)

vectorizer.adapt(X_train)

inp = Input(shape=(1,), dtype=tf.string)

x = vectorizer(inp)
x = Embedding(input_dim=3000, output_dim=64)(x)
x = GlobalAveragePooling1D()(x)

x = Dense(128, activation="relu")(x)
x = Dropout(0.25)(x)

x = Dense(64, activation="relu")(x)
x = Dropout(0.20)(x)

intent_out = Dense(len(INTENT_COLS), activation="sigmoid", name="intent")(x)
action_out = Dense(len(action_encoder.classes_), activation="softmax", name="action")(x)

model = Model(inputs=inp, outputs=[intent_out, action_out])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss={
        "intent": "binary_crossentropy",
        "action": "categorical_crossentropy",
    },
    metrics={
        "intent": ["binary_accuracy"],
        "action": ["accuracy"],
    },
)

early_stop = tf.keras.callbacks.EarlyStopping(
    monitor="val_loss",
    patience=25,
    restore_best_weights=True,
)

model.fit(
    X_train,
    {"intent": yi_train, "action": ya_train},
    validation_data=(X_test, {"intent": yi_test, "action": ya_test}),
    epochs=300,
    batch_size=8,
    callbacks=[early_stop],
    verbose=1,
)

model.save("intent_action_model.keras")
joblib.dump(action_encoder, "action_encoder.pkl")
joblib.dump(INTENT_COLS, "intent_cols.pkl")

print("✅ Model trained and saved successfully")


def predict(text, threshold=0.35):
    clean_text = normalize(text)

    intent_pred, action_pred = model.predict(tf.constant([clean_text]), verbose=0)

    nn_intents = [
        INTENT_COLS[i] for i, score in enumerate(intent_pred[0]) if score >= threshold
    ]

    rule_intents = keyword_intents(clean_text)
    detected_intents = rule_intents if rule_intents else nn_intents

    if not detected_intents:
        detected_intents = ["unknown"]

    rule_action = keyword_action(clean_text)

    action_index = int(np.argmax(action_pred[0]))
    nn_action = action_encoder.inverse_transform([action_index])[0]
    action_score = float(action_pred[0][action_index])

    action = rule_action if rule_action else nn_action

    if detected_intents == ["unknown"] and rule_action is None and action_score < 0.60:
        action = "unknown"

    return {
        "text": text,
        "intents": detected_intents,
        "intent_scores": {
            INTENT_COLS[i]: round(float(intent_pred[0][i]), 3)
            for i in range(len(INTENT_COLS))
        },
        "action": action,
        "action_score": round(action_score, 3),
    }


while True:
    user_text = input("Enter text: ").strip()

    if user_text.lower() in ["exit", "quit"]:
        break

    if not user_text:
        continue

    print(predict(user_text))
