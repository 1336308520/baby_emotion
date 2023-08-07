import os
import socket

def send_file_to_host(file_path):
    # 连接主机
    host = '192.168.1.101'  # 替换为主机的IP地址
    port = 12345  # 替换为主机的端口号
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    # 发送文件
    files = {'file': open(filename, 'rb')}
    s.sendall(files)

    # 关闭连接
    s.close()


send_file_to_host('baby_cry.wav')

