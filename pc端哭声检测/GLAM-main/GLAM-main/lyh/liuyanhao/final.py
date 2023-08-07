from flask import Flask, request
import librosa
import numpy as np
import torch
from feature_util_lyh import FeatureExtractor
from python_speech_features import mfcc
import models
from flask_socketio import SocketIO, emit
import feature_util_lyh
app = Flask(__name__)

# Load the trained PyTorch model
# 加载预训练的情感识别模型
state_dict = torch.load("model_CNN_Area_mfcc.pth")  # 替换为你的情感识别模型文件路径
# 创建模型对象
model = models.CNN_Area()  # 替换为你的模型类
# 将状态字典加载到模型中
model.load_state_dict(state_dict)
model.eval()
# Define the feature extractor
fe = FeatureExtractor(sample_rate=16000, nmfcc=26)


def preprocess_wav_file(wav_file_path, sample_rate=16000, nmfcc=26):
    # 读取音频文件
    wavfile, _ = librosa.load(wav_file_path, sr=sample_rate)
    #提取特征,预处理，返回形式（segments，26，63）
    X1 = feature_util_lyh.segment(wavfile,
                 sample_rate=sample_rate,
                 segment_length=2,
                 overlap=1,
                 padding=False)
    feature_extractor = FeatureExtractor(sample_rate, nmfcc)
    X1 = feature_extractor.get_features('mfcc', X1)
    x = torch.from_numpy(X1).float()
    if (x.size(0) == 1):
        x = torch.cat((x, x), 0)
    with torch.no_grad():
        out = model(x.unsqueeze(1))
    pred = out.mean(dim=0)
    pred = torch.max(pred, 0)[1].cpu().numpy()
    pred = int(pred)
    return pred
@app.route('/upload', methods=['POST'])
def predict():
    # Load the audio file from the request
    print("接收文件成功")
    wav_file_path = request.files['audio']
    print(wav_file_path)
    # 读取音频文件
    pred = preprocess_wav_file(wav_file_path, sample_rate=16000, nmfcc=26)
    label_mapping = {
        0: 'awake',
        1: 'diaper',
        2: 'hug',
        3: 'hungry'
    }
    pred_str = label_mapping[pred]
    print(pred_str)
    # Return the predicted class label as a JSON response
    return {'class': pred_str}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1235)