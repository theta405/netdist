import psutil
import os

# 获取当前进程的内存使用情况
process = psutil.Process(os.getpid())
memory_info = process.memory_info()

# 输出内存使用情况
print(f"RSS: {memory_info.rss / 1024 / 1024:.2f} MB")
print(f"VMS: {memory_info.vms / 1024 / 1024:.2f} MB")
print(f"Shared Memory: {memory_info.shared / 1024 / 1024:.2f} MB")
print(f"Text: {memory_info.text / 1024 / 1024:.2f} MB")
print(f"Lib: {memory_info.lib / 1024 / 1024:.2f} MB")
print(f"Data: {memory_info.data / 1024 / 1024:.2f} MB")
print(f"Dirty: {memory_info.dirty / 1024 / 1024:.2f} MB")
