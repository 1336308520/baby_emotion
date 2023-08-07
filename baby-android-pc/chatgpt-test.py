import socket

# 主机的IP地址和端口号
host = '192.168.1.104'
port = 1234

# 创建socket连接
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))

# 读取wav文件数据
file_path = './baby_cry.wav'
with open(file_path, 'rb') as file:
    file_data = file.read()

# 发送文件数据
client_socket.sendall(file_data)

# 关闭socket连接
client_socket.close()
