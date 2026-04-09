import torch
import argparse
import numpy as np
import torch.nn.functional as F
import cv2
from torch.autograd import Variable
from .models import get_model
from .utils import get_sobel,invert_flow,flowOverlay
from scipy.sparse.linalg import lsqr
import copy
import glob 
from tqdm import tqdm

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def remap_using_flow_fields(image, disp_x, disp_y, interpolation=cv2.INTER_LINEAR, border_mode=cv2.BORDER_CONSTANT):
    """
    opencv remap : carefull here mapx and mapy contains the index of the future position for each pixel
    not the displacement !
    map_x contains the index of the future horizontal position of each pixel [i,j] while map_y contains the index of the future y
    position of each pixel [i,j]

    All are numpy arrays
    :param image: image to remap, HxWxC
    :param disp_x: displacement on the horizontal direction to apply to each pixel. must be float32. HxW
    :param disp_y: isplacement in the vertical direction to apply to each pixel. must be float32. HxW
    :return:
    remapped image. HxWxC
    """
    h_scale, w_scale=image.shape[:2]
    disp_x = cv2.resize(disp_x,(w_scale,h_scale),interpolation=cv2.INTER_LINEAR)/1024*w_scale
    disp_y = cv2.resize(disp_y,(w_scale,h_scale),interpolation=cv2.INTER_LINEAR)/1024*h_scale
    # estimate the grid
    X, Y = np.meshgrid(np.linspace(0, w_scale - 1, w_scale),
                       np.linspace(0, h_scale - 1, h_scale))
    map_x = (X+disp_x).astype(np.float32)
    map_y = (Y+disp_y).astype(np.float32)
    remapped_image = cv2.remap(image, map_x, map_y, interpolation=interpolation, borderMode=border_mode)
    grid = np.stack((map_x/w_scale,map_y/h_scale),axis=-1)
    grid = (grid-0.5)*2

    grid0 = grid[:,:,0]
    grid0 = cv2.resize(grid0,(128,128))
    grid0 = cv2.blur(grid0,(9,9))
    grid0 = cv2.resize(grid0,(w_scale,h_scale),interpolation=cv2.INTER_LINEAR)
    grid1 = grid[:,:,1]
    grid1 = cv2.resize(grid1,(128,128))
    grid1 = cv2.blur(grid1,(9,9))
    grid1 = cv2.resize(grid1,(w_scale,h_scale),interpolation=cv2.INTER_LINEAR)
    grid = np.stack((grid0,grid1),axis=-1)

    return remapped_image,grid


def get_flow(dewarp_im,target_im,model):
    img_size=(1024,1024)
    flat_img_org = target_im
    h_org,w_org = flat_img_org.shape[:2]
    flat_img_resize = cv2.resize(flat_img_org, img_size)

    warp_img_org = dewarp_im
    warp_img_mask = warp_img_org.copy()
    warp_img_mask = cv2.resize(warp_img_mask, (w_org,h_org))
    warp_img_resize = cv2.resize(warp_img_mask, img_size)
    warp_img_org = cv2.resize(warp_img_org, (w_org,h_org))

    warp_img = warp_img_resize.astype(float) / 255.0
    warp_img = (warp_img-0.5)*2
    warp_img = warp_img.transpose(2, 0, 1) # NHWC -> NCHW
    warp_img = np.expand_dims(warp_img, 0)
    warp_img = torch.from_numpy(warp_img).float().cuda()

    flat_img = flat_img_resize.astype(float) / 255.0
    flat_img = (flat_img-0.5)*2
    flat_img = flat_img.transpose(2, 0, 1) # NHWC -> NCHW
    flat_img = np.expand_dims(flat_img, 0)
    flat_img = torch.from_numpy(flat_img).float().cuda()

    input = torch.cat((warp_img,flat_img),dim=1)

    # Predict
    model.eval()
    input = Variable(input.cuda())
    with torch.no_grad():
        _,_,_,_,estimated_flow = model(flat_img,warp_img)
    estimated_flow = estimated_flow[-1].float().squeeze(0).cpu().numpy()

    return estimated_flow

def T_solver(vx,vy,g=None):
    if g is None:
        g = np.ones_like(vx)
    else:
        g = (g-g.min())/(g.max()-g.min())
        g = g.reshape(-1,1)

    size = 1024

    xx1,yy1 = np.meshgrid(np.arange(size),np.arange(size))
    xx1 = xx1.reshape(-1,1)   
    yy1 = yy1.reshape(-1,1)

    xx2 = xx1 + vx
    yy2 = yy1 + vy

    xx2 = xx2[g>0.5]
    yy2 = yy2[g>0.5]
    xx1 = xx1[g>0.5]
    yy1 = yy1[g>0.5]

    new_size_sqr = yy1.shape[0]

    xx2 = xx2.reshape(-1,1)
    t = np.concatenate((xx2, np.zeros_like(xx2)),axis=-1) 
    A1 = t.reshape(-1,1) 
    yy2 = yy2.reshape(-1,1)
    t = np.concatenate((np.zeros_like(yy2),yy2),axis=-1) 
    A2 = t.reshape(-1,1) 
    A3 = np.tile((np.array([1,0]).reshape(2,1)),(new_size_sqr,1))
    A4 = np.tile((np.array([0,1]).reshape(2,1)),(new_size_sqr,1))
    A = np.concatenate((A1,A2,A3,A4),axis=-1)

    yy1 = yy1.reshape(-1,1)
    xx1 = xx1.reshape(-1,1)
    B = np.concatenate((xx1,yy1),axis=-1).reshape(-1,1)
    B = B.reshape(-1,1)
    b = B
    x, istop, itn, normr = lsqr(A, b)[:4]
    Sx,Sy,Tx,Ty = x
    T = np.zeros((3,3))
    T[0,0] = Sx
    T[0,2] = Tx
    T[1,1] = Sy
    T[1,2] = Ty
    T[2,2] = 1
    return Sx,Sy,Tx,Ty,T

def metricInit(checkpoint_path):
    # model
    model = get_model('docaligner', n_classes=2, in_channels=6)
    model = torch.nn.DataParallel(model, device_ids=range(torch.cuda.device_count()))
    model.cuda()
    if not checkpoint_path is None:
        checkpoint = torch.load(checkpoint_path,map_location='cpu')
        model.load_state_dict(checkpoint['model_state'])
    return model

def getDD(model,result_path,gt_path):

    # ## get flow
    dewarp = cv2.imread(result_path)
    target = cv2.imread(gt_path)

    flow = get_flow(dewarp,target,model)

    ### G+T
    # ## get global T 
    gt_sobel = get_sobel(cv2.resize(target,(1024,1024)))
    gt_sobel = (gt_sobel-gt_sobel.min())/(gt_sobel.max()-gt_sobel.min())
    Sx,Sy,Tx,Ty,T = T_solver(flow[0].reshape(-1,1),flow[1].reshape(-1,1),g=gt_sobel)

    ## get dd
    xx,yy = np.meshgrid(np.arange(1024),np.arange(1024))
    vx = copy.deepcopy(flow[0])
    vy = copy.deepcopy(flow[1])

    new_vx = T[0,0]*(vx+xx) + T[0,2] - xx
    new_vy = T[1,1]*(vy+yy) + T[1,2] - yy

    mean_std_new_vx = np.mean(np.std(new_vx,axis=0))
    mean_std_new_vy = np.mean(np.std(new_vy,axis=1))

    H,W = target.shape[:2]
    dd = mean_std_new_vx*H/(H+W)+mean_std_new_vy*W/(H+W)

    ## visualize
    flow_overlay_global_include = flowOverlay(invert_flow(np.stack((vx,vy),-1)),dewarp,arrowscale=0.5,step=60) ## invert target flow to dewarp flow
    flow_overlay_global_exclude = flowOverlay(invert_flow(np.stack((new_vx,new_vy),-1)),dewarp,arrowscale=0.5,step=60) ## invert target flow to dewarp flow

    return dd,flow_overlay_global_include,flow_overlay_global_exclude

_model = None

@torch.no_grad()
def compute_dd(pred_path,gt_path):
    global _model
    if _model is None:
        _model = metricInit('/media/l/disk4/zpr/EvalBench/dd/checkpoint/docaligner.pkl')
    cur_dd, flow_overlay_global_include, flow_overlay_global_exclude = getDD(_model,pred_path,gt_path)
    return cur_dd

if __name__ == '__main__':
    total_dd = 0 
    model = metricInit('checkpoint/docaligner.pkl')

    im_paths = glob.glob('./demo/*_dewarpnet.*')
    for im_path in tqdm(im_paths):
        gt_path = im_path.replace('_dewarpnet.','_target.')
        cur_dd, flow_overlay_global_include, flow_overlay_global_exclude = getDD(model,im_path,gt_path)
        total_dd+=cur_dd
    
    print(total_dd/len(im_paths))
        