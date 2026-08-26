import os
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", 3000))
file_path = "/shared/output.log"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            try:
                with open(file_path, "r") as f:
                    content = f.read()

                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(content.encode())

            except FileNotFoundError:
                self.send_response(503)
                self.end_headers()
                self.wfile.write(b"Waiting for log output")

        else:
            self.send_response(404)
            self.end_headers()


server = HTTPServer(("0.0.0.0", PORT), Handler)

print(f"Reader server started in port {PORT}", flush=True)

server.serve_forever()