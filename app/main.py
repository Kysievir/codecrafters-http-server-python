import socket  # noqa: F401
import threading
import argparse
import gzip
from pathlib import Path


def handle_client(conn: socket.socket, address: tuple, args: argparse.Namespace):
    file_root = args.directory

    with conn:
        while True:
            try:
                http_request = conn.recv(2048).decode()
                if not http_request:
                    # Client closed the connection
                    break

                parts = http_request.split("\r\n")

                first_line = parts[0].split(" ")
                if len(first_line) < 2:
                    break
                request_type = first_line[0]
                url = first_line[1]

                content = ""

                headers = {}
                is_content = False
                for part in parts[1:]:
                    if is_content:
                        content = part
                        break
                    elif part == "":
                        is_content = True
                    else:
                        header, info = part.split(": ")[:2]
                        headers[header] = info

                # Check if client supports gzip compression
                accept_encoding = headers.get("Accept-Encoding", "")
                encodings = [enc.strip() for enc in accept_encoding.split(",")]
                use_gzip = "gzip" in encodings
                encoding_header = "Content-Encoding: gzip\r\n" if use_gzip else ""

                # Check if client requested to close the connection (prepares for next stage)
                should_close = headers.get("Connection", "").lower() == "close"
                connection_header = "Connection: close\r\n" if should_close else ""

                if url == "/":
                    reply = f"HTTP/1.1 200 OK\r\n{connection_header}\r\n"
                    conn.send(reply.encode())
                elif url.startswith("/echo/"):
                    message = url.removeprefix("/echo/")
                    body_bytes = message.encode("utf-8")
                    if use_gzip:
                        body_bytes = gzip.compress(body_bytes)

                    header_bytes = (
                        "HTTP/1.1 200 OK\r\n"
                        f"{encoding_header}"
                        f"{connection_header}"
                        "Content-Type: text/plain\r\n"
                        f"Content-Length: {len(body_bytes)}\r\n"
                        "\r\n"
                    ).encode("utf-8")
                    conn.send(header_bytes + body_bytes)
                elif url == "/user-agent":
                    message = headers["User-Agent"]
                    body_bytes = message.encode("utf-8")
                    if use_gzip:
                        body_bytes = gzip.compress(body_bytes)

                    header_bytes = (
                        "HTTP/1.1 200 OK\r\n"
                        f"{encoding_header}"
                        f"{connection_header}"
                        "Content-Type: text/plain\r\n"
                        f"Content-Length: {len(body_bytes)}\r\n"
                        "\r\n"
                    ).encode("utf-8")
                    conn.send(header_bytes + body_bytes)
                elif url.startswith("/files/"):
                    file_path = file_root / url.removeprefix("/files/")

                    if request_type == "GET":
                        if file_path.is_file():
                            body_bytes = file_path.read_bytes()
                            if use_gzip:
                                body_bytes = gzip.compress(body_bytes)

                            header_bytes = (
                                "HTTP/1.1 200 OK\r\n"
                                f"{encoding_header}"
                                f"{connection_header}"
                                "Content-Type: application/octet-stream\r\n"
                                f"Content-Length: {len(body_bytes)}\r\n"
                                "\r\n"
                            ).encode("iso-8859-1")
                            conn.send(header_bytes + body_bytes)
                        else:
                            reply = f"HTTP/1.1 404 Not Found\r\n{connection_header}\r\n"
                            conn.send(reply.encode())
                    elif request_type == "POST":
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        file_path.write_text(content, encoding="utf-8")

                        reply = f"HTTP/1.1 201 Created\r\n{connection_header}\r\n"
                        conn.send(reply.encode())
                else:
                    reply = f"HTTP/1.1 404 Not Found\r\n{connection_header}\r\n"
                    conn.send(reply.encode())

                if should_close:
                    break

            except Exception as e:
                print(f"Error handling connection from {address}: {e}")
                break


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
    