import http.server
import socketserver
import threading
from contextlib import suppress

PORT = 8765

HTML = """
<!doctype html>
<title>Browser Agent Demo</title>
<style>body{font-family:Inter,system-ui;margin:48px;max-width:720px}button{padding:10px 14px}</style>
<h1>Browser Agent Demo</h1>
<p>This page is served inside the Capsule runtime and shown beside chat.</p>
<button id=run>Mark task complete</button>
<p id=status>Waiting for agent...</p>
<script>document.getElementById('run').onclick=()=>status.textContent='Task complete';</script>
"""


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(HTML.encode())

    def log_message(self, *_):
        return


def start_demo_server() -> int:
    def run():
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            with suppress(Exception):
                httpd.serve_forever()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return PORT
