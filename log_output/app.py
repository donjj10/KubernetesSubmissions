import uuid
import time
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

random_string = str(uuid.uuid4())


def current_status():
    timestamp = datetime.now(timezone.utc).isoformat()
    return f"{timestamp}: {random_string}"


def log_output():
    while True:
        print(current_status(), flush=True)
        time.sleep(5)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(current_status().encode())
        else:
            self.send_response(404)
            self.end_headers()


threading.Thread(target=log_output, daemon=True).start()

server = HTTPServer(("0.0.0.0", 3000), Handler)

print("Server started in port 3000", flush=True)

server.serve_forever()