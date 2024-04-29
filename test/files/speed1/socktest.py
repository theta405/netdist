import socket
import time
import sys
import os

def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 5555))
    server_socket.listen(1)
    print("Server is listening...")

    while True:
        conn, addr = server_socket.accept()
        print(f"Connection from {addr}")

        start_time = time.time()

        with conn:
            file_size = int.from_bytes(conn.recv(4), "big")
            print(f"Receiving file of size {file_size} bytes")

            received_data = bytearray()
            while len(received_data) < file_size:
                data = conn.recv(1024)
                if not data:
                    break
                received_data.extend(data)

            conn.sendall(b"Received")

            end_time = time.time()
            print(f"Received file in {end_time - start_time} seconds")

            with open("received_file", "wb") as file:
                file.write(received_data)

def client(file_path):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("127.0.0.1", 5555))

    file_size = os.path.getsize(file_path)
    client_socket.sendall(file_size.to_bytes(4, "big"))

    with open(file_path, "rb") as file:
        start_time = time.time()
        for data in iter(lambda: file.read(1024), b""):
            client_socket.sendall(data)

        server_response = client_socket.recv(1024)
        end_time = time.time()

        print(f"Server response: {server_response.decode()}")
        print(f"File transfer completed in {end_time - start_time} seconds")

def main():
    mode = sys.argv[1]

    if mode == "server":
        server()
    elif mode == "client":
        file_path = sys.argv[2]
        client(file_path)
    else:
        print("Invalid mode. Use 'client' or 'server'")
        sys.exit(1)

if __name__ == "__main__":
    main()
