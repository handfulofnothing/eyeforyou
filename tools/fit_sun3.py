import numpy as np, cv2, json
from scipy.optimize import minimize
exec(open('tools/fit_sun.py').read().split("times=")[0])   # reuse classes/model/loss
# early ray length: farthest white/orange pixel from the centre
for t,(cx,cy) in [(17.1,(475,160)),(17.133,(472,165)),(17.167,(470,166)),(17.2,(468,167)),(17.233,(467,168)),(17.3,(462,171)),(17.367,(460,173)),(17.433,(457,175))]:
    f=int(round(t*30)); im=cv2.imread(f'analysis/frames/f_{f+1:05d}.jpg').astype(int); b,g,r=im[...,0],im[...,1],im[...,2]
    m=((r>200)&(g>200)&(b>200))|((r>200)&(g>55)&(g<150)&(b<70))
    yy,xx=np.nonzero(m[:, :]); d=np.hypot(xx-cx,yy-cy); d=d[(xx>5)&(xx<848)&(yy<470)]
    print('L',t, round(np.percentile(d,99.5),1) if len(d) else 0)
# tail fit 19.1 -> 20.0 seeded from polar result
pol=json.load(open('analysis/fit_sun_polar.json'))
prev=np.array([436,315,116.2,-41.0,np.log(5000)])
out=[]
for k in range(0,29):
    t=round(19.1+k/30,4); cls=classes(t)
    if (cls==0).mean()>0.985: out.append([t,None]); print(t,'white'); continue
    rs=np.random.RandomState(k); cands=[prev]
    for _ in range(40): cands.append(prev+np.array([rs.uniform(-150,150),rs.uniform(-150,250),rs.uniform(-12,12),rs.uniform(-12,12),0]))
    best=None
    for x0 in cands:
        r=minimize(lambda p:loss(p,cls),x0,method='Nelder-Mead',options={'maxiter':900,'xatol':0.2,'fatol':1e-5})
        if best is None or r.fun<best.fun: best=r
    prev=best.x; p=best.x
    out.append([t]+[float(v) for v in p]+[float(best.fun)])
    print(f"{t:7.3f} c=({p[0]:8.1f},{p[1]:8.1f}) rotW {p[2]:7.1f} rotO {p[3]:7.1f} err {best.fun:.3f}")
json.dump(out,open('analysis/fit_sun_tail.json','w'))
