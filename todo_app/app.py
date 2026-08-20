import os
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", 3000))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("contenttype", "text/html")
            self.end_headers()

            html = """
            <html>
                <head>
                    <title>Todo App</title>
                </head>
                <body>
                    <h1>Todo App</h1>
                    <p>The application is running in Kubernetes.</p>
                </body>
            </html>
            """

            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()
       


server = HTTPServer(("0.0.0.0",PORT), Handler)

print(f"Server started in port {PORT}", flush=True)

server.serve_forever()