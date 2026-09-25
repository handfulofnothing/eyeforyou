import cv2, numpy as np, sys
def dots(t):
    f=int(round(t*30)); im=cv2.imread(f'analysis/frames/f_{f+1:05d}.jpg')
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    # inside hub white ellipse only
    yy,xx=np.mgrid[0:480,0:854]; inside=((xx-427)/529.0)**2+((yy-240)/195.0)**2<0.97
    sat=(hsv[...,1]>90)&(hsv[...,2]>90)&inside
    m=(sat*255).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    out=[]
    for i in range(1,n):
        x,y,w,h,a=st[i]
        if a<120: continue
        comp=(lab==i).astype(np.uint8)
        # distance transform peak = circle(s) inside the component
        dt=cv2.distanceTransform(comp,cv2.DIST_L2,5)
        # iterative peak picking for touching circles
        d=dt.copy()
        for _ in range(8):
            r=d.max()
            if r<6: break
            yx=np.unravel_index(d.argmax(),d.shape)
            b,g,rr=im[yx[0],yx[1]]
            out.append((int(yx[1]),int(yx[0]),round(float(r)+0.5,1),'#%02x%02x%02x'%(rr,g,b)))
            cv2.circle(d,(int(yx[1]),int(yx[0])),int(r*1.6),0,-1)
    return sorted(out,key=lambda p:p[1])
for t in [float(x) for x in sys.argv[1:]]:
    print(f"{t:6.2f}:", ' '.join(f"({x},{y}) r{r} {c}" for x,y,r,c in dots(t)))
