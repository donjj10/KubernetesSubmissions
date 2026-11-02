import json
import os
import time
from contextlib import closing
from http.server import BaseHTTPRequestHandler, HTTPServer

import psycopg2
from psycopg2.extras import RealDictCursor

PORT = int(os.environ["PORT"])

DB_CONFIG = {
    "host": os.environ["DB_HOST"],
    "port": int(os.environ["DB_PORT"]),
    "dbname": os.environ["DB_NAME"],
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
}


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


def initialize_database():
    for attempt in range(30):
        try:
            with closing(get_db_connection()) as conn:
                with conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS todos (
                                id SERIAL PRIMARY KEY,
                                todo VARCHAR(140) NOT NULL
                            )
                        """)

                        # Preserve the two initial example todos
                        # when the database is first created.
                        cursor.execute("SELECT COUNT(*) FROM todos")
                        count = cursor.fetchone()[0]

                        if count == 0:
                            cursor.executemany(
                                "INSERT INTO todos (todo) VALUES (%s)",
                                [
                                    ("Learn Kubernetes",),
                                    ("Learn service-to-service communication",),
                                ]
                            )

            print("PostgreSQL database initialized", flush=True)
            return

        except psycopg2.OperationalError as error:
            print(f"Waiting for PostgreSQL: {error}", flush=True)
            time.sleep(2)

    raise RuntimeError("Could not connect to PostgreSQL")


def get_todos():
    with closing(get_db_connection()) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT todo FROM todos ORDER BY id")
            return [row["todo"] for row in cursor.fetchall()]


def save_todo(todo):
    with closing(get_db_connection()) as conn:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO todos (todo) VALUES (%s)",
                    (todo,)
                )


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/todos":
            try:
                response = json.dumps(get_todos())

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(response.encode())

            except Exception as error:
                print(f"Database error: {error}", flush=True)
                self.send_response(500)
                self.end_headers()

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/todos":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            try:
                data = json.loads(body)
                todo = data.get("todo", "").strip()

                if not todo or len(todo) > 140:
                    self.send_response(400)
                    self.end_headers()
                    return

                save_todo(todo)

                response = json.dumps({"todo": todo})

                self.send_response(201)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(response.encode())

            except (json.JSONDecodeError, AttributeError):
                self.send_response(400)
                self.end_headers()

            except Exception as error:
                print(f"Database error: {error}", flush=True)
                self.send_response(500)
                self.end_headers()

        else:
            self.send_response(404)
            self.end_headers()


initialize_database()

server = HTTPServer(("0.0.0.0", PORT), Handler)

print(f"Todo backend started on port {PORT}", flush=True)

server.serve_forever()