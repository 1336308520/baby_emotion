import torch.nn as nn
class FeatureExtractor(nn.Module):
    def __init__(self, model, layer_name):
        super(FeatureExtractor, self).__init__()
        self.model = model
        self.layer_name = layer_name
        self.features = None
        self.register_hooks()

    def register_hooks(self):
        def hook_fn(module, input, output):
            if self.layer_name=='lstm':
                self.features = output[1][0].detach()
            else:
                self.features = output.detach()  # 如果不是，直接对output进行'detach'

        layer = dict([*self.model.named_modules()])[self.layer_name]
        layer.register_forward_hook(hook_fn)

    def forward(self, x):
        _ = self.model(x)
        return self.features
