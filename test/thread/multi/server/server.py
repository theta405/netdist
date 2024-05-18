import socket
import pickle
from struct import Struct
import pathlib
import sys

CHUNK_SIZE = 1024
STRUCT = Struct("!I")
TIMEOUT = 5  # 超时时间，单位为秒
WINDOW_SIZE = 100  # 窗口大小


class File:
    def file_packets_generator(self, file_path):
        self.file_path = pathlib.Path(file_path)
        if not self.file_path.is_file():
            print(f"File {self.file_path} does not exist.")
            return
        order = 1
        with self.file_path.open('rb') as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                packet = {
                    "operation": "file",
                    "order": order,
                    "data": chunk,
                    "message": {"file_name": self.file_path.name}
                }
                yield packet
                order += 1
        end_packet = {
            "operation": "stop",
            "order": order,
            "data": b'',
            "message": {"file_name": self.file_path.name}
        }
        yield end_packet

    def process_received_file(self, generator):
        def process_packet(packet, f):
            chunk_data = packet['data']
            f.write(chunk_data)
            f.flush()

        packet = next(generator)
        file_path = packet['message']['file_name']

        with pathlib.Path(file_path).open('wb') as f:
            process_packet(packet, f)

            while True:
                packet = next(generator)
                if packet['operation'] == 'stop':
                    break
                process_packet(packet, f)
        print(f"File received and saved as {file_path}")


class StreamSocketServer:
    def __init__(self, host="0.0.0.0", port=65432):
        self.host = host
        self.port = port
        self.sock = None
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print("Server started and listening on",self.host, self.port)
            while True:
                print("Waiting for new connection")
                conn, addr = s.accept()
                with conn:
                    print("Connected by", addr)
                    self.handle_client(conn)

    def receive_full_data(self, size):
        data = bytearray()
        while len(data) < size:
            packet = self.sock.recv(size - len(data))
            if not packet:
                raise ConnectionError("Socket connection broken")
            data.extend(packet)
        return data

    def receive_packet(self):
        size_data = self.sock.recv(STRUCT.size)
        if not size_data:
            return None
        size = STRUCT.unpack(size_data)[0]
        data = self.receive_full_data(size)
        return pickle.loads(data)

    def receive_ack(self):
        try:
            ack = self.sock.recv(STRUCT.size)
            if ack:
                return STRUCT.unpack(ack)[0]
        except socket.timeout:
            return None
        return None

    def send_ack(self, order):
        ack = STRUCT.pack(order)
        self.sock.sendall(ack)

    def send_packet(self, packet):
        serialized_packet = pickle.dumps(packet)
        packet_length = STRUCT.pack(len(serialized_packet))
        self.sock.sendall(packet_length)
        self.sock.sendall(serialized_packet)

    def send_with_ack(self, packets_generator):
        base = 1
        next_seq = 1
        packets = {}

        while True:
            while next_seq < base + WINDOW_SIZE:
                try:
                    packet = next(packets_generator)
                    packets[next_seq] = packet
                    self.send_packet(packet)
                    next_seq += 1
                except StopIteration:
                    break

            if base == next_seq:
                break

            self.sock.settimeout(TIMEOUT)
            try:
                ack = self.receive_ack()
                if ack is not None and ack >= base:
                    # 清除已确认的分片
                    for i in range(base, ack + 1):
                        if i in packets:
                            del packets[i]
                    base = ack + 1
            except socket.timeout:
                for i in range(base, next_seq):
                    if i in packets:
                        self.send_packet(packets[i])

    def file_generator(self, packet):
        expected_seq = 1
        while True:
            if packet["order"] == expected_seq:
                self.send_ack(expected_seq)
                expected_seq += 1
                yield packet
                packet = self.receive_packet()
                if not packet:
                    break
            else:
                self.send_ack(expected_seq - 1)


    def object_packets_generator(self, obj):
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

    def handle_client(self, conn):
        self.sock = conn
        try:
            packet = self.receive_packet()
            if not packet:
                return None
            first_operation = operation = packet["operation"]
            if operation == "file":
                File().process_received_file(self.file_generator(packet))
            elif operation == "object":
                expected_seq = 1
                obj_chunks = []
                while True:
                    if packet["order"] == expected_seq:
                        self.send_ack(expected_seq)
                        expected_seq += 1
                        if packet['operation'] == 'stop':
                            serialized_obj = b''.join(obj_chunks)
                            obj = pickle.loads(serialized_obj)
                            print("Received object:", obj)
                            obj_chunks.clear()
                            break
                        else:
                            chunk_data = packet['data']
                            obj_chunks.append(chunk_data)
                            packet = self.receive_packet()
                            if not packet:
                                break
                    else:
                        self.send_ack(expected_seq - 1)

            # 处理完成后，根据类型返回文件或对象
            if first_operation == "file":
                file_path = "example.txt"  # 返回的文件
                packets_generator = File().file_packets_generator(file_path)
                self.send_with_ack(packets_generator)
            elif first_operation == "object":
                response_obj = {"result": "ok"}  # 返回的对象
                packets_generator = self.object_packets_generator(response_obj)
                self.send_with_ack(packets_generator)

        except Exception as e:
            print(f"An error occurred while handling client: {e}")
            

if __name__ == "__main__":
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
        StreamSocketServer(port=port)
    else:
        StreamSocketServer()