"""Core SEO checks shared by local development and the Vercel API."""
from __future__ import annotations
import re
from urllib.parse import urlsplit

def analyze_page(data: dict[str, object]) -> dict[str, object]:
    """Score user-provided page details and return actionable SEO checks."""
    fields = ("page_url", "title", "description", "keyword", "heading", "content")
    values: dict[str, str] = {}
    for field in fields:
        value = data.get(field, "")
        if not isinstance(value, str):
            raise ValueError(f"{field.replace('_', ' ').capitalize()} must be text.")
        if len(value) > 100_000:
            raise ValueError(f"{field.replace('_', ' ').capitalize()} is too long.")
        values[field] = value.strip()

    if not values["keyword"]:
        raise ValueError("Please enter a focus keyword.")

    keyword = values["keyword"].casefold()
    title = values["title"]
    description = values["description"]
    heading = values["heading"]
    content = values["content"]
    word_count = len(re.findall(r"\b[\w'-]+\b", content))

    checks: list[dict[str, object]] = []

    def add_check(label: str, passed: bool, points: int, advice: str) -> None:
        checks.append(
            {
                "label": label,
                "passed": passed,
                "points": points if passed else 0,
                "max_points": points,
                "advice": advice,
            }
        )

    title_length = len(title)
    add_check(
        "Title length",
        30 <= title_length <= 60,
        20,
        f"Your title is {title_length} characters. Aim for 30-60 characters.",
    )
    description_length = len(description)
    add_check(
        "Meta description length",
        120 <= description_length <= 160,
        20,
        f"Your description is {description_length} characters. Aim for 120-160 characters.",
    )
    add_check(
        "Keyword in title",
        keyword in title.casefold(),
        15,
        "Include your focus keyword naturally in the page title.",
    )
    add_check(
        "Keyword in description",
        keyword in description.casefold(),
        15,
        "Include your focus keyword naturally in the meta description.",
    )

    parsed_url = urlsplit(values["page_url"])
    slug_text = f"{parsed_url.path} {parsed_url.query}".replace("-", " ").replace("_", " ")
    add_check(
        "Keyword in page URL",
        keyword in slug_text.casefold(),
        10,
        "Use a short, readable URL that includes your focus keyword.",
    )
    add_check(
        "Keyword in main heading",
        keyword in heading.casefold(),
        5,
        "Add your focus keyword to the main heading if it reads naturally.",
    )
    add_check(
        "Content length",
        word_count >= 300,
        15,
        f"Your content has {word_count} words. Consider adding useful detail to reach 300 words.",
    )

    score = sum(int(check["points"]) for check in checks)
    return {"score": score, "checks": checks, "word_count": word_count}
