import os
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", 3000))

output_file = "/shared/output.log"
pingpong_file = "/shared/pingpong.txt"


def read_file(path, default=""):
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return default


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            status = read_file(output_file, "Waiting for log output")
            pingpong = read_file(pingpong_file, "0")

            response = f"{status}\nPing / Pongs: {pingpong}"

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(response.encode())

        else:
            self.send_response(404)
            self.end_headers()


server = HTTPServer(("0.0.0.0", PORT), Handler)

print(f"Reader server started in port {PORT}", flush=True)

server.serve_forever()