import io
import json
# 安装所需工具包
import flask
import torch
import torch
import torch.nn.functional as F
from PIL import Image
from torch import nn
from torchvision import transforms as T
from torchvision.models import resnet50
from torch.autograd import Variable
# 初始化Flask app
app = flask.Flask(__name__)
model = None
use_gpu = False
import librosa
import numpy as np
from feature_util_lyh import FeatureExtractor

# Load the audio file
audio_file = 'path/to/audio/file.wav'
signal, sr = librosa.load(audio_file, sr=16000)

# Define the frame length and hop length
frame_length = int(sr * 0.025)
hop_length = int(sr * 0.010)

# Split the audio signal into frames
frames = librosa.util.frame(signal, frame_length=frame_length, hop_length=hop_length)

# Truncate the last frame if it is shorter than the frame length
if frames.shape[1] < frame_length:
    frames = frames[:, :-1]

# Apply pre-emphasis to each frame
frames = librosa.effects.preemphasis(frames)

# Apply windowing to each frame
frames *= np.hamming(frame_length)[:, np.newaxis]

# Extract the features from each frame
fe = FeatureExtractor(sample_rate=sr, nmfcc=26)
features = fe.get_features('mfcc', frames.T[np.newaxis, ...])
# 返回结果用的
with open('imagenet_class.txt', 'r') as f:
    idx2label = eval(f.read())

# 加载模型进来
def load_model():
    """Load the pre-trained model, you can use your model just as easily.

    """
    global model
    model = resnet50(pretrained=True)
    model.eval()
    if use_gpu:
        model.cuda()

# 数据预处理
def prepare_wav(image, ):

    return Variable(image, volatile=True) #不需要求导

# 开启服务
@app.route("/predict", methods=["POST"])
def predict():
    # Initialize the data dictionary that will be returned from the view.
    data = {"success": False}

    # Ensure an image was properly uploaded to our endpoint.
    if flask.request.method == 'POST':
        if flask.request.files.get("image"):
            # Read the image in PIL format
            image = flask.request.files["image"].read()
            image = Image.open(io.BytesIO(image)) #二进制数据

            # Preprocess the image and prepare it for classification.
            image = prepare_image(image, target_size=(224, 224))

            # Classify the input image and then initialize the list of predictions to return to the client.
            preds = F.softmax(model(image), dim=1)
            results = torch.topk(preds.cpu().data, k=3, dim=1)
            results = (results[0].cpu().numpy(), results[1].cpu().numpy())

            data['predictions'] = list()

            # Loop over the results and add them to the list of returned predictions
            for prob, label in zip(results[0][0], results[1][0]):
                label_name = idx2label[label]
                r = {"label": label_name, "probability": float(prob)}
                data['predictions'].append(r)

            # Indicate that the request was a success.
            data["success"] = True

    # Return the data dictionary as a JSON response.
    return flask.jsonify(data)


if __name__ == '__main__':
    print("Loading PyTorch model and Flask starting server ...")
    print("Please wait until server has fully started")
    load_model()
    app.run()