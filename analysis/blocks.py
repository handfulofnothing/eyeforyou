import numpy as np, json, librosa
kt,kv=np.load('lowhits.npy')
# intro onsets (no low hits) -> use broadband onset peaks
y, sr = librosa.load('audio.wav', sr=22050, mono=True)
hop=64
o=librosa.onset.onset_strength(y=y,sr=sr,hop_length=hop); to=np.arange(len(o))*hop/sr
from scipy.signal import find_peaks
pk,_=find_peaks(o,distance=int(0.1*sr/hop),prominence=np.percentile(o,90)*0.5)
it=to[pk]; iv=o[pk]/np.percentile(o,99)
blocks=[('I','intro (pad + arp)',0.0,12.90),('A','drums in: logo zoom → welcome',12.90,22.60),('H1','hub build',22.60,29.00),
        ('S','special + hub return',29.00,44.53),('R','showroom',44.53,56.23),('E','showroom → hub',56.23,63.20),('F','info&contact → hub',63.20,84.87)]
out=[]
for key,name,a,b in blocks:
    if key=='I': ts,ws=it[(it>a+0.3)&(it<b-0.1)],iv[(it>a+0.3)&(it<b-0.1)]
    else:
        m=(kt>a+0.25)&(kt<b-0.05); ts,ws=kt[m],kv[m]
    best=None
    for bpm in np.arange(134.6,135.61,0.01):
        p8=60/bpm/2
        for ph in np.arange(0,p8,0.001):
            r=((ts-ph+p8/2)%p8)-p8/2
            s=np.sum(ws*np.exp(-(r/0.012)**2/2)) - 0.0*abs(bpm-135.09)
            if best is None or s>best[0]: best=(s,bpm,ph)
    s,bpm,ph=best; p8=60/bpm/2; beat=2*p8
    r=((ts-ph+p8/2)%p8)-p8/2; on=np.abs(r)<0.04
    # anchor: 8th grid point nearest block start; downbeat = that point
    n=round((a-ph)/p8); anchor=ph+n*p8
    if key=='I': anchor=a  # audio start
    out.append(dict(key=key,name=name,start=a,end=b,bpm=round(float(bpm),2),anchor=round(float(anchor),4),
        hits=int(len(ts)),on_grid=int(on.sum()),med_res_ms=round(float(np.median(np.abs(r[on]))*1000),1) if on.sum() else None))
    print(f"{key:3s} {a:6.2f}-{b:6.2f} bpm {bpm:7.2f} anchor(bar1) {anchor:7.3f} (visual {a:6.2f}, Δ {1000*(anchor-a):+5.0f}ms) hits {len(ts):3d} on-grid {on.sum():3d} med|res| {np.median(np.abs(r[on]))*1000 if on.sum() else 0:4.1f}ms")
json.dump(out,open('blocks.json','w'),indent=1)
