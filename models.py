import torch
import torch.nn as nn
import torch.nn.functional as F


class encoder_net(nn.Module):
    def __init__(self):
        super(encoder_net, self).__init__()
        self.conv1 = nn.Conv2d(1, 64, kernel_size=3, stride=2, padding=1, bias=False)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1, bias=False)
        self.conv3 = nn.Conv2d(128, 128, kernel_size=3, stride=2, padding=1, bias=False)
        self.conv4 = nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1, bias=False)
        self.conv5 = nn.Conv2d(256, 256, kernel_size=3, stride=2, padding=1, bias=False)
        self.conv6 = nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1, bias=False)
        self.conv7 = nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1, bias=False)
        self.conv8 = nn.Conv2d(512, 256, kernel_size=3, stride=1, padding=1, bias=False)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x = F.relu(self.conv4(x))
        x = F.relu(self.conv5(x))
        x = F.relu(self.conv6(x))
        x = F.relu(self.conv7(x))
        x = F.relu(self.conv8(x))
        return x


class decoder_net(nn.Module):
    def __init__(self):
        super(decoder_net, self).__init__()
        self.conv1 = nn.Conv2d(256, 128, kernel_size=3, stride=1, padding=1, bias=False)
        self.conv2 = nn.Conv2d(128, 64, kernel_size=3, stride=1, padding=1, bias=False)
        self.conv3 = nn.Conv2d(64, 32, kernel_size=3, stride=1, padding=1, bias=False)
        self.conv4 = nn.Conv2d(32, 16, kernel_size=3, stride=1, padding=1, bias=False)
        self.conv5 = nn.Conv2d(16, 8, kernel_size=3, stride=1, padding=1, bias=False)
        self.conv6 = nn.Conv2d(8, 2, kernel_size=3, stride=1, padding=1, bias=False)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.upsample(x, scale_factor = 2)
        x = F.relu(self.conv2(x))
        x = F.upsample(x, scale_factor = 2)
        x = F.relu(self.conv3(x))
        x = F.relu(self.conv4(x))
        x = F.relu(self.conv5(x))
        x = F.tanh(self.conv6(x))
        x = F.upsample(x, scale_factor = 2)
        return x


class complete_net(nn.Module):
    def __init__(self):
        super(complete_net, self).__init__()
        self.encoder = encoder_net()
        self.conv1 = nn.Conv2d(1256, 256, kernel_size=1, stride=1, padding=0, bias=False)
        self.decoder = decoder_net()

    def forward(self, x, emd):
        end = self.encoder(x)
        # concate end and emd to mix
        emd = emd.unsqueeze(1)
        emd = emd.expand(end.shape[0], 32, 32, 1000)
        emd = emd.transpose(1, 3)
        mix = torch.cat((end, emd), 1)
        mix = F.relu(self.conv1(mix))
        res = self.decoder(mix)
        return res