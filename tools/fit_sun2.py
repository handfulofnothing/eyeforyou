import cv2, numpy as np, json
def load(t):
    f=int(round(t*30)); return cv2.imread(f'analysis/frames/f_{f+1:05d}.jpg').astype(int)
def cls_map(im):
    b,g,r=im[...,0],im[...,1],im[...,2]
    out=np.full(im.shape[:2],2); out[(r>200)&(g>55)&(g<150)&(b<70)]=1; out[(r>200)&(g>200)&(b>200)]=0; return out
def ring(cm,cx,cy,r,angs):
    xs=np.round(cx+r*np.cos(np.radians(angs))).astype(int); ys=np.round(cy+r*np.sin(np.radians(angs))).astype(int)
    ok=(xs>=0)&(ys>=0)&(xs<854)&(ys<480); v=np.full(len(angs),-1); v[ok]=cm[ys[ok],xs[ok]]; return v
angs=np.arange(0,360,0.5)
def centre(cm,guess,span=36,step=3):
    best=None
    for dx in range(-span,span+1,step):
        for dy in range(-span,span+1,step):
            a=ring(cm,guess[0]+dx,guess[1]+dy,60,angs); b=ring(cm,guess[0]+dx,guess[1]+dy,140,angs)
            ok=(a>=0)&(b>=0)
            if ok.sum()<200: continue
            sc=np.mean(a[ok]==b[ok])
            if best is None or sc>best[0]: best=(sc,guess[0]+dx,guess[1]+dy)
    return best
def rot_of(v,cls):
    m=(v==cls)
    if m.sum()==0: return None
    th=np.radians((angs[m]%72)*5)   # 5-fold symmetry -> circular mean
    return (np.degrees(np.arctan2(np.sin(th).mean(),np.cos(th).mean()))/5)%72
res=[]; g=(438,182)
guesses={17.25:(462,170),17.6:(438,182),18.3:(239,251),19.0:(453,270)}
for k in range(0,64):
    t=round(17.233+k/30,4)
    cm=cls_map(load(t))
    near=min(guesses,key=lambda a:abs(a-t))
    cands=[centre(cm,g,24,3),centre(cm,guesses[near],40,4)]
    best=max([c for c in cands if c],key=lambda c:c[0])
    sc,cx,cy=best; best2=centre(cm,(cx,cy),3,1); sc,cx,cy=best2
    v=ring(cm,cx,cy,100,angs)
    rw=rot_of(v,0); ro=rot_of(v,1)
    g=(cx,cy)
    res.append([t,cx,cy,rw,ro,sc]); print(f"{t:7.3f} c=({cx},{cy}) agree {sc:.2f} rotW {rw} rotO {ro}")
json.dump(res,open('analysis/fit_sun_polar.json','w'))
