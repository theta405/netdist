import json
import socket as socket_module
import zmq
import msgpack
import threading

# 快速响应消息
def send_message(sock, operation, status, data):
    message = {
        "operation": operation,
        "status": status,
        "data": data
    }
    sock.send(json.dumps(message).encode())

def receive_message(sock):
    data = sock.recv(1024).decode()
    print(data)
    message = json.loads(data)
    return message

# 高速传输数据
def send_data(socket, data):
    packed_data = msgpack.packb(data)
    socket.send(packed_data)

def receive_data(socket):
    packed_data = socket.recv()
    data = msgpack.unpackb(packed_data)
    return data

def handle_client(zmq_socket, client_socket, address):
    print(f"Connected to slave node: {address}")

    while True:
        # 接收从节点消息
        message = receive_message(client_socket)
        print(f"Received message: {message}")

        # 检查消息内容，如果满足条件则发送快速响应消息和高速传输数据
        if message.get("operation") == "specific_operation":
            # 发送快速响应消息
            send_message(client_socket, "command", 200, {"key": "value"})

            # 发送高速传输数据
            data = [1, 2, 3, 4, 5]
            send_data(zmq_socket, data)

        if message.get("operation") == "stop":
            send_message(client_socket, "stopped", 200, {"key": "value"})
            client_socket.close()
            break


# 主节点
def master_node():
    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.bind("tcp://*:5555")

    server_socket = socket_module.socket(socket_module.AF_INET, socket_module.SOCK_STREAM)
    server_socket.bind(("localhost", 8888))
    server_socket.listen(1)

    print("Master node started.")

    while True:
        threading.Thread(target=handle_client, args=(zmq_socket, *server_socket.accept()))


# 从节点
def slave_node():
    context = zmq.Context()
    zmq_socket = context.socket(zmq.PULL)
    zmq_socket.connect("tcp://localhost:5555")

    client_socket = socket_module.socket(socket_module.AF_INET, socket_module.SOCK_STREAM)
    client_socket.connect(("localhost", 8888))

    print("Slave node started.")

    while True:
        cmd = input("Cmd: ")
        if cmd == "s":
            send_message(client_socket, "stop", 200, {})
            client_socket.close()
            break
        else:
            # 接收快速响应消息
            send_message(client_socket, "specific_operation", 200, {"key": "val"})
            message = receive_message(client_socket)
            print(f"Received message: {message}")

            # 接收高速传输数据
            data = receive_data(zmq_socket)
            print(f"Received data: {data}")


# 主程序入口
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "master":
        master_node()
    else:
        slave_node()
