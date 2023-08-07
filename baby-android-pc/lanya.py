import bluetooth
import subprocess

def record_audio():
    subprocess.run(["arecord", "-d", "9", "-f", "S16_LE", "-r", "44100", "baby_cry.wav"])

server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_socket.bind(("", bluetooth.PORT_ANY))
server_socket.listen(1)

uuid = "00001101-0000-1000-8000-00805F9B34FB"  # UUID用于与Android应用程序匹配
bluetooth.advertise_service(server_socket, "RecordService", service_id=uuid)

print("等待连接...")
client_socket, address = server_socket.accept()
print("已连接：", address)

while True:
    data = client_socket.recv(1024)
    if not data:
        break
    if data.decode() == "record":
        print("收到录音指令")
        record_audio()
        print("录音完成")

client_socket.close()
server_socket.close()
