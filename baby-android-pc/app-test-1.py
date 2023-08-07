import requests
from flask import Flask, request
import wave
import pyaudio
from gevent import pywsgi
import os
import socket
import requests
app = Flask(__name__)


# 发送音频文件到主机
def send_wav_file(filename, host, port):
    url = f"http://192.168.1.102:1235/upload"  # 替换为主机的IP地址和端口号
    files = {'audio': open(filename, 'rb')}
    response = requests.post(url, files=files)

    if response.status_code == 200:
        print("音频文件上传成功！")
        print("情感识别结果:", response.text)
        return response.text
    else:
        print("音频文件上传失败！")



@app.route('/record', methods=['POST'])
def record():
    chunk = 1024
    audio_format = pyaudio.paInt16
    channels = 1
    rate = 16000
    record_seconds = 9
    filename = 'baby_cry.wav'

    frames = []
    p = pyaudio.PyAudio()

    stream = p.open(format=audio_format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    for i in range(int(rate / chunk * record_seconds)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wave_file = wave.open(filename, 'wb')
    wave_file.setnchannels(channels)
    wave_file.setsampwidth(p.get_sample_size(audio_format))
    wave_file.setframerate(rate)
    wave_file.writeframes(b''.join(frames))
    wave_file.close()

    # 发送音频文件到服务器
# 调用发送函数
    result = send_wav_file("baby_cry.wav", "192.168.1.102", 1235)  # 替换为主机的IP地址和端口号
    print(result)
    return result

def get_ip_address():
    # 创建一个临时套接字连接到互联网
    temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    temp_socket.connect(("8.8.8.8", 80))
    ip_address = temp_socket.getsockname()[0]
    temp_socket.close()
    return ip_address

ip_address = get_ip_address()
print("树莓派的IP地址是:", ip_address)
if __name__ == '__main__':
    ip_address = get_ip_address()  # 获取树莓派的IP地址
    server = pywsgi.WSGIServer((ip_address, 1234), app)
    server.serve_forever()
    app.run()

