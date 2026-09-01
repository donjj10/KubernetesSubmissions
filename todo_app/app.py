import os
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", 3000))

CACHE_DIR = "/cache"
IMAGE_PATH = os.path.join(CACHE_DIR, "image.jpg")

CACHE_SECONDS = 600  # 10 minutes


def image_needs_refresh():
    if not os.path.exists(IMAGE_PATH):
        return True

    age = time.time() - os.path.getmtime(IMAGE_PATH)

    return age >= CACHE_SECONDS


def download_image():
    print("Downloading new image from Lorem Picsum...", flush=True)

    os.makedirs(CACHE_DIR, exist_ok=True)

    # Temporary file prevents serving a half-downloaded image
    temp_path = IMAGE_PATH + ".tmp"

    urllib.request.urlretrieve(
        "https://picsum.photos/1200",
        temp_path
    )

    os.replace(temp_path, IMAGE_PATH)

    print("New image cached.", flush=True)


def ensure_image():
    if image_needs_refresh():
        try:
            download_image()
        except Exception as error:
            print(f"Image download failed: {error}", flush=True)

            # If an old cached image exists, keep using it
            if not os.path.exists(IMAGE_PATH):
                raise


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path == "/todo":

            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Todo App</title>

                <style>
                    body {
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 50px auto;
                        padding: 20px;
                    }

                    h1, h2 {
                        text-align: center;
                    }

                    img {
                        display: block;
                        max-width: 500px;
                        width: 100%;
                        margin: 30px auto;
                    }

                    .todo-form {
                        display: flex;
                        gap: 10px;
                        margin: 30px 0;
                    }

                    input {
                        flex: 1;
                        padding: 12px;
                        font-size: 16px;
                    }

                    button {
                        padding: 12px 24px;
                        cursor: pointer;
                    }

                    li {
                        padding: 12px;
                        margin-bottom: 8px;
                        background: #f4f4f4;
                    }
                </style>
            </head>

            <body>

                <h1>Todo App</h1>

                <img src="/todo/image" alt="Random image">

                <div class="todo-form">
                    <input
                        type="text"
                        maxlength="140"
                        placeholder="Enter a new todo (max 140 characters)"
                    >

                    <button type="button">
                        Send
                    </button>
                </div>

                <h2>Todos</h2>

                <ul>
                    <li>Learn Kubernetes basics</li>
                    <li>Deploy application to cluster</li>
                    <li>Configure persistent volumes</li>
                </ul>

            </body>
            </html>
            """

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()

            self.wfile.write(html.encode())

        elif self.path == "/todo/image":

            try:
                ensure_image()

                with open(IMAGE_PATH, "rb") as image:
                    content = image.read()

                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()

                self.wfile.write(content)

            except Exception as error:

                print(f"Unable to serve image: {error}", flush=True)

                self.send_response(500)
                self.end_headers()

        else:

            self.send_response(404)
            self.end_headers()


server = HTTPServer(("0.0.0.0", PORT), Handler)

print(f"Server started in port {PORT}", flush=True)

server.serve_forever()