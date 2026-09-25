import cv2, numpy as np, json
def load(t):
    f=int(round(t*30)); im=cv2.imread(f'analysis/frames/f_{f+1:05d}.jpg'); return cv2.cvtColor(im,cv2.COLOR_BGR2HSV), im
def mask(hsv, kind):
    h,s,v=hsv[...,0].astype(int),hsv[...,1].astype(int),hsv[...,2].astype(int)
    if kind=='orange': return (h>=6)&(h<=16)&(s>150)&(v>150)
    if kind=='red': return ((h<=4)|(h>=172))&(s>180)&(v>120)
    if kind=='green': return (h>=45)&(h<=75)&(s>150)&(v>150)
def smooth(m): 
    m=(m*255).astype(np.uint8); m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8)); return m>127
out={}
# special page
hsv,_=load(33.0)
o=smooth(mask(hsv,'orange')|((hsv[...,0]>=6)&(hsv[...,0]<=20)&(hsv[...,1]>120)))
pts=[]
for y in range(0,480,12):
    xs=np.where(o[y,:600])[0]; pts.append([int(xs.max()) if len(xs) else 0,y])
pts.append([int(np.where(o[479,:600])[0].max()),480]); out['special_orange_right']=pts
g=smooth(mask(hsv,'green')); pts=[]
for x in range(400,854,14):
    ys=np.where(g[:,x])[0]; pts.append([x,int(ys.min()) if len(ys) else 480])
pts.append([853,int(np.where(g[:,853])[0].min())]); out['special_green_top']=pts
# showroom
hsv,_=load(51.0)
r=smooth(mask(hsv,'red')); o=smooth(mask(hsv,'orange'))
out['showroom_red_right']=[[int(np.where(r[y,:500])[0].max()) if r[y,:500].any() else -1,y] for y in list(range(0,480,12))+[479]]
out['showroom_orange_left']=[[int(np.where(o[y,300:])[0].min())+300 if o[y,300:].any() else 854,y] for y in list(range(0,480,12))+[479]]
# info
hsv,_=load(67.0)
o=smooth(mask(hsv,'orange')); r=smooth(mask(hsv,'red'))
top=[];bot=[]
for x in list(range(0,854,14))+[853]:
    ys=np.where(o[:,x])[0]
    if len(ys): top.append([x,int(ys.min())]); bot.append([x,int(ys.max())])
out['info_band_top']=top; out['info_band_bottom']=bot
out['info_red_left']=[[int(np.where(r[y,:])[0].min()) if r[y,:].any() else 854,y] for y in list(range(300,480,8))+[479]]
json.dump(out,open('analysis/shapes.json','w'))
for k,v in out.items(): print(k, v[:4],'...',v[-3:], len(v))
