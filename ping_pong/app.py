import os
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", 3000))

counter = 0


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global counter

        if self.path == "/pingpong":
            response = f"pong {counter}"

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(response.encode())

            counter += 1

        else:
            self.send_response(404)
            self.end_headers()


server = HTTPServer(("0.0.0.0", PORT), Handler)

print(f"Ping-pong server started in port {PORT}", flush=True)

server.serve_forever()