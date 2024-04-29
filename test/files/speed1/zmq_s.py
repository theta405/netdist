import zmq
import msgpack
import time

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    # 接收文件名和文件内容
    filename = socket.recv_string()
    filedata_packed = socket.recv()

    start_time = time.time()

    # 使用msgpack解码文件数据
    filedata = msgpack.unpackb(filedata_packed, raw=False)

    # 保存文件到本地
    with open(filename, "wb") as f:
        f.write(filedata)

    end_time = time.time()
    elapsed_time = end_time - start_time
    speed = len(filedata) / (1024 * 1024 * elapsed_time)  # MB/s

    socket.send_string(f"File received successfully. Speed: {speed:.2f} MB/s")
