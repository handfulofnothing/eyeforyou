import json, numpy as np
d=json.load(open('scene_raw.json'))
diffs=np.array(d['diffs']); means=np.array(d['means'])
fi=diffs[:,0].astype(int); pd=diffs[:,1]
act = pd>0.35
# cluster
iv=[]; start=None; last=None
for f,a in zip(fi,act):
    if a:
        if start is None: start=f
        last=f
    elif start is not None and f-last>4:
        iv.append((start,last)); start=None
if start is not None: iv.append((start,last))
for a,b in iv:
    seg=pd[(fi>=a)&(fi<=b)]
    print(f"frames {a:5d}-{b:5d}  t {a/30:6.2f}-{b/30:6.2f}  dur {(b-a+1)/30:5.2f}s  meanΔ {seg.mean():6.2f} maxΔ {seg.max():6.1f}")
