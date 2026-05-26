import readline from "readline";
import dayjs from "dayjs";
import { runAutoTests } from "./prompts.js";
import { aiExtractDeadline } from "./model.js";
import { makeCanonicalPrompt } from "./canonical.js";

const loadFeedbackPatterns = () => [];
const saveFeedbackPattern = () => {};
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

const TYPES = ["quiz", "assignment", "presentation", "mid exam", "final exam"];

const DAYS = {
  sunday: 0,
  monday: 1,
  tuesday: 2,
  wednesday: 3,
  thursday: 4,
  friday: 5,
  saturday: 6,
};

const MONTHS = {
  jan: "january", january: "january",
  feb: "february", february: "february",
  mar: "march", march: "march",
  apr: "april", april: "april",
  may: "may",
  jun: "june", june: "june",
  jul: "july", july: "july",
  aug: "august", august: "august",
  sep: "september", sept: "september", september: "september",
  oct: "october", october: "october",
  nov: "november", november: "november",
  dec: "december", december: "december",
};
function normalize(input) {
  return String(input || "")
    .toLowerCase()

    // weekdays
    .replace(/\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)ko\b/g, "$1 ko")
    .replace(/\bmoonday\b/g, "monday")
    .replace(/\b(modnay|mondy|mondayy)\b/g, "monday")
    .replace(/\btuesdat\b/g, "tuesday")
    .replace(/\b(satruday|satuday|satday)\b/g, "saturday")

    // task names
    .replace(/\b(kwiz|quz|quizzz|quizz|quizes|quizzes)\b/g, "quiz")
    .replace(/\b(assignments|asignment|assinment|assingment|assigment|assigmnt|assmnt|homework|task)\b/g, "assignment")
    .replace(/\b(presentaion|presntation|present)\b/g, "presentation")

    // exams
    .replace(/\b(midterm|mid term|mid exams|midle exam|midd exam|mid xam)\b/g, "mid exam")
    .replace(/\b(finalterm|final term|final exams|finals)\b/g, "final exam")

    // relative dates
    .replace(/\b(prso|parso|parson|perso|prson)\b/g, "day after tomorrow")
    .replace(/\bday after tommorow\b/g, "day after tomorrow")
    .replace(/\bafter tomorrow\b/g, "day after tomorrow")

    .replace(/\b(aj|aaj)\b/g, "today")
    .replace(/\bkal\b/g, "tomorrow")

    // week phrases
    .replace(/\b(isi week|is week)\b/g, "this week")
    .replace(/\b(agle week)\b/g, "next week")
    .replace(/\b(agle monday)\b/g, "next monday")
    .replace(/\b(is monday|isi monday)\b/g, "this monday")

    // ranges
    .replace(/(\d+)\s*se\s*(lekr|lekar)?\s*(\d+)\s*(tk|tak)/g, "$1 to $3")
    .replace(/(\d+)\s*-\s*(\d+)/g, "$1 to $2")

    // connectors
    .replace(/\bor\b/g, " and ")
    .replace(/\baur\b/g, " and ")

    // spacing
    .replace(/quiz(\d+)/g, "quiz $1")
    .replace(/assignment(\d+)/g, "assignment $1")
    .replace(/presentation(\d+)/g, "presentation $1")
    .replace(/exam(\d+)/g, "exam $1")
    .replace(/(\d)(am|pm)/g, "$1 $2")

    // time
    .replace(/\b(baje|bjy|bjay|bje)\b/g, "")
    .replace(/\b(subah|morning)\b/g, "am")
    .replace(/\b(sham|shaam|raat|evening|night)\b/g, "pm")

    // noise words
    .replace(/\b(ai|hello|bro|bhai|yar|yaar|yr|mein|main|he|hi)\b/g, " ")

    // cleanup
    .replace(/\s+/g, " ")
    .trim();
}
function getNextDate(dayName, mode = "this") {
  const today = dayjs();
  const target = DAYS[dayName];

  let diff = target - today.day();
  if (diff < 0) diff += 7;

  if (mode === "next") diff += 7;
  if (mode === "next2") diff += 14;

  return today.add(diff, "day");
}

function dateObj(d, index) {
  return {
    day: d.format("dddd"),
    date: d.format("YYYY-MM-DD"),
    index,
  };
}
function similarity(a, b) {
  const aw = a.split(/\s+/);
  const bw = b.split(/\s+/);

  let match = 0;

  for (const w of aw) {
    if (bw.includes(w)) match++;
  }

  return match / Math.max(aw.length, bw.length);
}

function applyFeedback(text) {
  const patterns = loadFeedbackPatterns();

  let best = null;
  let bestScore = 0;

  for (const p of patterns) {
    const score = similarity(text, p.wrong) * (p.weight || 1);

    if (score > bestScore) {
      bestScore = score;
      best = p;
    }
  }

  if (best && bestScore >= 0.65) {
    return best.correct;
  }

  return text;
}
function extractDays(text) {
  const found = [];
  
const relativePatterns = [
  { regex: /\bday after tomorrow\b/g, add: 2 },
  { regex: /\btomorrow\b/g, add: 1 },
  { regex: /\btoday\b/g, add: 0 },
];

  for (const p of relativePatterns) {
    let m;
    while ((m = p.regex.exec(text)) !== null) {
      found.push(dateObj(dayjs().add(p.add, "day"), m.index));
    }
  }

  const monthRegex = /\b(\d{1,2})\s+(jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|sept|september|oct|october|nov|november|dec|december)\b/g;
  if (/\bthis week\b/.test(text)) {
  const weekDay = text.match(/\bthis week\b.*\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b/);

  if (weekDay) {
    found.push(dateObj(getNextDate(weekDay[1], "this"), text.indexOf(weekDay[1])));
  } else {
    found.push(dateObj(dayjs(), text.indexOf("this week")));
  }
}

const hasWeekDayAfterNextWeek =
  /\bnext week\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b/.test(text) ||
  /\bnext week\b.*\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b/.test(text);

if (/\bnext week\b/.test(text) && !hasWeekDayAfterNextWeek) {
  found.push(dateObj(dayjs().add(7, "day"), text.indexOf("next week")));
}
  let mm;
  while ((mm = monthRegex.exec(text)) !== null) {
    const dayNum = Number(mm[1]);
    const month = MONTHS[mm[2]];
    const d = dayjs(`${dayNum} ${month} ${dayjs().year()}`);
    found.push(dateObj(d, mm.index));
  }

  for (const day of Object.keys(DAYS)) {
const regex = new RegExp(`\\b((next\\s+se\\s+next|next|this|not this)\\s+)?${day}\\b`, "g");
    let m;

    while ((m = regex.exec(text)) !== null) {
      const before = text.slice(Math.max(0, m.index - 25), m.index + m[0].length + 25);
      const mode =
  m[0].includes("next se next")
    ? "next2"
    : m[0].includes("next") ||
      before.includes("next week") ||
      m[0].includes("not this") ||
      before.includes("nahi hai next") ||
      before.includes("ni hai next")
        ? "next"
        : "this";

      found.push(dateObj(getNextDate(day, mode), m.index));
    }
  }

  return found.sort((a, b) => a.index - b.index);
}
function extractTime(text) {

  let match = text.match(/\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b/i);

  if (!match) {
    match = text.match(/\b(sham|shaam|raat|evening|night|subah|morning)\s+(\d{1,2})(?::(\d{2}))?\b/i);
    match = text.match(/\b(sham|shaam|raat|evening|night|subah|morning|dopahar|dupehar|afternoon)\s+(\d{1,2})(?::(\d{2}))?\b/i);

    if (!match) return null;

    let hour = Number(match[2]);
    const minute = match[3] || "00";
    const marker = match[1];

    if (/\b(sham|shaam|raat|evening|night)\b/i.test(marker) && hour < 12) {
      hour += 12;
    }

    if (/\b(subah|morning)\b/i.test(marker) && hour === 12) {
      hour = 0;
    }

    return `${String(hour).padStart(2, "0")}:${minute}`;
  }

  let hour = Number(match[1]);
  const minute = match[2] || "00";
  const marker = match[3];

  if (marker === "pm" && hour < 12) hour += 12;
  if (marker === "am" && hour === 12) hour = 0;

  return `${String(hour).padStart(2, "0")}:${minute}`;
}

function isNegated(text, index) {
  const before = text.slice(Math.max(0, index - 18), index);
  const after = text.slice(index, index + 35);
  return /\b(no|not|without|nahi|ni)\s*$/i.test(before) || /\b(nahi|ni|not)\b/i.test(after);
}

function parseNumbers(raw) {
  const nums = [];

  const range = raw.match(/(\d+)\s*(?:to|-)\s*(\d+)/);
  if (range) {
    const start = Number(range[1]);
    const end = Number(range[2]);
    for (let i = start; i <= end; i++) nums.push(i);
    return nums;
  }

  const all = raw.match(/\d+/g);
  if (all) return all.map(Number);

  return [0];
}
function removeDateNumbers(text) {
  return text.replace(
    /\b\d{1,2}\s+(jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|sept|september|oct|october|nov|november|dec|december)\b/g,
    ""
  );
}


function extractItems(text) {
  const items = [];

  for (const type of TYPES) {
    const typeRegex = new RegExp(`\\b${type}\\b`, "g");
    let match;

    while ((match = typeRegex.exec(text)) !== null) {
      if (isNegated(text, match.index)) continue;

const after = removeDateNumbers(
  text.slice(match.index + type.length, match.index + type.length + 70)
);

      let numberText = "";
      const numberMatch = after.match(/^\s*((?:\d+\s*(?:and|,|to|-)?\s*)+)/);

      if (numberMatch) numberText = numberMatch[1];

      const numbers = parseNumbers(numberText);

      for (const n of numbers) {
        items.push({
          university_data: type,
          number: n,
          index: match.index,
        });
      }
    }
  }

  return items.sort((a, b) => a.index - b.index);
}
function findNearestDate(item, dates) {
  if (!dates.length) return { day: null, date: null };
  if (dates.length === 1) return dates[0];

  let best = dates[0];
  let bestScore = Math.abs(item.index - best.index);

  for (const d of dates) {
    const dist = Math.abs(item.index - d.index);
    if (dist < bestScore) {
      best = d;
      bestScore = dist;
    }
  }

  return best;
}

function cleanAiOutput(aiOutput) {
  if (!Array.isArray(aiOutput)) return [];

  return aiOutput
    .map(x => ({
      university_data: x.university_data || x.type || null,
      number: Number(x.number) || 0,
      date: x.date === "null" ? null : x.date || null,
      day: x.day === "null" ? null : x.day || null,
      time: x.time === "null" ? null : x.time || null,
    }))
    .filter(x =>
      x.university_data &&
      TYPES.includes(x.university_data)
    );
}

function dedupe(output) {
  return output.filter((item, index, self) =>
    index === self.findIndex(t =>
      t.university_data === item.university_data &&
      t.number === item.number &&
      t.date === item.date &&
      t.day === item.day &&
      t.time === item.time
    )
  );
}
function detectIntent(text) {
  if (/\b(kahan|kya|allowed|center|syllabus|passing marks|online|offline|record|format|result kab|kab|dress code|upload karun|postpone|extend)\b/.test(text)) {
    return "question";
  }

 if (/\b(nahi|ni|kaam nahi|glitch|corrupt|server down|login|refresh|save nahi|duplicate|upload nahi|missing|plagiarism|absent|cut ho gaya|technical issue|chhoot gaya|submit nahi|marks kam|kam aaye|low marks)\b/.test(text)) {
  return "issue";
}

  return "deadline";
}
let lastType = null;
let lastNumber = 0;
export async function checkInput(userInput, showTable = true) {
  let text = makeCanonicalPrompt(userInput);
  text = applyFeedback(text);
  text = makeCanonicalPrompt(text);

  let items = extractItems(text);
  const dates = extractDays(text);
  const time = extractTime(text);
  const intent = detectIntent(text);

  // ✅ question / issue ko deadline parser mein mat bhejo
  if (intent !== "deadline" && dates.length === 0) {
    const result = [{
      intent,
      university_data: items[0]?.university_data || null,
      number: items[0]?.number ?? null,
      date: null,
      day: null,
      time: null,
    }];

    if (showTable) {
      console.log("\n📊 FINAL INTENT RESPONSE:");
      console.table(result);
    }

    return result;
  }

  // ✅ context memory
  if (items.length === 0 && dates.length > 0 && lastType) {
    items.push({
      university_data: lastType,
      number: lastNumber,
      index: dates[0].index,
    });
  }

  if (items.length > 0) {
    lastType = items[items.length - 1].university_data;
    lastNumber = items[items.length - 1].number || 0;
  }

  let output = [];

  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    const d = dates[i] || findNearestDate(item, dates);

    output.push({
      intent: "deadline",
      university_data: item.university_data,
      number: item.number,
      date: d.date,
      day: d.day,
      time,
    });
  }

  output = dedupe(output);

  const needsAI =
    output.length === 0 ||
    output.some(x => x.date === null && x.day === null);

  console.log("\n🤖 MODEL RESPONSE:");
  const modelOutput = await aiExtractDeadline(userInput);

  console.log("\n🤖 RAW MODEL:");
  console.log(modelOutput.raw);

  console.log("\n🤖 PARSED MODEL:");
  console.table(modelOutput.parsed);

  if (needsAI) {
    const cleaned = cleanAiOutput(modelOutput.parsed);

    if (cleaned.length > output.length) {
      output = cleaned;
    }
  }

  if (showTable) {
    console.log("\n📊 FINAL GRAPH/RULE RESPONSE:");
    console.table(
      output.length
        ? output
        : [{
            intent,
            university_data: null,
            number: null,
            date: null,
            day: null,
            time: null,
          }]
    );
  }

  return output;
}


function ask() {
  rl.question("\n📝 Enter your query: ", async (answer) => {
    const cleanAnswer = answer.trim();

    if (cleanAnswer.toLowerCase() === "exit") {
      rl.close();
      return;
    }

    if (cleanAnswer.includes("=>")) {
      const [wrongText, correctText] = cleanAnswer
        .split("=>")
        .map(x => x.trim());

      if (wrongText && correctText) {
        saveFeedbackPattern(wrongText, correctText);

        console.log("✅ Feedback saved:");
        console.log("Wrong:", wrongText);
        console.log("Correct:", correctText);
      } else {
        console.log("❌ Format: wrong prompt => correct prompt");
      }

      ask();
      return;
    }

    await checkInput(cleanAnswer);
    ask();
  });
}
if (process.argv[1] && process.argv[1].endsWith("date.js")) {
  console.log("🎓 University Schedule Assistant");

  if (process.argv.includes("--test")) {
await runAutoTests(checkInput);
    process.exit(0);
  }


  ask();
}