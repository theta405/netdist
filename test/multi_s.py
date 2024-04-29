import socket
import threading

def handle_client(client_socket):
    while True:
        # 接收客户端消息
        request = client_socket.recv(1024)
        if not request:
            break
        # 原样返回消息
        client_socket.send(request)

    # 关闭客户端连接
    client_socket.close()

def main():
    # 创建 socket 对象
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 绑定地址和端口
    server_socket.bind(('127.0.0.1', 8888))
    # 开始监听
    server_socket.listen(5)
    print("[*] Listening on 127.0.0.1:8888")

    try:
        while True:
            # 接受客户端连接
            client_socket, addr = server_socket.accept()
            print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
            # 创建线程处理客户端请求
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.start()
    except KeyboardInterrupt:
        print("\n[*] Exiting...")

    # 关闭服务器socket
    server_socket.close()

if __name__ == "__main__":
    main()
