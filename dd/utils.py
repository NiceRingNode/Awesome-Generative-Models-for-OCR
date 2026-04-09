'''
Misc Utility functions
'''
from collections import OrderedDict
import numpy as np
import torch
import cv2
import matplotlib.pyplot as plt

def flow2normmap(flow,size=1024):
    bs,n,w,h = flow.shape
    x, y = np.meshgrid(np.arange(size),np.arange(size))
    base_cord = np.stack((x,y),axis=0)
    base_cord = np.tile(np.expand_dims(base_cord,axis=0),(bs,1,1,1))
    base_cord = torch.from_numpy(base_cord).to(flow.device)
    map = ((flow+base_cord)/size-0.5)*2
    return map
def torch2cvimg(tensor,min=0,max=1):
    '''
    input:
        tensor -> torch.tensor BxCxHxW C can be 1,3
    return
        im -> ndarray uint8 HxWxC 
    '''
    im_list = []
    for i in range(tensor.shape[0]):
        im = tensor.detach().cpu().data.numpy()[i]
        im = im.transpose(1,2,0)
        im = np.clip(im,min,max)
        im = ((im-min)/(max-min)*255).astype(np.uint8)
        im_list.append(im)
    return im_list
def cvimg2torch(img,min=0,max=1):
    '''
    input:
        im -> ndarray uint8 HxWxC 
    return
        tensor -> torch.tensor BxCxHxW 
    '''
    if len(img.shape)==2:
        img = np.expand_dims(img,axis=-1)
    img = img.astype(float) / 255.0
    img = img.transpose(2, 0, 1) # NHWC -> NCHW
    img = np.expand_dims(img, 0)
    img = torch.from_numpy(img).float()
    return img

def get_sobel(img):
    x = cv2.Sobel(img,cv2.CV_16S,1,0)  
    y = cv2.Sobel(img,cv2.CV_16S,0,1)  
    absX = cv2.convertScaleAbs(x)   # 转回uint8  
    absY = cv2.convertScaleAbs(y)  
    high_frequency = cv2.addWeighted(absX,0.5,absY,0.5,0)
    high_frequency = cv2.cvtColor(high_frequency,cv2.COLOR_BGR2GRAY)
    return high_frequency


def flow_reverse(f):
    # ÊäÈë¹âÁ÷ f µÄ shape
    h, w, _ = f.shape

    # ŒÆËãÍøžñµã×ø±ê
    X, Y = np.meshgrid(np.arange(w), np.arange(h))

    # ŒÆËã¶ÔÓŠÍŒÏñµÄ×ø±ê
    coord1 = np.stack([X, Y], axis=-1).reshape(-1, 2)
    coord2 = np.clip(coord1 + f.reshape(-1, 2), [[0, 0]], [[w - 1, h - 1]])

    # œ»»»×ø±êµÄË³Ðò
    coord1, coord2 = coord2, coord1

    # ŒÆËãÐÂµÄ¹âÁ÷
    flow = coord2 - coord1

    # œ«ÐÂµÄ¹âÁ÷·µ»Ø
    return flow.reshape((h, w, 2))

def flow2sparsearrow(flow,arrowscale=2,step=60):
    H,W=flow.shape[:2]

    x = np.arange(W)
    y = np.arange(H)
    X, Y = np.meshgrid(x, y)

    # 分离偏移量 (dx, dy)
    dx = flow[:, :, 0]
    dy = flow[:, :, 1]

    # 设置采样步长（稀疏化）
    X_sparse = X[::step, ::step]
    Y_sparse = Y[::step, ::step]
    dx_sparse = dx[::step, ::step]
    dy_sparse = dy[::step, ::step]

    # 绘制箭头图
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.quiver(X_sparse, Y_sparse, dx_sparse, dy_sparse, angles='xy', scale_units='xy', scale=arrowscale, color='blue')
    plt.gca().invert_yaxis()
    ax.axis('off')

    ## 转换为 OpenCV 格式（RGB 转 BGR）
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    # fig.patch.set_alpha(0)  # 整个图像背景透明
    # ax.set_facecolor((0, 0, 0, 0))  # 坐标区域背景透明
    fig.canvas.draw()
    flow_arrow = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    flow_arrow = flow_arrow.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    flow_arrow = cv2.cvtColor(flow_arrow, cv2.COLOR_RGB2BGR)
    plt.close()
    return flow_arrow


def invert_flow(flow_t_to_s):
    """
    将 `target` 到 `source` 的光流反转为 `source` 到 `target` 的光流。
    
    参数:
    - flow_t_to_s: numpy 数组，形状为 (H, W, 2)，表示 `target` 到 `source` 的光流。
    
    返回:
    - flow_s_to_t: numpy 数组，形状为 (H, W, 2)，表示 `source` 到 `target` 的光流。
    """
    H, W, _ = flow_t_to_s.shape

    # 初始化 source 到 target 的 flow
    flow_s_to_t = np.zeros_like(flow_t_to_s)
    counts = np.zeros((H, W))  # 记录每个 source 像素被映射的次数

    # 遍历 target 图的每个像素
    for y in range(H):
        for x in range(W):
            dx, dy = flow_t_to_s[y, x]
            sx = int(x + dx)
            sy = int(y + dy)

            # 如果映射的位置在 source 图范围内
            if 0 <= sx < W and 0 <= sy < H:
                flow_s_to_t[sy, sx, 0] += -dx  # 反向偏移
                flow_s_to_t[sy, sx, 1] += -dy
                counts[sy, sx] += 1

    # 平均化处理
    valid = counts > 0
    flow_s_to_t[valid, 0] /= counts[valid]
    flow_s_to_t[valid, 1] /= counts[valid]

    return flow_s_to_t

def flowOverlay(flow,im,arrowscale=2,step=60):
    ## get flow arrow
    flow_arrow = flow2sparsearrow(flow,arrowscale=arrowscale,step=step)
    flow_arrow = cv2.resize(flow_arrow,im.shape[:2][::-1])
    ## seamlessclone
    mask = np.ones(im.shape, im.dtype)*255
    w, h = flow_arrow.shape[:2]
    center = (h // 2, w // 2)
    mixed_clone = cv2.seamlessClone(flow_arrow,im,mask, center, cv2.MIXED_CLONE)
    return mixed_clone