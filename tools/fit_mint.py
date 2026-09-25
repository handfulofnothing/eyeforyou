import numpy as np, cv2, json
from scipy.optimize import minimize
DS=4; H,W=120,214
ys,xs=np.mgrid[0:H,0:W]; X=(xs*DS+2.0); Y=(ys*DS+2.0)
def classes(t):
    f=int(round(t*30)); im=cv2.imread(f'analysis/frames/f_{f+1:05d}.jpg'); im=cv2.resize(im,(W,H),interpolation=cv2.INTER_AREA)
    h,s,v=[c.astype(int) for c in cv2.split(cv2.cvtColor(im,cv2.COLOR_BGR2HSV))]
    out=np.zeros((H,W),int)
    out[(h>=65)&(h<=90)&(s>120)&(v>150)]=1          # mint
    out[(s<45)&(v>200)]=2                            # white
    out[(h>=5)&(h<=20)&(s>150)&(v>150)]=3            # orange
    out[((h<=4)|(h>=170))&(s>150)&(v>90)]=4          # red
    return out
NOTCH=np.array([[-16,-40],[-7,-40],[-9,-24],[-14,-24]])
def inpoly(px,py,P):
    ins=np.zeros(px.shape,bool)
    for i in range(len(P)):
        x1,y1=P[i]; x2,y2=P[(i+1)%len(P)]
        ins^=((y1>py)!=(y2>py))&(px<(x2-x1)*(py-y1)/(y2-y1+1e-12)+x1)
    return ins
def model(p):
    dx,dy,lR,ex,ey,les,eth=p; R=np.exp(lR); es=np.exp(les)
    out=np.zeros((H,W),int)
    r=np.hypot(X-dx,Y-dy)
    out[r<R]=3; out[r<0.898*R]=2; out[r<0.795*R]=1
    c,sn=np.cos(np.radians(eth)),np.sin(np.radians(eth))
    ddx,ddy=X-ex,Y-ey; lx=(c*ddx+sn*ddy)/es; ly=(-sn*ddx+c*ddy)/es
    outer=(lx/100)**2+(ly/38)**2<1
    out[outer]=3; out[outer&((lx/66)**2+(ly/22)**2<1)]=2; out[outer&(lx**2+ly**2<37**2)]=4
    out[outer&inpoly(lx,ly,NOTCH)]=1
    return out
def loss(p,cls): return np.mean(model(p)!=cls)
init={15.45:[267,45,np.log(44),276,61,np.log(0.03),-40],15.55:[281,64,np.log(281),437,179,np.log(0.09),-45],15.7:[150,-300,np.log(1100),600,297,np.log(0.22),-45],
      16.1:[-300,-800,np.log(1700),697,330,np.log(0.78),-38],16.4:[-380,-760,np.log(1760),521,341,np.log(1.1),-23]}
times=[round(15.4+k/30,4) for k in range(0,51)]
res=[]; prev=None
for t in times:
    cls=classes(t)
    cands=[]
    if prev is not None: cands.append(prev)
    k=min(init,key=lambda a:abs(a-t)); cands.append(np.array(init[k],float))
    rs=np.random.RandomState(int(t*1000))
    base=cands[0]
    for _ in range(10): cands.append(base+np.array([rs.uniform(-60,60),rs.uniform(-60,60),rs.uniform(-0.3,0.3),rs.uniform(-60,60),rs.uniform(-60,60),rs.uniform(-0.4,0.4),rs.uniform(-15,15)]))
    best=None
    for x0 in cands:
        r=minimize(loss,x0,args=(cls,),method='Nelder-Mead',options={'maxiter':1500,'xatol':0.3,'fatol':1e-5})
        if best is None or r.fun<best.fun: best=r
    prev=best.x; p=best.x
    res.append([t]+[float(v) for v in p]+[float(best.fun)])
    print(f"{t:7.3f} disc ({p[0]:7.1f},{p[1]:7.1f}) R {np.exp(p[2]):7.1f} | eye ({p[3]:7.1f},{p[4]:7.1f}) s {np.exp(p[5]):6.3f} th {p[6]:6.1f} | err {best.fun:.3f}")
json.dump(res,open('analysis/fit_mint.json','w'))
