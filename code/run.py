#!/usr/bin/python3

import aliLink,mqttd,rpi
import time,json
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
    url = f"http://192.168.0.104:1235/upload"  # 替换为主机的IP地址和端口号
    files = {'audio': open(filename, 'rb')}
    response = requests.post(url, files=files)

    if response.status_code == 200:
        print("音频文件上传成功！")
        print("情感识别结果:", response.text)
        return response.text
    else:
        print("音频文件上传失败！")

# 三元素（iot后台获取）
ProductKey = 'k022e8OSwlm'
DeviceName = 'raspi_dev'
DeviceSecret = "483f7e9f8cc7376279856d7181bfe818"
# topic (iot后台获取)
POST = '/sys/k022e8OSwlm/raspi_dev/thing/event/property/post'  # 上报消息到云
#POST_REPLY = '/sys/a1Wb3NoSU9z/raspberrypi4-00001/thing/event/property/post_reply'  
SET = '/sys/k022e8OSwlm/app_dev/thing/service/property/set'  # 订阅云端指令


# 消息回调（云端下发消息的回调函数）
def on_message(client, userdata, msg):
    try:
        Msg = json.loads(msg.payload)
        detect_value = Msg.get('items', {}).get('detect', {}).get('value')
        if detect_value == 1:
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
            result = send_wav_file("baby_cry.wav", "192.168.0.104", 1235)               
            emotion = result
            updateMsn = {
                "emotion": emotion,
                "detect": 0,
            }
            JsonUpdataMsn = aliLink.Alink(updateMsn)
            print("成功的")
            mqtt.push(POST, JsonUpdataMsn)
    except Exception as e:
        print("处理消息时出现异常:", e)

 #   if(Msg.items.detect.value == 1):
    #    print("成功")
   # print(Msg) 

#连接回调（与阿里云建立链接后的回调函数）
def on_connect(client, userdata, flags, rc):
    pass


# 链接信息
Server,ClientId,userNmae,Password = aliLink.linkiot(DeviceName,ProductKey,DeviceSecret)

# mqtt链接
mqtt = mqttd.MQTT(Server,ClientId,userNmae,Password)
mqtt.subscribe(SET) # 订阅服务器下发消息topic
mqtt.begin(on_message,on_connect)

#while True:
    #time.sleep(3)
    # 信息获取上报，每10秒钟上报一次系统参数
    #while True:
     #   time.sleep(10)
        # 构建与云端模型一致的消息结构

