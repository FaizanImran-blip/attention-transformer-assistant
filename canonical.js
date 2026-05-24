export function makeCanonicalPrompt(input) {
  let text = String(input || "").toLowerCase();

  text = text
    .replace(/\bmoonday\b/g, "monday")
    .replace(/\b(modnay|mondy|mondayy)\b/g, "monday")
    .replace(/\btuesdat\b/g, "tuesday")
    .replace(/\b(satruday|satuday|satday)\b/g, "saturday")
.replace(/\b(day after tommorow|after tomorrow)\b/g, "day after tomorrow")
.replace(/\b(agale hafte|agle hafte|agly hafte)\b/g, "next week")



    .replace(/\b(kwiz|quz|quizzz|quizz|quizes|quizzes)\b/g, "quiz")
    .replace(/\b(assignmennt|assignments|asignment|assinment|assingment|assigment|assigmnt|assmnt|homework|task)\b/g, "assignment")
    .replace(/\b(presentaion|presntation|present)\b/g, "presentation")
    .replace(/\b(mix exam|midle exam|midd exam|mid xam|midterm|mid term|mid exams)\b/g, "mid exam")
    .replace(/\b(finals|finalterm|final term|final exams)\b/g, "final exam")

    .replace(/\b(prso|parso|parson)\b/g, "day after tomorrow")
    .replace(/\b(aj|aaj)\b/g, "today")
    .replace(/\bkal\b/g, "tomorrow")

    .replace(/\b(suba|subah|morning)\b/g, "am")
    .replace(/\b(sham|shaam|evening|raat)\b/g, "pm")
    .replace(/\b(am|pm)\s+(\d{1,2})\b/g, "$2 $1")
    .replace(/\b(bje|baje|bjy|bjay)\b/g, "")

    .replace(/\b(agle week)\b/g, "next week")
    .replace(/\b(isi week|is week)\b/g, "this week")
    .replace(/\b(agle monday)\b/g, "next monday")
    .replace(/\b(is monday|isi monday)\b/g, "this monday")

    .replace(/\b(bi|bhi|aur|or)\b/g, " and ")
    .replace(/\b(yr|yar|yaar|bro|bhai|hello|model|ai|hi|he|mein|main)\b/g, " ")

    .replace(/\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)ko\b/g, "$1 ko")
    .replace(/(\d+)\s*se\s*(lekr|lekar)?\s*(\d+)\s*(tk|tak)/g, "$1 to $3")
    .replace(/(\d+)\s*-\s*(\d+)/g, "$1 to $2")

    .replace(/\s+/g, " ")
    .trim();

  return text;
}