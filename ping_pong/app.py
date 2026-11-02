import os
import time
import psycopg2
from http.server import BaseHTTPRequestHandler, HTTPServer

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
    # Wait for PostgreSQL to accept connections.
    for attempt in range(30):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS ping_counter (
                            id INTEGER PRIMARY KEY CHECK (id = 1),
                            count BIGINT NOT NULL
                        )
                    """)
                    cursor.execute("""
                        INSERT INTO ping_counter (id, count)
                        VALUES (1, 0)
                        ON CONFLICT (id) DO NOTHING
                    """)
            print("PostgreSQL database initialized", flush=True)
            return
        except psycopg2.OperationalError as error:
            print(f"Waiting for PostgreSQL: {error}", flush=True)
            time.sleep(2)

    raise RuntimeError("Could not connect to PostgreSQL")


def increment_counter():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE ping_counter
                SET count = count + 1
                WHERE id = 1
                RETURNING count - 1
            """)
            previous_count = cursor.fetchone()[0]
            return previous_count


def get_counter():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT count
                FROM ping_counter
                WHERE id = 1
            """)
            return cursor.fetchone()[0]


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        try:
            if self.path == "/pingpong":
                response = f"pong {increment_counter()}"

            elif self.path == "/pings":
                response = str(get_counter())

            else:
                self.send_response(404)
                self.end_headers()
                return

            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(response.encode())

        except Exception as error:
            print(f"Request failed: {error}", flush=True)
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Database error")


initialize_database()

server = HTTPServer(("0.0.0.0", PORT), Handler)

print(f"Ping-pong server started on port {PORT}", flush=True)

server.serve_forever()