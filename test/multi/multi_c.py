import socket

def main():
    # 创建 socket 对象
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 连接服务器
    client_socket.connect(('127.0.0.1', 8888))

    try:
        while True:
            # 输入消息
            message = input("Enter message to send (type 'exit' to quit): ")
            if message.lower() == 'exit':
                break
            # 发送消息到服务器
            client_socket.send(message.encode())

            # 接收服务器返回的消息
            response = client_socket.recv(1024)
            print(f"Received from server: {response.decode()}")
    finally:
        # 关闭客户端socket
        client_socket.close()

if __name__ == "__main__":
    main()
