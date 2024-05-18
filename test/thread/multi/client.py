import socket
import pickle
from struct import Struct
import pathlib
import threading
from queue import Queue, Empty


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


class StreamSocketClient(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.sock = None
        self.send_queue = Queue()
        self.result = Queue()
        self.stop_event = threading.Event()
        self.condition = threading.Condition()
        self.condition_ok = False

    def run(self):
        while not self.stop_event.is_set():
            try:
                data = self.send_queue.get(timeout=1)
                if data is None:  # None 是停止信号
                    break
                if self.sock is None:
                    self.connect()
                self.send_with_ack(data)
                result = self.receive_server_data()
                self.result.put(result)
                with self.condition:
                    self.condition.wait_for(lambda: self.condition_ok)
                    self.condition_ok = False
                    self.disconnect()
            except Empty:
                continue

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def disconnect(self):
        if self.sock:
            self.sock.close()
            self.sock = None

    def send_packet(self, packet):
        serialized_packet = pickle.dumps(packet)
        packet_length = STRUCT.pack(len(serialized_packet))
        self.sock.sendall(packet_length)
        self.sock.sendall(serialized_packet)

    def receive_ack(self):
        try:
            ack = self.sock.recv(STRUCT.size)
            if ack:
                return STRUCT.unpack(ack)[0]
        except socket.timeout:
            return None
        return None

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

    def send_ack(self, order):
        ack = STRUCT.pack(order)
        self.sock.sendall(ack)

    def receive_server_data(self):
        try:
            packet = self.receive_packet()
            if not packet:
                return None
            operation = packet["operation"]
            if operation == "file":
                return self.file_generator(packet)
            elif operation == "object":
                obj_chunks = []
                while True:
                    self.send_ack(packet["order"])
                    if packet['operation'] == 'stop':
                        serialized_obj = b''.join(obj_chunks)
                        obj = pickle.loads(serialized_obj)
                        obj_chunks.clear()
                        with self.condition:
                            self.condition_ok = True
                            self.condition.notify()
                        return obj
                    else:
                        chunk_data = packet['data']
                        obj_chunks.append(chunk_data)
                        packet = self.receive_packet()
                        if not packet:
                            break

        except Exception as e:
            print(f"An error occurred while receiving server data: {e}")

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

    def file_generator(self, packet):
        while True:
            self.send_ack(packet["order"])
            if packet["operation"] == "stop":
                with self.condition:
                    self.condition_ok = True
                    self.condition.notify()
                yield packet
                continue
            yield packet
            packet = self.receive_packet()
            if not packet:
                break

    def send_file(self, file_generator):
        self.send_queue.put(file_generator)

    def send_python_object(self, obj):
        packets_generator = self.object_packets_generator(obj)
        self.send_queue.put(packets_generator)

    def get_result(self):
        try:
            return self.result.get(timeout=TIMEOUT)
        except Empty:
            return None

    def stop(self):
        self.stop_event.set()
        self.send_queue.put(None)  # 发送停止信号
        self.disconnect()


# 示例用法
def main():
    # hosts_and_ports = [
    #     ("0.0.0.0", 65432),
    #     ("0.0.0.0", 65431),
    #     ("0.0.0.0", 65430),
    # ]

    # client1 = StreamSocketClient(*hosts_and_ports[0])
    # client2 = StreamSocketClient(*hosts_and_ports[1])
    # client3 = StreamSocketClient(*hosts_and_ports[2])

    # client1.start()
    # client2.start()
    # client3.start()

    # # 发送Python对象
    # data = {"key1": "value1", "key2": [1, 2, 3], "key3": {"nested_key": "nested_value"}}
    # client1.send_python_object(data)
    # client2.send_python_object(data)
    # client3.send_python_object(data)

    # # 获取结果
    # result1 = client1.get_result()
    # result2 = client2.get_result()
    # result3 = client3.get_result()
    # print(f"Received result:", result1, result2, result3, sep="\n")

    # client1.stop()
    # client2.stop()
    # client3.stop()

    host = '127.0.0.1'  # 服务器IP
    port = 65432        # 服务器端口

    client = StreamSocketClient(host, port)
    client.start()

    # 发送Python对象
    data = {"key1": "value1", "key2": [1, 2, 3], "key3": {"nested_key": "nested_value"}}
    client.send_python_object(data)

    # 获取结果
    result = client.get_result()
    print(f"Received result: {result}")

    # 发送文件
    client.send_file(File().file_packets_generator("test.txt"))
    File().process_received_file(client.get_result())
    
    client.stop()

if __name__ == "__main__":
    main()
