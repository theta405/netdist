import threading
import queue
import socket
import pickle

class CustomThread(threading.Thread):
    def __init__(self, name, host, port):
        super().__init__()
        self.name = name
        self.queue = queue.Queue()
        self.host = host
        self.port = port
        self.running = True

    def run(self):
        while self.running:
            try:
                # 从队列中获取内容，如果队列为空，则会等待
                data = self.queue.get(timeout=1)
                if data is not None:
                    self.send_data(data)
            except queue.Empty:
                continue

    def send_data(self, data):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                serialized_data = pickle.dumps(data)
                s.sendall(serialized_data)
                response = s.recv(1024)
                deserialized_response = pickle.loads(response)
                print(f"[{self.name}] Received:", deserialized_response)
        except Exception as e:
            print(f"[{self.name}] Connection error: {e}")

    def add_to_queue(self, data):
        self.queue.put(data)

    def stop(self):
        self.running = False

import time

def main():
    host = '127.0.0.1'  # 服务器IP
    port1 = 65432        # 服务器端口
    port2 = 65431        # 服务器端口

    # 创建多个自定义线程实例
    thread1 = CustomThread(name="Thread-1", host=host, port=port1)
    thread2 = CustomThread(name="Thread-2", host=host, port=port2)

    # 启动线程
    thread1.start()
    thread2.start()

    # 模拟主线程向各自线程的队列中添加内容
    for i in range(5):
        thread1.add_to_queue(f"Message {i} from main to Thread-1")
        thread2.add_to_queue(f"Message {i} from main to Thread-2")
        time.sleep(1)  # 休眠一段时间以模拟实际的任务处理

    # 停止线程
    time.sleep(5)
    thread1.stop()
    thread2.stop()

    # 等待线程结束
    thread1.join()
    thread2.join()

if __name__ == "__main__":
    main()
