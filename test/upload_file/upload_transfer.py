from flask import Flask, request, render_template_string
import socket
import pickle
from struct import Struct

CHUNK_SIZE = 1024
REMOTE_HOST = "0.0.0.0"
REMOTE_PORT = 65432
STRUCT = Struct("!I")

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
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((REMOTE_HOST, REMOTE_PORT))
                order = 1
                while True:
                    chunk = file.read(CHUNK_SIZE)
                    if not chunk:
                        break

                    packet = {
                        "operation": "file",
                        "order": order,
                        "data": chunk,
                        "message": {"file_name": filename}
                    }
                    send_packet(s, packet)
                    print(order)
                    order += 1

                end_packet = {
                    "operation": "stop",
                    "order": order,
                    "data": b'',
                    "message": {"file_name": filename}
                }
                send_packet(s, end_packet)

            
            return 'File successfully uploaded and saved'
    
    return render_template_string(upload_form)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)