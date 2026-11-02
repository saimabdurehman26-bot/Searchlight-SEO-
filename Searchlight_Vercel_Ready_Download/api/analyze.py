"""Vercel serverless endpoint for Searchlight's on-page SEO checker."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler

from seo_core import analyze_page

MAX_REQUEST_SIZE = 1_000_000


class handler(BaseHTTPRequestHandler):
    """Handle POST /api/analyze requests on Vercel."""

    def do_POST(self) -> None:
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

    def do_GET(self) -> None:
        self._send_json(405, {"error": "Use POST to analyze a page."})

    def _send_json(self, status: int, payload: dict[str, object]) -> None:
        content = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)
