import torch
import torch.nn as nn
import torch.nn.functional as F
from area_attention import AreaAttention
from g_mlp_pytorch import gMLP
from g_mlp_pytorch import SpatialGatingUnit
class ResMultiConv(nn.Module):
    '''
    Multi-scale block with short-cut connections
    '''
    def __init__(self, channels = 16, **kwargs):
        super(ResMultiConv, self).__init__()
        self.conv3 = nn.Conv2d(kernel_size=(3, 3), in_channels=channels, out_channels=channels, padding=1)
        self.conv5 = nn.Conv2d(kernel_size=(5, 5), in_channels=channels, out_channels=channels, padding=2)
        self.bn = nn.BatchNorm2d(channels*2)

    def forward(self, x):
        x3 = self.conv3(x) + x
        x5 = self.conv5(x) + x
        x = torch.cat((x3,x5),1)
        x = self.bn(x)
        x = F.relu(x)
        return x
class GLAM(nn.Module):
    '''
    GLobal-Aware Multiscale block with 3x3 convolutional kernels in CNN architecture
    '''
    def __init__(self, shape=(26,63), **kwargs):
        super(GLAM, self).__init__()
        self.conv1a = nn.Conv2d(kernel_size=(3, 1), in_channels=1, out_channels=16, padding=(1, 0))
        self.conv1b = nn.Conv2d(kernel_size=(1, 3), in_channels=1, out_channels=16, padding=(0, 1))
        self.conv2 = ResMultiConv(16)
        self.conv3 = ResMultiConv(32)
        self.conv4 = ResMultiConv(64)
        self.conv5 = nn.Conv2d(kernel_size=(5, 5), in_channels=128, out_channels=128, padding=2)
        self.maxp = nn.MaxPool2d(kernel_size=(2, 2))
        self.bn1a = nn.BatchNorm2d(16)
        self.bn1b = nn.BatchNorm2d(16)
        self.bn5 = nn.BatchNorm2d(128)
        dim = (shape[0]//2) * (shape[1]//4)
        i = 128 * dim
        self.fc = nn.Linear(in_features=i, out_features=4)
        self.dropout = nn.Dropout(0.5)

        self.gmlp = gMLP(dim = dim, depth = 1, seq_len = 128, act = nn.Tanh())

    def forward(self, *input):
        # input[0]: torch.Size([32, 1, 26, 63])
        xa = self.conv1a(input[0]) # (32, 16, 25, 62)
        xa = self.bn1a(xa) # (32, 16, 25, 62)

        xa = F.relu(xa)
        xb = self.conv1b(input[0])
        xb = self.bn1b(xb)

        xb = F.relu(xb)
        x = torch.cat((xa, xb), 2) # (32, 16, 50, 62)

        x = self.conv2(x) # (32, 32, 50, 62)
        x = self.maxp(x)
        x = self.conv3(x) # (32, 64, 25, 31)
        x = self.maxp(x)
        x = self.conv4(x) # (32, 128, 12, 15)

        x = self.conv5(x)  # (32, 128, 12, 15)
        x = self.bn5(x)
        x = F.relu(x)

        # flatten
        shape = x.shape
        x = x.view(*x.shape[:-2],-1)

        x = self.gmlp(x)
        x = F.relu(x)

        x = x.reshape(x.shape[0], -1)
        x = self.fc(x)
        return x
