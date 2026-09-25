import numpy as np, cv2, json
from scipy.optimize import minimize
DS=4
H,W=480//DS,856//DS
ys,xs=np.mgrid[0:H,0:W]; X=(xs*DS+DS/2).astype(np.float64); Y=(ys*DS+DS/2).astype(np.float64)
def classes(t):
    f=int(round(t*30)); im=cv2.imread(f'analysis/frames/f_{f+1:05d}.jpg'); im=cv2.resize(im,(W,H),interpolation=cv2.INTER_AREA)
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV).astype(int)
    orange=(hsv[...,0]>=5)&(hsv[...,0]<=20)&(hsv[...,1]>140)&(hsv[...,2]>140)
    black=hsv[...,2]<70
    return np.where(orange,1,np.where(black,2,0))
NOTCH=np.array([[-8.6,-14],[-2.6,-14],[-4.3,-7.2],[-5.9,-7.2]])
def inpoly(px,py,P):
    ins=np.zeros(px.shape,bool); n=len(P)
    for i in range(n):
        x1,y1=P[i]; x2,y2=P[(i+1)%n]
        c=((y1>py)!=(y2>py))&(px<(x2-x1)*(py-y1)/(y2-y1+1e-12)+x1)
        ins^=c
    return ins
def model(p):
    cx,cy,ls,th=p; s=np.exp(ls); c,sn=np.cos(np.radians(th)),np.sin(np.radians(th))
    dx,dy=X-cx,Y-cy; lx=(c*dx+sn*dy)/s; ly=(-sn*dx+c*dy)/s
    ring=(lx/36)**2+(ly/12.5)**2<1; pup=((lx+0.5)/24.6)**2+(ly/8.5)**2<1; notch=inpoly(lx,ly,NOTCH)
    out=np.zeros(X.shape,int); out[ring&~notch]=1; out[pup]=2
    return out
def loss(p,cls): return np.mean(model(p)!=cls)
times=[round(12.9+k/30,4) for k in range(0,50)]
res=[]; prev=np.array([496,205,0.0,0.0])
for t in times:
    cls=classes(t)
    best=None
    inits=[prev]+[prev+np.array([np.random.uniform(-150,150),np.random.uniform(-150,150),np.random.uniform(0,0.8),np.random.uniform(-40,40)]) for _ in range(14)]
    for x0 in inits:
        r=minimize(loss,x0,args=(cls,),method='Nelder-Mead',options={'xatol':0.5,'fatol':1e-4,'maxiter':600,'initial_simplex':None})
        if best is None or r.fun<best.fun: best=r
    prev=best.x; res.append([t,*[float(v) for v in best.x],float(best.fun)])
    print(f"{t:7.3f} cx {best.x[0]:8.1f} cy {best.x[1]:8.1f} s {np.exp(best.x[2]):7.2f} th {best.x[3]:7.1f}  err {best.fun:.3f}")
json.dump(res,open('analysis/fit_drop.json','w'))
