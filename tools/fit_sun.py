import numpy as np, cv2, json
from scipy.optimize import minimize
DS=4; H,W=120,214
ys,xs=np.mgrid[0:H,0:W]; X=(xs*DS+2.0); Y=(ys*DS+2.0)
def classes(t):
    f=int(round(t*30)); im=cv2.imread(f'analysis/frames/f_{f+1:05d}.jpg'); im=cv2.resize(im,(W,H),interpolation=cv2.INTER_AREA).astype(int)
    b,g,r=im[...,0],im[...,1],im[...,2]
    out=np.full((H,W),2)             # red
    out[(r>200)&(g>55)&(g<150)&(b<70)]=1   # orange
    out[(r>200)&(g>200)&(b>200)]=0         # white
    return out
HW=6.5
def model(p):
    cx,cy,rw,ro,lL=p; L=np.exp(lL)
    ang=np.degrees(np.arctan2(Y-cy,X-cx)); dist=np.hypot(X-cx,Y-cy)
    out=np.full((H,W),2)
    dO=np.abs(((ang-ro)+36)%72-36); out[(dO<HW)&(dist<L)]=1
    dW=np.abs(((ang-rw)+36)%72-36); out[(dW<HW)&(dist<L)]=0
    return out
def loss(p,cls): return np.mean(model(p)!=cls)
times=[round(17.1+k/30,4) for k in range(0,90)]
res=[]; prev=np.array([472,165,-20.0,40.0,np.log(60)])
for t in times:
    cls=classes(t)
    if (cls==0).mean()>0.97: print(t,'white'); continue
    cands=[prev]; rs=np.random.RandomState(int(t*1000))
    for _ in range(16): cands.append(prev+np.array([rs.uniform(-80,80),rs.uniform(-80,80),rs.uniform(-36,36),rs.uniform(-36,36),rs.uniform(-0.3,1.2)]))
    best=None
    for x0 in cands:
        r=minimize(loss,x0,args=(cls,),method='Nelder-Mead',options={'maxiter':1200,'xatol':0.2,'fatol':1e-5})
        if best is None or r.fun<best.fun: best=r
    p=best.x.copy(); p[2]=p[2]%72; p[3]=p[3]%72
    prev=best.x
    res.append([t]+[float(v) for v in p]+[float(best.fun)])
    print(f"{t:7.3f} c=({p[0]:7.1f},{p[1]:7.1f}) rotW {p[2]:6.1f} rotO {p[3]:6.1f} L {np.exp(p[4]):8.1f} err {best.fun:.3f}")
json.dump(res,open('analysis/fit_sun.json','w'))
