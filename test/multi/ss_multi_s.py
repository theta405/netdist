import socketserver

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        while True:
            data = str(self.request.recv(1024), 'ascii')
            if data.strip() == 'stop':
                break
            else:
                print(f"Received from {self.client_address[0]}:{self.client_address[1]}: {data}")
            self.request.sendall(bytes(data, 'ascii'))

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    server.serve_forever()
