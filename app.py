"""Local SEO checker website using only Python's standard library."""

from __future__ import annotations

import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


PROJECT_DIR = Path(__file__).resolve().parent
STATIC_DIR = PROJECT_DIR / "static"
HOST = "127.0.0.1"
PORT = 8000
MAX_REQUEST_SIZE = 1_000_000


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


class SEORequestHandler(BaseHTTPRequestHandler):
    """Serve the website and its local analysis endpoint."""

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        files = {
            "/": (PROJECT_DIR / "index.html", "text/html; charset=utf-8"),
            "/static/style.css": (STATIC_DIR / "style.css", "text/css; charset=utf-8"),
            "/static/app.js": (
                STATIC_DIR / "app.js",
                "text/javascript; charset=utf-8",
            ),
        }
        if path not in files:
            self.send_error(404, "Not found")
            return

        file_path, content_type = files[path]
        content = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/api/analyze":
            self.send_error(404, "Not found")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(400, {"error": "Invalid request length."})
            return
        if content_length <= 0 or content_length > MAX_REQUEST_SIZE:
            self._send_json(413, {"error": "Request must be between 1 byte and 1 MB."})
            return

        try:
            data = json.loads(self.rfile.read(content_length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(400, {"error": "Send valid JSON data."})
            return
        if not isinstance(data, dict):
            self._send_json(400, {"error": "Request data must be a JSON object."})
            return

        try:
            result = analyze_page(data)
        except ValueError as error:
            self._send_json(400, {"error": str(error)})
            return
        self._send_json(200, result)

    def _send_json(self, status: int, payload: dict[str, object]) -> None:
        content = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), SEORequestHandler)
    print(f"SEO checker is running at http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping SEO checker.")
    finally:
        server.server_close()
