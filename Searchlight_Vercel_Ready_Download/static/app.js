const form = document.querySelector("#seo-form");
const description = document.querySelector("#description");
const content = document.querySelector("#content");
const descriptionCount = document.querySelector("#description-count");
const wordCount = document.querySelector("#word-count");
const emptyState = document.querySelector("#empty-state");
const results = document.querySelector("#results");
const errorMessage = document.querySelector("#error-message");
const analyzeButton = document.querySelector("#analyze-button");

function updateCounts() {
  descriptionCount.textContent = `${description.value.length} characters`;
  const words = content.value.trim().match(/\b[\w'-]+\b/g) || [];
  wordCount.textContent = `${words.length} words`;
}

description.addEventListener("input", updateCounts);
content.addEventListener("input", updateCounts);

function showResults(data) {
  document.querySelector("#score").textContent = data.score;
  document.querySelector("#score-bar").style.width = `${data.score}%`;

  const title = data.score >= 80 ? "Looking good" : data.score >= 50 ? "Good start" : "Room to grow";
  document.querySelector("#score-title").textContent = title;
  document.querySelector("#score-caption").textContent = `${data.word_count} words checked · ${data.checks.filter((check) => check.passed).length} of ${data.checks.length} checks passed`;

  const list = document.querySelector("#check-list");
  list.replaceChildren();
  for (const check of data.checks) {
    const item = document.createElement("div");
    item.className = `check-item${check.passed ? "" : " needs-work"}`;

    const icon = document.createElement("span");
    icon.className = "check-icon";
    icon.setAttribute("aria-hidden", "true");
    icon.textContent = check.passed ? "✓" : "!";

    const text = document.createElement("div");
    const name = document.createElement("div");
    name.className = "check-name";
    name.textContent = check.label;
    const advice = document.createElement("div");
    advice.className = "check-advice";
    advice.textContent = check.passed ? "Nice work. This check looks good." : check.advice;
    text.append(name, advice);

    const points = document.createElement("span");
    points.className = "check-points";
    points.textContent = `${check.points}/${check.max_points}`;
    item.append(icon, text, points);
    list.append(item);
  }

  emptyState.hidden = true;
  results.hidden = false;
  errorMessage.hidden = true;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorMessage.hidden = true;
  analyzeButton.disabled = true;
  analyzeButton.querySelector("span:first-child").textContent = "Checking...";

  const data = Object.fromEntries(new FormData(form).entries());
  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || "The page could not be checked.");
    }
    showResults(result);
  } catch (error) {
    errorMessage.textContent = error.message || "Could not connect to the SEO checker.";
    errorMessage.hidden = false;
  } finally {
    analyzeButton.disabled = false;
    analyzeButton.querySelector("span:first-child").textContent = "Check my page";
  }
});

document.querySelector("#reset-button").addEventListener("click", () => {
  results.hidden = true;
  emptyState.hidden = false;
  document.querySelector("#score-bar").style.width = "0";
});

updateCounts();
