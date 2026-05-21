# 🎓 Attention Transformer University Assistant

An AI-powered university assistant built with Python, FastAPI, NLP intent pipelines, fuzzy matching, and multilingual understanding.

This project is designed to understand messy student prompts in English, Urdu, and Hinglish and convert them into structured university-related intents.

---

# 🚀 Features

- 🧠 NLP Intent Detection Pipeline
- 🔍 Fuzzy Matching using RapidFuzz
- 🌐 English + Urdu/Hinglish Understanding
- ⚡ FastAPI REST API
- 🧹 Text Cleaning & Normalization
- 🎯 Intent Ranking System
- 🧩 Entity Extraction Layer
- 🔄 Transformer-style Input Processing
- 📚 University Task Understanding
- 📝 Quiz / Assignment / Presentation Detection

---

# 🏗️ Project Architecture

```text
User Prompt
     ↓
Text Cleaning Layer
     ↓
Tokenization
     ↓
Spelling Correction
     ↓
Stopword Removal
     ↓
Intent Pipeline
     ↓
Fuzzy Matching Network
     ↓
Entity Detection Layer
     ↓
Structured AI Response
```

---

# 📂 Project Structure

```text
new_product/
│
├── pipeline_py/
│   ├── api_service.py
│   ├── entity_layer.py
│   ├── trans.py
│   └── main.py
│
├── date.js
├── model.js
├── package.json
├── README.md
└── data.json
```

---

# ⚙️ Technologies Used

- Python
- FastAPI
- RapidFuzz
- JavaScript
- Node.js
- NLP Pipelines
- Fuzzy Logic Matching

---

# 📡 API Example

## GET Request

```bash
/api/intent?text=mera quiz monday ko hai
```

## Response

```json
{
  "success": true,
  "intent": "quiz_view",
  "entity": "monday"
}
```

---

# 🧠 AI Processing Capabilities

The assistant can understand:

- Messy Inputs
- Mixed Languages
- Hinglish Queries
- Typing Mistakes
- Informal Student Prompts

Example:

```text
mera quizz monday ko show kro
```

Automatically normalized and processed into structured intents.

---

# 🔒 Security

Sensitive files are protected using `.gitignore`.

Ignored files include:

- node_modules
- __pycache__
- .env
- logs
- virtual environments

---

# 🌟 Future Goals

- LLM Integration
- Voice Assistant
- University Dashboard
- Smart Schedule Detection
- AI Memory System
- Offline AI Models
- Real-time Notifications

---

# 👨‍💻 Developer

Muhammad Faizan

AI Engineer • NLP Pipeline Developer • University AI Systems Builder

---

# ⭐ Support

If you like this project, give it a star on GitHub ⭐
