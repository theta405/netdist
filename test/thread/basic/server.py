import socket
import pickle
import sys

def start_server(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print("Server started and listening on", host, port)
        while True:
            conn, addr = s.accept()
            with conn:
                print("Connected by", addr)
                data = conn.recv(1024)
                if not data:
                    break
                deserialized_data = pickle.loads(data)
                print("Received:", deserialized_data)
                response = f"Echo: {deserialized_data}"
                serialized_response = pickle.dumps(response)
                conn.sendall(serialized_response)

if __name__ == "__main__":
    port = int(sys.argv[1])
    start_server(port=port)
