import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # TODO: Uncomment the code below to pass the first stage
    
    with socket.create_server(("localhost", 4221), reuse_port=True) as server:
        conn, address = server.accept()
        http_request = conn.recv(2048).decode()
        parts = http_request.split("\r\n")
        first_line = parts[0]
        url = first_line.split(" ")[1]

        headers = {}
        for i in range(1, len(parts) - 2):
            print(parts[i])
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
        else:
            conn.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())


if __name__ == "__main__":
    main()
