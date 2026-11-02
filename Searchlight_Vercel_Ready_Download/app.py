"""Run Searchlight locally with: python app.py"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from api.analyze import handler as APIHandler

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"


class LocalHandler(APIHandler):
    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        files = {
            "/": (ROOT / "index.html", "text/html; charset=utf-8"),
            "/index.html": (ROOT / "index.html", "text/html; charset=utf-8"),
            "/static/style.css": (STATIC / "style.css", "text/css; charset=utf-8"),
            "/static/app.js": (STATIC / "app.js", "text/javascript; charset=utf-8"),
        }
        if path == "/api/analyze":
            super().do_GET()
            return
        if path not in files:
            self.send_error(404, "Not found")
            return
        file_path, content_type = files[path]
        try:
            content = file_path.read_bytes()
        except OSError:
            self.send_error(404, "Not found")
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)


if __name__ == "__main__":
    host, port = "127.0.0.1", 8000
    server = ThreadingHTTPServer((host, port), LocalHandler)
    print(f"Searchlight is running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Searchlight.")
    finally:
        server.server_close()
