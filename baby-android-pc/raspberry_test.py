import socket
import pyaudio
import wave

# 定义录音参数
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

# 定义套接字参数
HOST = '192.168.1.102'  # 树莓派的IP地址
PORT = 1234  # 与Android应用程序中使用的端口号相同

# 初始化PyAudio
audio = pyaudio.PyAudio()

# 创建套接字并开始监听
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    print("开始监听")
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            if data.decode() == 'START_RECORDING':
                print('Start recording...')
                # 打开音频流
                stream = audio.open(format=FORMAT, channels=CHANNELS,
                                    rate=RATE, input=True,
                                    frames_per_buffer=CHUNK)
                frames = []
                # 录制音频
                for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                    data = stream.read(CHUNK)
                    frames.append(data)
                # 关闭音频流
                stream.stop_stream()
                stream.close()
                audio.terminate()
                # 保存音频文件
                wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()
                print('Recording finished.')