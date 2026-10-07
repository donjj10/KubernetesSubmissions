
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", 3000))

OUTPUT_FILE = "/shared/output.log"

CONFIG_FILE = "/config/information.txt"
MESSAGE = os.environ.get("MESSAGE", "")

PING_PONG_URL = "http://ping-pong-svc:3000/pings"


def read_output():
    try:
        with open(OUTPUT_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "Waiting for log output"


def read_config_file():
    try:
        with open(CONFIG_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "Config file not found"


def get_ping_count():
    try:
        with urllib.request.urlopen(PING_PONG_URL, timeout=2) as response:
            return response.read().decode().strip()

    except Exception as error:
        print(f"Unable to contact Ping-Pong: {error}", flush=True)
        return "Unavailable"


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path == "/":

            output = read_output()
            file_content = read_config_file()
            ping_count = get_ping_count()

            response = (
                f"file content: {file_content}\n"
                f"env variable: MESSAGE={MESSAGE}\n"
                f"{output}\n"
                f"Ping / Pongs: {ping_count}"
            )

            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()

            self.wfile.write(response.encode())

        else:
            self.send_response(404)
            self.end_headers()


server = HTTPServer(("0.0.0.0", PORT), Handler)

print(f"Reader server started in port {PORT}", flush=True)

server.serve_forever()
