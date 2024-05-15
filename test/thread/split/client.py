import socket
import pickle
from struct import Struct
import pathlib

CHUNK_SIZE = 1024
STRUCT = Struct("!I")

def send_packet(sock, packet):
    serialized_packet = pickle.dumps(packet)
    packet_length = STRUCT.pack(len(serialized_packet))
    sock.sendall(packet_length)
    sock.sendall(serialized_packet)

def send_file(file_path, host, port):
    path = pathlib.Path(file_path)
    if not path.is_file():
        print(f"File {file_path} does not exist.")
        return

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        order = 1
        with path.open('rb') as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                packet = {
                    "operation": "file",
                    "order": order,
                    "data": chunk,
                    "message": {"file_name": path.name}
                }
                send_packet(s, packet)
                order += 1

        # 发送结束标志
        end_packet = {
            "operation": "stop",
            "order": order,
            "data": b'',
            "message": {"file_name": path.name}
        }
        send_packet(s, end_packet)

def send_python_object(obj, host, port):
    serialized_obj = pickle.dumps(obj)
    chunks = [serialized_obj[i:i + CHUNK_SIZE] for i in range(0, len(serialized_obj), CHUNK_SIZE)]
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        for order, chunk in enumerate(chunks, 1):
            packet = {
                "operation": "object",
                "order": order,
                "data": chunk,
                "message": {}
            }
            send_packet(s, packet)

        # 发送结束标志
        end_packet = {
            "operation": "stop",
            "order": len(chunks) + 1,
            "data": b'',
            "message": {}
        }
        send_packet(s, end_packet)

def main():
    host = '127.0.0.1'  # 服务器IP
    port = 65432        # 服务器端口

    # 示例：发送文件
    # send_file('example.txt', host, port)

    # 示例：发送Python对象
    data = {"key1": "value1", "key2": [1, 2, 3], "key3": {"nested_key": "nested_value"}}
    send_python_object(data, host, port)

if __name__ == "__main__":
    main()
