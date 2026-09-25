import numpy as np
from PIL import Image, ImageFilter
import cv2
# temporal median of the static hub (25.0-26.5s) - eye region in source px
x0,y0,x1,y1=180,150,420,290
stack=[]
for f in range(int(25.0*30),int(26.5*30)):
    im=np.asarray(Image.open(f'analysis/frames/f_{f+1:05d}.jpg').convert('RGB')).astype(np.float32)
    stack.append(im[y0:y1,x0:x1])
med=np.median(np.stack(stack),axis=0)
# normalise: push near-white paper to pure white so multiply blend leaves no box
lum=med.mean(axis=2,keepdims=True)
white=np.percentile(med.reshape(-1,3),97,axis=0)
med=np.clip(med/white*255,0,255)
S=1920/854
W,H=int(round((x1-x0)*S)),int(round((y1-y0)*S))
up=cv2.resize(med,(W,H),interpolation=cv2.INTER_LANCZOS4)
# gentle unsharp to counter the upscale softness
bl=cv2.GaussianBlur(up,(0,0),2.0); up=np.clip(up*1.35-bl*0.35,0,255)
# feather edges to white
yy,xx=np.mgrid[0:H,0:W]; e=np.minimum.reduce([xx,yy,W-1-xx,H-1-yy]).astype(np.float32)
m=np.clip(e/40.0,0,1)[...,None]
up=up*m+255*(1-m)
Image.fromarray(up.astype(np.uint8)).save('analysis/ref/eye_up.png')
# blur ladder: horizontal smear dominant, 24 levels (level 0 = sharp)
N=24
for k in range(N):
    sx=0.0 if k==0 else (k/(N-1))**1.3*38.0   # up to ~38px @1080p horizontally
    sy=sx*0.28
    if k==0: out=up
    else: out=cv2.GaussianBlur(up,(0,0),sigmaX=sx,sigmaY=max(0.1,sy),borderType=cv2.BORDER_REPLICATE)
    Image.fromarray(np.clip(out,0,255).astype(np.uint8)).save(f'build/assets/eye/eye_{k:02d}.jpg',quality=90)
print(W,H,'levels',N)
