import os
import librosa
import torch.utils.data as data
import torch
class MyDataset(data.Dataset):
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.classes = os.listdir(root_dir)
        self.class_to_idx = {self.classes[i]: i for i in range(len(self.classes))}
        self.samples = []
        for c in self.classes:
            class_dir = os.path.join(root_dir, c)
            for file_name in os.listdir(class_dir):
                if file_name.endswith('.wav'):
                    file_path = os.path.join(class_dir, file_name)
                    self.samples.append((file_path, self.class_to_idx[c]))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        file_path, label = self.samples[index]
        # 使用 librosa 库加载音频文件并提取 MFCC 特征
        y, sr = librosa.load(file_path, sr=16000)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
        # 将 MFCC 特征转换为 PyTorch 张量
        mfcc_tensor = torch.tensor(mfcc)
        # 返回样本和标签
        return mfcc_tensor, label

