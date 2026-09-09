import os
import time
import json
import urllib.request
import urllib.error
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer


PORT = int(os.environ.get("PORT", 3000))

# Image cache
CACHE_DIR = "/cache"
IMAGE_PATH = os.path.join(CACHE_DIR, "image.jpg")
CACHE_SECONDS = 600  # 10 minutes

# Kubernetes Service for todo-backend
TODO_BACKEND_URL = "http://todo-backend-svc:3000"



def image_needs_refresh():
    if not os.path.exists(IMAGE_PATH):
        return True

    age = time.time() - os.path.getmtime(IMAGE_PATH)

    return age >= CACHE_SECONDS


def download_image():
    print(
        "Downloading new image from Lorem Picsum...",
        flush=True
    )

    os.makedirs(CACHE_DIR, exist_ok=True)

    # Download to temporary file first
    temp_path = IMAGE_PATH + ".tmp"

    urllib.request.urlretrieve(
        "https://picsum.photos/1200",
        temp_path
    )

    # Replace old image only after download succeeds
    os.replace(temp_path, IMAGE_PATH)

    print(
        "New image cached.",
        flush=True
    )


def ensure_image():
    if image_needs_refresh():

        try:
            download_image()

        except Exception as error:

            print(
                f"Image download failed: {error}",
                flush=True
            )

            # If there is no old cached image,
            # we cannot serve anything
            if not os.path.exists(IMAGE_PATH):
                raise


def get_todos():
    """
    Get todos from todo-backend through
    the Kubernetes Service.
    """

    try:

        with urllib.request.urlopen(
            f"{TODO_BACKEND_URL}/todos",
            timeout=2
        ) as response:

            return json.loads(
                response.read().decode()
            )

    except Exception as error:

        print(
            f"Unable to fetch todos: {error}",
            flush=True
        )

        return []


def create_todo(todo):
    """
    Send a new todo to todo-backend.
    """

    data = json.dumps({
        "todo": todo
    }).encode()

    request = urllib.request.Request(
        f"{TODO_BACKEND_URL}/todos",
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(
        request,
        timeout=2
    ) as response:

        return response.status

class Handler(BaseHTTPRequestHandler):


    def do_GET(self):

    
        if self.path == "/todo":

            # Get todos from todo-backend
            todos = get_todos()

            # Convert todos into HTML <li> elements
            todo_items = "".join(
                f"<li>{todo}</li>"
                for todo in todos
            )

            html = f"""
            <!DOCTYPE html>

            <html>

            <head>

                <title>Todo App</title>

                <style>

                    body {{
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 50px auto;
                        padding: 20px;
                    }}

                    h1, h2 {{
                        text-align: center;
                    }}

                    img {{
                        display: block;
                        max-width: 500px;
                        width: 100%;
                        margin: 30px auto;
                    }}

                    .todo-form {{
                        display: flex;
                        gap: 10px;
                        margin: 30px 0;
                    }}

                    input {{
                        flex: 1;
                        padding: 12px;
                        font-size: 16px;
                    }}

                    button {{
                        padding: 12px 24px;
                        cursor: pointer;
                    }}

                    li {{
                        padding: 12px;
                        margin-bottom: 8px;
                        background: #f4f4f4;
                    }}

                </style>

            </head>


            <body>

                <h1>Todo App</h1>

                <img
                    src="/todo/image"
                    alt="Random image"
                >


                <form
                    class="todo-form"
                    method="POST"
                    action="/todo"
                >

                    <input
                        type="text"
                        name="todo"
                        maxlength="140"
                        placeholder="Enter a new todo (max 140 characters)"
                        required
                    >

                    <button type="submit">
                        Send
                    </button>

                </form>


                <h2>Todos</h2>

                <ul>
                    {todo_items}
                </ul>

            </body>

            </html>
            """

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "text/html"
            )

            self.end_headers()

            self.wfile.write(
                html.encode()
            )



        elif self.path == "/todo/image":

            try:

                ensure_image()

                with open(
                    IMAGE_PATH,
                    "rb"
                ) as image:

                    content = image.read()

                self.send_response(200)

                self.send_header(
                    "Content-Type",
                    "image/jpeg"
                )

                self.send_header(
                    "Content-Length",
                    str(len(content))
                )

                self.end_headers()

                self.wfile.write(
                    content
                )

            except Exception as error:

                print(
                    f"Unable to serve image: {error}",
                    flush=True
                )

                self.send_response(500)
                self.end_headers()

        else:

            self.send_response(404)
            self.end_headers()

    def do_POST(self):

        if self.path == "/todo":

            # Get POST body size
            content_length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            # Read form body
            body = self.rfile.read(
                content_length
            ).decode()

            # Parse HTML form
            form_data = urllib.parse.parse_qs(
                body
            )

            todo = form_data.get(
                "todo",
                [""]
            )[0].strip()

            if not todo:

                self.send_response(400)
                self.end_headers()

                return

            if len(todo) > 140:

                self.send_response(400)
                self.end_headers()

                return


            try:

                create_todo(todo)

                # Redirect browser back to Todo page
                self.send_response(303)

                self.send_header(
                    "Location",
                    "/todo"
                )

                self.end_headers()


            except Exception as error:

                print(
                    f"Unable to create todo: {error}",
                    flush=True
                )

                self.send_response(500)
                self.end_headers()


        else:

            self.send_response(404)
            self.end_headers()


server = HTTPServer(
    ("0.0.0.0", PORT),
    Handler
)

print(
    f"Todo App server started in port {PORT}",
    flush=True
)

server.serve_forever()