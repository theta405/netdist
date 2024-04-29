import zmq
import msgpack
import time
import sys

def server():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    while True:
        message = socket.recv()
        start_time = time.time()

        # Receive and unpack data
        data = msgpack.unpackb(message)

        # Simulate processing time
        time.sleep(1)

        # Acknowledge receipt
        socket.send(b"Received")

        end_time = time.time()
        print(f"Received file of size {len(data)} bytes in {end_time - start_time} seconds")

def client(file_path):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    with open(file_path, "rb") as file:
        data = file.read()
        packed_data = msgpack.packb(data)

        start_time = time.time()
        socket.send(packed_data)

        message = socket.recv()
        end_time = time.time()

        print(f"Server response: {message.decode()}")
        print(f"File transfer completed in {end_time - start_time} seconds")

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <client/server> <file_path>")
        sys.exit(1)

    mode = sys.argv[1]
    file_path = sys.argv[2]

    if mode == "server":
        server()
    elif mode == "client":
        client(file_path)
    else:
        print("Invalid mode. Use 'client' or 'server'")
        sys.exit(1)

if __name__ == "__main__":
    main()
