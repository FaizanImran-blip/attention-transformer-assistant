import fs from "fs";
import { makeCanonicalPrompt } from "./canonical.js";

export function loadFeedbackPatterns() {
  try {
    return JSON.parse(fs.readFileSync("./feedback_patterns.json", "utf8"));
  } catch {
    return [];
  }
}

export function saveFeedbackPattern(wrongText, correctText) {
  const patterns = loadFeedbackPatterns();

  const wrong = makeCanonicalPrompt(wrongText);
  const correct = makeCanonicalPrompt(correctText);

  const existing = patterns.find(p => p.wrong === wrong);

  if (existing) {
    existing.correct = correct;
    existing.weight = (existing.weight || 1) + 1;
  } else {
    patterns.push({
      wrong,
      correct,
      weight: 1
    });
  }

  fs.writeFileSync("./feedback_patterns.json", JSON.stringify(patterns, null, 2));
}