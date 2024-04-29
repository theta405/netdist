import zmq
import msgpack
import time

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

# 读取文件并发送
filename = "testfile.txt"
with open(filename, "rb") as f:
    filedata = f.read()

# 使用msgpack对文件数据进行序列化
filedata_packed = msgpack.packb(filedata, use_bin_type=True)

socket.send_string(filename)
socket.send(filedata_packed)

start_time = time.time()
response = socket.recv_string()
end_time = time.time()
elapsed_time = end_time - start_time

print(response)
print(f"Elapsed time: {elapsed_time:.2f} seconds")
