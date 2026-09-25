import numpy as np, json
kt,kv=np.load('lowhits.npy')
m=kt>12.5; kt=kt[m]; kv=kv[m]
def fit(ts,ws,bpms=np.arange(133.5,137.0,0.01)):
    best=None
    for bpm in bpms:
        p8=60/bpm/2
        ph=np.angle(np.sum(ws*np.exp(2j*np.pi*ts/p8)))  # circular mean phase for 8th grid
        off=(ph/(2*np.pi))*p8
        r=((ts-off+p8/2)%p8)-p8/2
        s=np.sum(ws*np.exp(-(r/0.012)**2/2))
        if best is None or s>best[0]: best=(s,bpm,off%p8)
    return best
s,bpm,off=fit(kt,kv)
print('global 8th-grid fit bpm',round(bpm,3),'offset',round(off,4))
p8=60/bpm/2
r=((kt-off+p8/2)%p8)-p8/2
for t_,r_,v in zip(kt,r,kv):
    print(f"{t_:7.3f} resid {r_*1000:+6.1f}ms  {'#'*int(v)}")
