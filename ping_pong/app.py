import os
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", 3000))

file_path = "/shared/pingpong.txt"


def read_counter():
    try:
        with open(file_path, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def write_counter(value):
    with open(file_path, "w") as f:
        f.write(str(value))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/pingpong":
            counter = read_counter()

            response = f"pong {counter}"

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(response.encode())

            write_counter(counter + 1)

        else:
            self.send_response(404)
            self.end_headers()


server = HTTPServer(("0.0.0.0", PORT), Handler)

print(f"Ping-pong server started in port {PORT}", flush=True)

server.serve_forever()