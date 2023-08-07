from flask import Flask, request
import wave
import pyaudio
from gevent import pywsgi
app = Flask(__name__)

@app.route('/record', methods=['POST'])
def record():
    chunk = 1024
    audio_format = pyaudio.paInt16
    channels = 1
    rate = 44100
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

    return 'Recording saved.'

if __name__ == '__main__':
    server = pywsgi.WSGIServer(('192.168.1.105',5000),app)
    server.serve_forever()
    app.run()
