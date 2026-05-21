import ollama from "ollama";
import fuzzysort from "fuzzysort";

const workingPrompts = [
  "mera quiz 1 se lekr 4 tk hai tuesday ko",
  "mera assingment monday ko 5 bje sham hai",
  "hello today no quiz no assignment",
  "quiz 1 monday 10am aur quiz 2 tuesday 2pm aur assignment 4 friday 5pm",
  "mera quiz hai monday ko aur assignment hai tuesday ko",
  "my quiz 1 to 3 is on monday at 10am",
  "assignment 4 and presentation 2 are due on friday 5pm",
  "no quiz no assignment today",
  "my assignment is on monday evening at 5pm",
  "quiz 1 to 5 tuesday 9am",
  "presentation 2 tomorrow morning 8am",
  "mid exam 3 is on thursday at 1pm"
];

function normalizeInput(input) {
  return input
    .toLowerCase()
    .replace(/kwiz|quz|quizz|quizzz/g, "quiz")
    .replace(/assingment|asignment|assinment|assigment/g, "assignment")
    .replace(/lekr|lekar/g, "lekr")
    .replace(/tak/g, "tk")
    .replace(/\s+/g, " ")
    .trim();
}

export function convertPrompt(userInput) {
  const cleanInput = normalizeInput(userInput);

  const result = fuzzysort.go(cleanInput, workingPrompts, {
    threshold: -10000,
    limit: 1,
  });

  if (result.length === 0) return userInput;

  const best = result[0];

  if (best.score > -300) {
    return best.target;
  }

  return userInput;
}

export async function aiExtractDeadline(userInput) {
  const convertedInput = convertPrompt(userInput);

  const prompt = `
You are a strict university deadline extractor.

Return ONLY valid JSON.
No markdown.
No explanation.
Do not guess.

If text says:
- no quiz
- no assignment
- koi quiz nahi
- quiz ni
- assignment ni
then return [].

Allowed types:
quiz, assignment, presentation, mid exam, final exam

Roman Urdu meanings:
kal = tomorrow
parson = day after tomorrow
subah = AM
sham/shaam/raat = PM
"1 se lekr 4 tk" = numbers 1,2,3,4
"1 or 3" = numbers 1 and 3

Original text:
"${userInput}"

Closest working pattern:
"${convertedInput}"

Important:
Use original text as truth.
Use closest working pattern only to understand style.
Never copy numbers, days, dates, or times from closest pattern unless they exist in original text.

Return schema exactly:
[
  {
    "university_data": "quiz",
    "number": 1,
    "date": null,
    "day": "Monday",
    "time": "17:00"
  }
]
`;

  const response = await ollama.chat({
    model: "qwen2.5:3b",
    messages: [{ role: "user", content: prompt }],
    format: "json",
    options: {
      temperature: 0,
    },
  });

  try {
    const parsed = JSON.parse(response.message.content);

    if (!Array.isArray(parsed)) return [];

    return parsed;
  } catch {
    return [];
  }
}