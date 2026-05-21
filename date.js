import readline from "readline";
import { aiExtractDeadline } from "./model.js";
import dayjs from "dayjs";

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
function normalize(input) {
  return input
    .toLowerCase()


    .replace(/kwiz|quz|quizzz|quizz/g, "quiz")
    .replace(/quizes|quizzes/g, "quiz")
    .replace(/assignment|assignments|asignment|assinment|assingment|assigment|assigmnt|assmnt|homework|task/g, "assignment")
    .replace(/presentaion|presntation|presentation|present/g, "presentation")
    .replace(/midterm|mid term|mid exams|mid exam/g, "mid exam")
    .replace(/finalterm|final term|final exams|final exam/g, "final exam")

    // roman urdu date words
    .replace(/\bkal\b/g, "tomorrow")
    .replace(/\baj\b|\baaj\b/g, "today")
    .replace(/\bparson\b/g, "day after tomorrow")

    // roman urdu range words
.replace(/(\d+)\s*se\s*lekr\s*(\d+)\s*tk/g, "$1 to $2")
.replace(/(\d+)\s*se\s*lekar\s*(\d+)\s*tak/g, "$1 to $2")


    .replace(/\baur\b/g, " aur ")
    .replace(/\bor\b/g, " or ")
    .replace(/\band\b/g, " and ")


    .replace(/quiz(\d+)/g, "quiz $1")
    .replace(/assignment(\d+)/g, "assignment $1")
    .replace(/presentation(\d+)/g, "presentation $1")
    .replace(/exam(\d+)/g, "exam $1")
    .replace(/(\d)(am|pm)/g, "$1 $2")

    // time words
    .replace(/baje|bjy|bjay|bje/g, "o clock")
    .replace(/shaam|sham|raat/g, "pm")
    .replace(/subah|morning/g, "am")

    .replace(/\s+/g, " ")
    .trim();
}
function getNextDate(dayName) {
  const today = dayjs();
  const target = DAYS[dayName];

  let diff = target - today.day();

  // past day ko next week banao
  if (diff < 0) diff += 7;

  return today.add(diff, "day");
}
function extractDays(text) {
  const found = [];

  // day after tomorrow pehle check karo
  if (text.includes("day after tomorrow")) {
    const d = dayjs().add(2, "day");
    return [{
      day: d.format("dddd"),
      date: d.format("YYYY-MM-DD"),
    }];
  }

  if (text.includes("tomorrow")) {
    const d = dayjs().add(1, "day");
    return [{
      day: d.format("dddd"),
      date: d.format("YYYY-MM-DD"),
    }];
  }

  if (text.includes("today")) {
    const d = dayjs();
    return [{
      day: d.format("dddd"),
      date: d.format("YYYY-MM-DD"),
    }];
  }

  const monthMatch = text.match(
    /\b(\d{1,2})\s+(jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|sept|september|oct|october|nov|november|dec|december)\b/i
  );

  if (monthMatch) {
    const d = dayjs(`${monthMatch[1]} ${monthMatch[2]} ${dayjs().year()}`);

    return [{
      day: d.format("dddd"),
      date: d.format("YYYY-MM-DD"),
    }];
  }

  for (const day of Object.keys(DAYS)) {
    if (text.includes(day)) {
      const d = getNextDate(day);
      found.push({
        day: d.format("dddd"),
        date: d.format("YYYY-MM-DD"),
      });
    }
  }

  return found;
}
function extractTime(text) {
  const match = text.match(/\b(?:at|ko|pe)?\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm|o clock)\b/i);

  if (!match) return null;

  let hour = Number(match[1]);
  const minute = match[2] || "00";

  const afterText = text.slice(match.index, match.index + 30);
  const isPM = /\b(pm|sham|shaam|raat)\b/i.test(afterText);
  const isAM = /\b(am|subah|morning)\b/i.test(afterText);

  if (isPM && hour < 12) hour += 12;
  if (isAM && hour === 12) hour = 0;

  return `${String(hour).padStart(2, "0")}:${minute}`;
}
function extractItems(text) {
  const items = [];

  for (const type of TYPES) {
    const regex = new RegExp(`${type}\\s*((?:\\d+\\s*(?:and|,|to|-)?\\s*)*)`, "g");

    let match;
    while ((match = regex.exec(text)) !== null) {
      const beforeText = text.slice(Math.max(0, match.index - 10), match.index);

if (/\b(no|not|without|nahi|ni)\s*$/i.test(beforeText)) {
  continue;
}
      const numberText = match[1] || "";

      const rangeMatch = numberText.match(/(\d+)\s*(?:to|-)\s*(\d+)/);

      if (rangeMatch) {
        const start = Number(rangeMatch[1]);
        const end = Number(rangeMatch[2]);

        for (let i = start; i <= end; i++) {
          items.push({
            university_data: type,
            number: i,
            index: match.index,
          });
        }
      } else {
        const nums = numberText.match(/\d+/g);

        if (nums && nums.length > 0) {
          for (const n of nums) {
            items.push({
              university_data: type,
              number: Number(n),
              index: match.index,
            });
          }
        } else {
          items.push({
            university_data: type,
            number: 0,
            index: match.index,
          });
        }
      }
    }
  }

  return items;
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
      x.university_data !== "null" &&
      ["quiz", "assignment", "presentation", "mid exam", "final exam"].includes(x.university_data)
    );
}
function splitTasks(text) {
  return text
    .split(/\s+aur\s+/i)
    .map(x => x.trim())
    .filter(Boolean);
}
async function checkInput(userInput) {
  const text = normalize(userInput);
  const chunks = splitTasks(text);
  let output = [];

  for (const chunk of chunks) {
    const items = extractItems(chunk);
    const days = extractDays(chunk);
    const time = extractTime(chunk);

    if (items.length === 0) continue;

    const d = days[0] || { day: null, date: null };

    for (const item of items) {
      output.push({
        university_data: item.university_data,
        number: item.number,
        date: d.date,
        day: d.day,
        time,
      });
    }
  }

  output = output.filter((item, index, self) =>
    index === self.findIndex(t =>
      t.university_data === item.university_data &&
      t.number === item.number &&
      t.date === item.date &&
      t.time === item.time
    )
  );
 
if (
  output.length === 0 ||
  output.some(x => x.date === null && x.day === null) ||
  userInput.includes("ek monday") ||
  userInput.includes("se lekr") ||
  userInput.includes("lekar") ||
  userInput.includes("parson")
) {
  const aiOutput = await aiExtractDeadline(userInput);

  if (aiOutput.length > 0) {
     output = cleanAiOutput(aiOutput);
  }
}
  console.table(
    output.length
      ? output
      : [{
          university_data: null,
          number: null,
          date: null,
          day: null,
          time: null,
        }]
  );
}
function ask() {
  rl.question("\n📝 Enter your query: ", async (answer) => {
    if (answer.toLowerCase() === "exit") {
      rl.close();
      return;
    }

    await checkInput(answer);
    ask();
  });
}
console.log("🎓 University Schedule Assistant");
ask();