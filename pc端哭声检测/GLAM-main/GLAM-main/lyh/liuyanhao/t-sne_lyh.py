import pickle
from torch.utils.data import TensorDataset, DataLoader
import numpy
import torch.nn.functional as F
from sklearn.decomposition import PCA
import numpy as np
import torch
import torch.nn as nn
import data_loader
from models import *
import matplotlib.pyplot as plt
import matplotlib as mpl
from sklearn.manifold import TSNE
from FeatureExtractor import FeatureExtractor
mpl.use('TkAgg')  # !IMPORTANT
if __name__ == '__main__':
    from torch.utils.data import DataLoader

    # 加载features_mfcc.pkl文件
    with open('features/features_mfcc.pkl', 'rb') as f:
        features = pickle.load(f)
    train_X, train_y, val_dict, info = features['train_X'], features['train_y'], features['val_dict'], features.get(
        'info', '')
    train_data = data_loader.DataSet(train_X, train_y)
    sample = 1280
    x = train_data.X[:sample]
    y = train_data.Y[:sample]

    train_data = torch.tensor(x)
    train_data = train_data.unsqueeze(1)
    train_labels = torch.tensor(y, dtype=torch.long)
    # K = 4  # 假设有4个类别
    # train_labels = torch.nn.functional.one_hot(train_labels, num_classes=K)
    train_dataset = TensorDataset(train_data, train_labels)
    # 定义batch_size和shuffle参数
    batch_size = 128
    shuffle = True
    # 创建dataloader
    dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=shuffle)

    model = AACNN()
    model_path = r'data/model_AACNN_mfcc.pth'
    model.load_state_dict(torch.load(model_path))
    features = []
    labels = []
    layer_name = 'bn5'

    with torch.no_grad():
        for inputs, targets in dataloader:
            feature_extractor = FeatureExtractor(model, layer_name)
            feature = feature_extractor(inputs)
            feature = feature.transpose(0, 1).reshape(batch_size, -1)
            features.append(feature)
            labels.append(targets.numpy())

    features = torch.cat(features,dim=0)
    labels = np.concatenate(labels)
    features = features.view(sample, -1)

    # 对特征进行PCA降维
    # pca = PCA(n_components=None)
    # features_pca = pca.fit_transform(features.reshape((640, -1)))
    # 3. 对特征进行t-SNE降维，并将结果可视化
    tsne = TSNE(n_components=2,random_state=0,perplexity=30,learning_rate=250,n_iter=1000)
    features_tsne = tsne.fit_transform(features)
    name =['awake','diaper','hug','hungry']

    for i in range(4):
        plt.scatter(features_tsne[labels==i, 0], features_tsne[labels==i, 1],label=name[i])
    plt.legend()
    plt.show()
