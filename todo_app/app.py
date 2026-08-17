import os
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", 3000))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("contenttype", "text/plain")
        self.send_headers()
        self.wfile.write(b"Todo app")

server = HTTPServer(("0.0.0.0",PORT), Handler)

print(f"Server started in port {PORT}", flush=True)

server.serve_forever()