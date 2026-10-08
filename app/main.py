import socket  # noqa: F401
import threading


def handle_client(conn: socket.socket, address: tuple):
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
        else:
            conn.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
    except Exception as e:
        print(f"Error handling connection from {address}: {e}")
        

def main():
    print("Logs from your program will appear here!")

    with socket.create_server(("localhost", 4221), reuse_port=True) as server:
        conn, address = server.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(conn, address),
            daemon=True
        )
        thread.start()


if __name__ == "__main__":
    main()
