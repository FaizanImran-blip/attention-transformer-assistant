import ollama from "ollama";
import { makeCanonicalPrompt } from "./canonical.js";

const TYPES = ["quiz", "assignment", "presentation", "mid exam", "final exam"];

function normalizeModelParsed(parsed) {
  const arr = Array.isArray(parsed) ? parsed : [parsed];

  return arr.flatMap(x => {
    if (!x || !x.university_data) return [];

    const types = Array.isArray(x.university_data)
      ? x.university_data
      : String(x.university_data).split(",");

    return types.map(type => ({
      university_data: type.trim(),
      number: Number(x.number) || 0,
      date_text: x.date_text ?? null,
      time_text: x.time_text ?? null,
    }));
  });
}

export async function aiExtractDeadline(userInput) {
  const cleanInput = makeCanonicalPrompt(userInput);

  const prompt = `
Return ONLY JSON array.

Extract university tasks.

Allowed:
quiz, assignment, presentation, mid exam, final exam

Fields:
university_data, number, date_text, time_text

Rules:
- One object per task.
- Do not join tasks.
- Copy date_text from user text.
- Copy time_text from user text.
- Missing number = 0.
- Missing date_text = null.
- Missing time_text = null.
- Do not calculate date/day.

User:
${JSON.stringify(cleanInput)}
`;

  try {
    const response = await ollama.chat({
      model: "qwen2.5:3b",
      messages: [{ role: "user", content: prompt }],
      format: "json",
      options: {
        temperature: 0,
        top_p: 0.1,
        num_predict: 150,
      },
    });

    const content = response.message.content.trim();

    const parsed = normalizeModelParsed(JSON.parse(content))
      .filter(x => TYPES.includes(x.university_data));

    return {
      raw: content,
      parsed,
    };
  } catch (e) {
    return {
      raw: null,
      parsed: [],
      error: e.message,
    };
  }
}