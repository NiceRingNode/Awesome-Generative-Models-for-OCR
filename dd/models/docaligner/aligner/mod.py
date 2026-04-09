import torch
import torch.nn as nn
import numpy as np
from torch.autograd import Variable


def conv(in_planes, out_planes, kernel_size=3, stride=1, padding=1, dilation=1, batch_norm=False):
    if batch_norm:
        return nn.Sequential(
                            nn.Conv2d(in_planes, out_planes, kernel_size=kernel_size, stride=stride,
                                        padding=padding, dilation=dilation, bias=True),
                            nn.BatchNorm2d(out_planes),
                            nn.LeakyReLU(0.1, inplace=True))
    else:
        return nn.Sequential(
                            nn.Conv2d(in_planes, out_planes, kernel_size=kernel_size, stride=stride,
                            padding=padding, dilation=dilation, bias=True),
                            nn.LeakyReLU(0.1))


def predict_flow(in_planes):
    return nn.Conv2d(in_planes,2,kernel_size=3,stride=1,padding=1,bias=True)


def deconv(in_planes, out_planes, kernel_size=4, stride=2, padding=1):
    deconv_ = nn.ConvTranspose2d(in_planes, out_planes, kernel_size, stride, padding, bias=True)

    nn.init.kaiming_normal_(deconv_.weight.data, mode='fan_in')
    if deconv_.bias is not None:
        deconv_.bias.data.zero_()
    return deconv_


def unnormalise_and_convert_mapping_to_flow(map):
    # here map is normalised to -1;1
    # we put it back to 0,W-1, then convert it to flow
    B, C, H, W = map.size()
    mapping = torch.zeros_like(map)
    # mesh grid
    mapping[:,0,:,:] = (map[:, 0, :, :].float().clone() + 1) * (W - 1) / 2.0 # unormalise
    mapping[:,1,:,:] = (map[:, 1, :, :].float().clone() + 1) * (H - 1) / 2.0 # unormalise

    xx = torch.arange(0, W).view(1,-1).repeat(H,1)
    yy = torch.arange(0, H).view(-1,1).repeat(1,W)
    xx = xx.view(1,1,H,W).repeat(B,1,1,1)
    yy = yy.view(1,1,H,W).repeat(B,1,1,1)
    grid = torch.cat((xx,yy),1).float()

    if mapping.is_cuda:
        grid = grid.cuda()
    flow = mapping - grid
    return flow


class CorrelationVolume(nn.Module):
    """
    Implementation by Ignacio Rocco
    paper: https://arxiv.org/abs/1703.05593
    project: https://github.com/ignacio-rocco/cnngeometric_pytorch
    """

    def __init__(self):
        super(CorrelationVolume, self).__init__()

    def forward(self, feature_A, feature_B):
        b, c, h, w = feature_A.size()

        # reshape features for matrix multiplication
        feature_A = feature_A.transpose(2, 3).contiguous().view(b, c, h * w)  # shape (b,c,h*w)
        feature_B = feature_B.view(b, c, h * w).transpose(1, 2)  # shape (b,h*w,c)
        feature_mul = torch.bmm(feature_B, feature_A)  # shape (b,h*w,h*w)
        correlation_tensor = feature_mul.view(b, h, w, h * w).transpose(2, 3).transpose(1, 2)
        return correlation_tensor  # shape (b,h*w,h,w)


class FeatureL2Norm(nn.Module):
    """
    Implementation by Ignacio Rocco
    paper: https://arxiv.org/abs/1703.05593
    project: https://github.com/ignacio-rocco/cnngeometric_pytorch
    """
    def __init__(self):
        super(FeatureL2Norm, self).__init__()

    def forward(self, feature):
        epsilon = 1e-6
        norm = torch.pow(torch.sum(torch.pow(feature, 2), 1) + epsilon, 0.5).unsqueeze(1).expand_as(feature)
        return torch.div(feature, norm)


class OpticalFlowEstimator(nn.Module):

    def __init__(self, in_channels, batch_norm):
        super(OpticalFlowEstimator, self).__init__()

        dd = np.cumsum([128,128,96,64,32])
        self.conv_0 = conv(in_channels, 128, kernel_size=3, stride=1, batch_norm=batch_norm)
        self.conv_1 = conv(in_channels + dd[0], 128, kernel_size=3, stride=1, batch_norm=batch_norm)
        self.conv_2 = conv(in_channels + dd[1], 96, kernel_size=3, stride=1, batch_norm=batch_norm)
        self.conv_3 = conv(in_channels + dd[2], 64, kernel_size=3, stride=1, batch_norm=batch_norm)
        self.conv_4 = conv(in_channels + dd[3], 32, kernel_size=3, stride=1, batch_norm=batch_norm)
        self.predict_flow = predict_flow(in_channels + dd[4])

    def forward(self, x):
        # dense net connection
        x = torch.cat((self.conv_0(x), x),1)
        x = torch.cat((self.conv_1(x), x),1)
        x = torch.cat((self.conv_2(x), x),1)
        x = torch.cat((self.conv_3(x), x),1)
        x = torch.cat((self.conv_4(x), x),1)
        flow = self.predict_flow(x)
        return x, flow


class OpticalFlowEstimatorNoDenseConnection(nn.Module):

    def __init__(self, in_channels, batch_norm):
        super(OpticalFlowEstimatorNoDenseConnection, self).__init__()
        self.conv_0 = conv(in_channels, 128, kernel_size=3, stride=1, batch_norm=batch_norm)
        self.conv_1 = conv(128, 128, kernel_size=3, stride=1, batch_norm=batch_norm)
        self.conv_2 = conv(128, 96, kernel_size=3, stride=1, batch_norm=batch_norm)
        self.conv_3 = conv(96, 64, kernel_size=3, stride=1, batch_norm=batch_norm)
        self.conv_4 = conv(64, 32, kernel_size=3, stride=1, batch_norm=batch_norm)
        self.predict_flow = predict_flow(32)

    def forward(self, x):
        x = self.conv_4(self.conv_3(self.conv_2(self.conv_1(self.conv_0(x)))))
        flow = self.predict_flow(x)
        return x, flow


# extracted from DGCNet
def conv_blck(in_channels, out_channels, kernel_size=3,
              stride=1, padding=1, dilation=1, bn=False):
    if bn:
        return nn.Sequential(nn.Conv2d(in_channels, out_channels, kernel_size,
                                       stride, padding, dilation),
                             nn.BatchNorm2d(out_channels),
                             nn.ReLU(inplace=True))
    else:
        return nn.Sequential(nn.Conv2d(in_channels, out_channels, kernel_size,
                                       stride, padding, dilation),
                             nn.ReLU(inplace=True))


def conv_head(in_channels):
    return nn.Conv2d(in_channels, 2, kernel_size=3, padding=1)


class CorrespondenceMapBase(nn.Module):
    def __init__(self, in_channels, bn=False):
        super().__init__()

    def forward(self, x1, x2=None, x3=None):
        x = x1
        # concatenating dimensions
        if (x2 is not None) and (x3 is None):
            x = torch.cat((x1, x2), 1)
        elif (x2 is None) and (x3 is not None):
            x = torch.cat((x1, x3), 1)
        elif (x2 is not None) and (x3 is not None):
            x = torch.cat((x1, x2, x3), 1)

        return x


class CMDTop(CorrespondenceMapBase):
    def __init__(self, in_channels, bn=False):
        super().__init__(in_channels, bn)
        chan = [128, 128, 96, 64, 32]
        self.conv0 = conv_blck(in_channels, chan[0], bn=bn)
        self.conv1 = conv_blck(chan[0], chan[1], bn=bn)
        self.conv2 = conv_blck(chan[1], chan[2], bn=bn)
        self.conv3 = conv_blck(chan[2], chan[3], bn=bn)
        self.conv4 = conv_blck(chan[3], chan[4], bn=bn)
        self.final = conv_head(chan[-1])

    def forward(self, x1, x2=None, x3=None):
        x = super().forward(x1, x2, x3)
        x = self.conv4(self.conv3(self.conv2(self.conv1(self.conv0(x)))))
        return self.final(x)


def warp(x, flo):
    """
    warp an image/tensor (im2) back to im1, according to the optical flow

    x: [B, C, H, W] (im2)
    flo: [B, 2, H, W] flow

    """
    B, C, H, W = x.size()
    # mesh grid
    xx = torch.arange(0, W).view(1, -1).repeat(H, 1)
    yy = torch.arange(0, H).view(-1, 1).repeat(1, W)
    xx = xx.view(1, 1, H, W).repeat(B, 1, 1, 1)
    yy = yy.view(1, 1, H, W).repeat(B, 1, 1, 1)
    grid = torch.cat((xx, yy), 1).float()

    if x.is_cuda:
        grid = grid.cuda()
    vgrid = grid + flo
    # makes a mapping out of the flow

    # scale grid to [-1,1]
    vgrid[:, 0, :, :] = 2.0 * vgrid[:, 0, :, :].clone() / max(W - 1, 1) - 1.0
    vgrid[:, 1, :, :] = 2.0 * vgrid[:, 1, :, :].clone() / max(H - 1, 1) - 1.0

    vgrid = vgrid.permute(0, 2, 3, 1)

    if float(torch.__version__[:3]) >= 1.3:
        output = nn.functional.grid_sample(x, vgrid, align_corners=True)
    else:
        output = nn.functional.grid_sample(x, vgrid)
    return output