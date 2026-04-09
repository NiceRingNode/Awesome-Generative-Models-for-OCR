import torch
import torch.nn as nn
import torchvision.models as models
from collections import OrderedDict
import torch.nn.functional as F


class ResNetPyramid(nn.Module):
    def __init__(self, train=False):
        super().__init__()
        self.n_levels = 5
        self.model = models.resnet18(pretrained=True)
        modules = OrderedDict()
        n_block = 0


        self.resnet_module_list = [self.model.conv1,
                              self.model.bn1,
                              self.model.relu,
                              self.model.maxpool,
                              self.model.layer1,
                              self.model.layer2,
                              self.model.layer3,
                              self.model.layer4]

        modules['level_0'] = nn.Sequential(*[self.model.conv1,
                                              self.model.bn1,
                                              self.model.relu]) #H_2
        for param in modules['level_0'].parameters():
            param.requires_grad = train

        modules['level_1'] = nn.Sequential(*[self.model.maxpool,
                                             self.model.layer1])  # H_4
        for param in modules['level_1'].parameters():
            param.requires_grad = train

        modules['level_2'] = nn.Sequential(*[self.model.layer2]) #H/8
        for param in modules['level_2'].parameters():
            param.requires_grad = train
        modules['level_3'] = nn.Sequential(*[self.model.layer3]) #H/16
        for param in modules['level_3'].parameters():
            param.requires_grad = train
        modules['level_4'] = nn.Sequential(*[self.model.layer4])  #H/32
        for param in modules['level_4'].parameters():
            param.requires_grad = train
        self.__dict__['_modules'] = modules

    def forward(self, x, quarter_resolution_only=False, eigth_resolution=False):
        outputs = []
        if quarter_resolution_only:
            x_half = self.__dict__['_modules']['level_0'](x)
            x_quarter = self.__dict__['_modules']['level_1'](x_half)
            outputs.append(x_quarter)
        elif eigth_resolution:
            x_half = self.__dict__['_modules']['level_0'](x)
            x_quarter = self.__dict__['_modules']['level_1'](x_half)
            outputs.append(x_quarter)
            x_eight = self.__dict__['_modules']['level_2'](x_quarter)
            outputs.append(x_eight)
        else:
            for layer_n in range(0, self.n_levels):
                x = self.__dict__['_modules']['level_' + str(layer_n)](x)
                outputs.append(x)
            # import pdb;pdb.set_trace()
            x = torch.nn.functional.interpolate(x, scale_factor=0.5, mode='area')
            outputs.append(x)
            # it will contain [H/2, H/4, H/8, H/16, H/32, H/64]
        return outputs

class ResNetcontext(nn.Module):
    def __init__(self, train=False):
        super().__init__()
        self.n_levels = 5
        self.model = models.resnet50(pretrained=True)
        modules = OrderedDict()
        n_block = 0

        modules['level_0'] = nn.Sequential(*[self.model.conv1,
                                              self.model.bn1,
                                              self.model.relu]) #H_2
        for param in modules['level_0'].parameters():
            param.requires_grad = train
        

        modules['level_1'] = nn.Sequential(*[self.model.maxpool,
                                             self.model.layer1,
                                             nn.Conv2d(256,192,1,1)])  # H_4

        for param in modules['level_1'].parameters():
            param.requires_grad = train

        # modules['level_2'] = nn.Sequential(*[self.model.layer2]) #H/8
        # for param in modules['level_2'].parameters():
        #     param.requires_grad = train
        # modules['level_3'] = nn.Sequential(*[self.model.layer3]) #H/16
        # for param in modules['level_3'].parameters():
        #     param.requires_grad = train
        # modules['level_4'] = nn.Sequential(*[self.model.layer4])  #H/32
        # for param in modules['level_4'].parameters():
        #     param.requires_grad = train
        self.__dict__['_modules'] = modules
        self.model = None

    def forward(self, x, quarter_resolution_only=False, eigth_resolution=False):
        outputs = []
        # if quarter_resolution_only:
        x_half = self.__dict__['_modules']['level_0'](x)
        x_quarter = self.__dict__['_modules']['level_1'](x_half)
        outputs.append(x_quarter)
        # elif eigth_resolution:
        #     x_half = self.__dict__['_modules']['level_0'](x)
        #     x_quarter = self.__dict__['_modules']['level_1'](x_half)
        #     outputs.append(x_quarter)
        #     x_eight = self.__dict__['_modules']['level_2'](x_quarter)
        #     outputs.append(x_eight)
        # else:
        #     for layer_n in range(0, self.n_levels):
        #         x = self.__dict__['_modules']['level_' + str(layer_n)](x)
        #         outputs.append(x)
        #     # import pdb;pdb.set_trace()
        #     x = torch.nn.functional.interpolate(x, scale_factor=0.5, mode='area')
            # it will contain [H/2, H/4, H/8, H/16, H/32, H/64]
        return outputs
