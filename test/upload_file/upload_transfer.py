from flask import Flask, request, render_template_string
import socket
import pickle
from struct import Struct

CHUNK_SIZE = 1024
REMOTE_HOST = "0.0.0.0"
REMOTE_PORT = 65432
STRUCT = Struct("!I")
TIMEOUT = 5
WINDOW_SIZE = 50  # 窗口大小

app = Flask(__name__)

upload_form = '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>File Upload</title>
  </head>
  <body>
    <h1>Upload a File</h1>
    <form method="post" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
  </body>
</html>
'''

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

def send_with_ack(sock, packet):
    while True:
        send_packet(sock, packet)
        sock.settimeout(TIMEOUT)
        ack = receive_ack(sock)
        if ack == packet['order']:
            break

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # 检查是否有文件被上传
        if 'file' not in request.files:
            return 'No file part'
        
        file = request.files['file']
        
        # 如果用户没有选择文件，浏览器提交空文件（没有文件名）
        if file.filename == '':
            return 'No selected file'
        
        # 分片读取文件并写入本地文件
        if file:
            filename = file.filename
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((REMOTE_HOST, REMOTE_PORT))
                    order = 1
                    while True:
                        print(order)
                        chunk = file.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        packet = {
                            "operation": "file",
                            "order": order,
                            "data": chunk,
                            "message": {"file_name": filename}
                        }
                        send_with_ack(s, packet)
                        order += 1

                    # 发送结束标志
                    end_packet = {
                        "operation": "stop",
                        "order": order,
                        "data": b'',
                        "message": {"file_name": filename}
                    }
                    send_with_ack(s, end_packet)
            except Exception as e:
                print(f"An error occurred: {e}")
            
            return 'File successfully uploaded and saved'
    
    return render_template_string(upload_form)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)