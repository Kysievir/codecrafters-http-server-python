import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # TODO: Uncomment the code below to pass the first stage
    
    with socket.create_server(("localhost", 4221), reuse_port=True) as server:
        conn, address = server.accept()
        http_request = conn.recv(2048).decode()
        first_line = http_request.split("\r\n")[0]
        url = first_line.split(" ")[1]

        if url == "\\":
            conn.send("HTTP/1.1 200 OK\r\n\r\n".encode())
        else:
            conn.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())


if __name__ == "__main__":
    main()
