import socket
import pickle
from struct import Struct
import pathlib

CHUNK_SIZE = 1024
STRUCT = Struct("!I")

def receive_full_data(sock, size):
    data = bytearray()
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            raise ConnectionError("Socket connection broken")
        data.extend(packet)
    return data

def send_ack(sock, order):
    ack = STRUCT.pack(order)
    sock.sendall(ack)

def receive_packet(sock):
    size_data = sock.recv(STRUCT.size)
    if not size_data:
        return None
    size = STRUCT.unpack(size_data)[0]
    data = receive_full_data(sock, size)
    return pickle.loads(data)

def file_generator(f):
    while True:
        packet = yield
        if packet['operation'] == 'stop':
            f.close()
        else:
            chunk_data = packet['data']
            f.write(chunk_data)
            f.flush()

def object_generator():
    obj_chunks = []
    while True:
        packet = yield
        if packet['operation'] == 'stop':
            serialized_obj = b''.join(obj_chunks)
            obj = pickle.loads(serialized_obj)
            print("Received object:", obj)
            obj_chunks.clear()
        else:
            chunk_data = packet['data']
            obj_chunks.append(chunk_data)

def handle_client(conn):
    try:
        packet = receive_packet(conn)
        if not packet:
            return
        operation = packet["operation"]
        if operation == "file":
            file_name = packet['message']['file_name']
            path = pathlib.Path(file_name)
            file = open(path, "wb")
            generator = file_generator(file)
        elif operation == "object":
            generator = object_generator()

        next(generator)
        generator.send(packet)
        send_ack(conn, packet['order'])
        
        while True:
            packet = receive_packet(conn)
            if not packet:
                break

            generator.send(packet)
            send_ack(conn, packet['order'])
            operation = packet["operation"]
            if operation == "stop":
                break
    except Exception as e:
        print(f"An error occurred while handling client: {e}")

def start_server(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print("Server started and listening on", host, port)
        while True:
            conn, addr = s.accept()
            with conn:
                print("Connected by", addr)
                handle_client(conn)

if __name__ == "__main__":
    start_server()
