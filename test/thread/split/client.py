import socket
import pickle
from struct import Struct
import pathlib

CHUNK_SIZE = 1024
STRUCT = Struct("!I")
TIMEOUT = 5  # 超时时间，单位为秒
WINDOW_SIZE = 100  # 窗口大小

def send_packet(sock, packet):
    serialized_packet = pickle.dumps(packet)
    packet_length = STRUCT.pack(len(serialized_packet))
    sock.sendall(packet_length)
    sock.sendall(serialized_packet)

def receive_ack(sock):
    try:
        ack = sock.recv(STRUCT.size)
        if ack:
            return STRUCT.unpack(ack)[0]
    except socket.timeout:
        return None
    return None

def send_with_ack(sock, packets_generator):
    base = 0
    next_seq = 0
    packets = {}
    
    while True:
        while next_seq < base + WINDOW_SIZE:
            try:
                packet = next(packets_generator)
                packets[next_seq] = packet
                send_packet(sock, packet)
                next_seq += 1
            except StopIteration:
                break

        if base == next_seq:
            break

        sock.settimeout(TIMEOUT)
        try:
            ack = receive_ack(sock)
            if ack is not None and ack >= base:
                # 清除已确认的分片
                for i in range(base, ack + 1):
                    if i in packets:
                        del packets[i]
                base = ack + 1
        except socket.timeout:
            for i in range(base, next_seq):
                if i in packets:
                    send_packet(sock, packets[i])

def file_packets_generator(file_path):
    path = pathlib.Path(file_path)
    if not path.is_file():
        print(f"File {file_path} does not exist.")
        return
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
            yield packet
            order += 1
    end_packet = {
        "operation": "stop",
        "order": order,
        "data": b'',
        "message": {"file_name": path.name}
    }
    yield end_packet

def send_file(file_path, host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            packets_generator = file_packets_generator(file_path)
            send_with_ack(s, packets_generator)
    except Exception as e:
        print(f"An error occurred: {e}")

def object_packets_generator(obj):
    serialized_obj = pickle.dumps(obj)
    chunks = [serialized_obj[i:i + CHUNK_SIZE] for i in range(0, len(serialized_obj), CHUNK_SIZE)]
    order = 1
    for chunk in chunks:
        packet = {
            "operation": "object",
            "order": order,
            "data": chunk,
            "message": {}
        }
        yield packet
        order += 1
    end_packet = {
        "operation": "stop",
        "order": order,
        "data": b'',
        "message": {}
    }
    yield end_packet

def send_python_object(obj, host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            packets_generator = object_packets_generator(obj)
            send_with_ack(s, packets_generator)
    except Exception as e:
        print(f"An error occurred: {e}")

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
