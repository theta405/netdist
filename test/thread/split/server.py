import socket
import pickle
from struct import Struct
import pathlib

CHUNK_SIZE = 1024
STRUCT = Struct("!I")

def receive_packet(sock):
    size_data = sock.recv(STRUCT.size)
    if not size_data:
        return None
    size = STRUCT.unpack(size_data)[0]
    data = sock.recv(size)
    return pickle.loads(data)

def handle_client(conn):
    file_buffers = {}
    obj_buffers = {}
    
    while True:
        packet = receive_packet(conn)
        if not packet:
            break

        operation = packet["operation"]
        order = packet["order"]
        chunk_data = packet["data"]
        message = packet["message"]

        if operation == "file":
            file_name = message["file_name"]
            if file_name not in file_buffers:
                file_buffers[file_name] = {}
            file_buffers[file_name][order] = chunk_data
        elif operation == "object":
            if "object" not in obj_buffers:
                obj_buffers["object"] = {}
            obj_buffers["object"][order] = chunk_data
        elif operation == "stop":
            if "file_name" in message:
                file_name = message["file_name"]
                if file_name in file_buffers:
                    save_file(file_name, file_buffers[file_name])
                    del file_buffers[file_name]
            else:
                if "object" in obj_buffers:
                    obj_data = assemble_object(obj_buffers["object"])
                    print("Received object:", obj_data)
                    del obj_buffers["object"]
            break

def save_file(file_name, file_chunks):
    path = pathlib.Path(file_name)
    with path.open('wb') as f:
        for order in sorted(file_chunks):
            f.write(file_chunks[order])
    print(f"File {file_name} saved.")

def assemble_object(chunks):
    serialized_obj = b''.join(chunks[order] for order in sorted(chunks))
    return pickle.loads(serialized_obj)

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
