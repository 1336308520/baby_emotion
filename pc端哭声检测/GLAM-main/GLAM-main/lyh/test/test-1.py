import socket
import subprocess
import torch
import torchaudio
import numpy as np
import models
# 加载预训练的情感识别模型
state_dict = torch.load("model_CNN_Area_mfcc.pth")  # 替换为你的情感识别模型文件路径
# 创建模型对象
model = models.CNN_Area()  # 替换为你的模型类
# 将状态字典加载到模型中
model.load_state_dict(state_dict)
model.eval()

# 预处理音频
def preprocess_audio(filename):
    waveform, sample_rate = torchaudio.load(filename)
    # 进行音频预处理操作，例如降噪、特征提取等
    # ...

    return waveform

# 情感识别
def recognize_emotion(waveform):
    # 在这里调用你的情感识别模型进行推理
    # ...

    # 示例：假设模型输出为"happy"
    emotion = "happy"

    return emotion

# 接收wav文件并进行处理
def process_wav_file(filename):
    # 预处理音频
    waveform = preprocess_audio(filename)

    # 情感识别
    emotion = recognize_emotion(waveform)

    return emotion

# 监听端口并处理连接请求
def listen_and_process(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(1)

    print("等待连接...")

    while True:
        conn, addr = sock.accept()
        print("连接成功！来自：", addr)

        # 接收wav文件
        with open("received.wav", "wb") as f:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                f.write(data)

        conn.close()

        # 处理接收到的wav文件
        emotion = process_wav_file("received.wav")
        print(emotion)

        # 发送情感识别结果给Android app
        #send_emotion_result(emotion)

# 向Android app发送情感识别结果
def send_emotion_result(emotion):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("Android app的IP地址", 54321))  # 替换为Android app的IP地址和端口号

    # 发送情感识别结果字符串
    sock.sendall(emotion.encode())

    sock.close()

# 启动监听
listen_and_process("0.0.0.0", 1234)  # 监听所有网络接口的12345端口
