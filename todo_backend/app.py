import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", 3000))

todos = [
    "Learn Kubernetes",
    "Learn service-to-service communication"
]


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path == "/todos":

            response = json.dumps(todos)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(response.encode())

        else:
            self.send_response(404)
            self.end_headers()


    def do_POST(self):

        if self.path == "/todos":

            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length)

            try:
                data = json.loads(body)

                todo = data.get("todo", "").strip()

                if not todo:
                    self.send_response(400)
                    self.end_headers()
                    return

                if len(todo) > 140:
                    self.send_response(400)
                    self.end_headers()
                    return

                todos.append(todo)

                response = json.dumps({
                    "todo": todo
                })

                self.send_response(201)
                self.send_header(
                    "Content-Type",
                    "application/json"
                )
                self.end_headers()

                self.wfile.write(response.encode())

            except json.JSONDecodeError:

                self.send_response(400)
                self.end_headers()

        else:
            self.send_response(404)
            self.end_headers()


server = HTTPServer(
    ("0.0.0.0", PORT),
    Handler
)

print(
    f"Todo backend started in port {PORT}",
    flush=True
)

server.serve_forever()