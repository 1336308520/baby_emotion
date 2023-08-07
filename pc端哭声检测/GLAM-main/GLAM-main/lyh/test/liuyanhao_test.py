import socket

# 主机IP地址和端口号
host = '0.0.0.0'  # 监听所有网络接口
port = 1234

# 创建socket连接
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
# 监听连接
server_socket.listen(1)

print("等待连接...")
# 接受客户端连接
client_socket, addr = server_socket.accept()
print("连接地址:", addr)
# 接收文件数据
file_data = b""
while True:
    data = client_socket.recv(4096)
    if not data:
        break
    file_data += data
# 保存接收到的文件数据
save_path = 'baby_cry.wav'
with open(save_path, 'wb') as file:
    file.write(file_data)

# 在这里使用深度学习模型处理接收到的文件数据

# 关闭socket连接
client_socket.close()
server_socket.close()
