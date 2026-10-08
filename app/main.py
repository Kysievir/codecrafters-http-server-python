import socket  # noqa: F401
import threading
import argparse
from pathlib import Path


def handle_client(conn: socket.socket, address: tuple, args: argparse.Namespace):
    file_root = args.directory

    with conn:
        try:
            http_request = conn.recv(2048).decode()
            parts = http_request.split("\r\n")
            first_line = parts[0]
            url = first_line.split(" ")[1]
    
            headers = {}
            for i in range(1, len(parts) - 2):
                header, info = parts[i].split(": ")[:2]
                headers[header] = info
    
            if url == "/":
                conn.send("HTTP/1.1 200 OK\r\n\r\n".encode())
            elif url.startswith("/echo/"):
                message = url.removeprefix("/echo/")
                reply = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/plain\r\n"
                    f"Content-Length: {len(message)}\r\n"
                    "\r\n"
                    f"{message}"
                )
                conn.send(reply.encode())
            elif url == "/user-agent":
                message = headers["User-Agent"]
                reply = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/plain\r\n"
                    f"Content-Length: {len(message)}\r\n"
                    "\r\n"
                    f"{message}"
                )
                conn.send(reply.encode())
            elif url.startswith("/files/"):
                file_path = file_root / url.removeprefix("/files/")

                if file_path.is_file():
                    body_bytes = file_path.read_bytes()
                    header_bytes = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: application/octet-stream\r\n"
                        f"Content-Length: {len(body_bytes)}\r\n"
                        "\r\n"
                    ).encode("iso-8859-1")
                    conn.send(header_bytes + body_bytes)
                else:
                    conn.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
            else:
                conn.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
        except Exception as e:
            print(f"Error handling connection from {address}: {e}")
        

def main():
    print("Logs from your program will appear here!")

    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=Path("/"))
    args = parser.parse_args()

    with socket.create_server(("localhost", 4221), reuse_port=True) as server:
        while True:
            conn, address = server.accept()

            thread = threading.Thread(
                target=handle_client,
                args=(conn, address, args),
                daemon=True
            )
            thread.start()


if __name__ == "__main__":
    main()
