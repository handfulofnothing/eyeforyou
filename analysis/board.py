import numpy as np, json, librosa
# ---- piecewise grid (measured) ----
B=[('I',None,None),('A',12.871,135.03),('H1',22.598,134.96),('S',28.942,135.18),('R',44.540,135.63),('E',56.271,135.13),('F',63.134,135.10)]
ends={'A':22.598,'H1':28.942,'S':44.540,'R':56.271,'E':63.134,'F':84.867}
def blk(t):
    if t<12.871-0.05: return 'I'
    cur='A'
    for k,a,b in B[1:]:
        if t>=a-0.12: cur=k
    return cur
def grid(k):
    if k=='I': return 12.871,135.03
    for kk,a,b in B:
        if kk==k: return a,b
# global bar numbering
bar_starts=[]  # (global_bar, block, t, len)
a,bpm=12.871,135.03; L=240/bpm
g=-8
t=a-8*L
while t<a-1e-6: bar_starts.append((g,'I',t,L)); t+=L; g+=1
g=1
for k,a,bpm in B[1:]:
    L=240/bpm; t=a
    while t<ends[k]-1e-6:
        bar_starts.append((g,k,t,min(L,ends[k]-t))); t+=L; g+=1
def pos(t,k):
    a,bpm=grid(k); beat=60/bpm
    # find global bar
    cands=[b for b in bar_starts if b[1]==k and b[2]<=t+1e-6] if k!='I' else [b for b in bar_starts if b[1]=='I' and b[2]<=t+1e-6]
    if not cands: cands=[bar_starts[0]]
    gb,_,t0,_=cands[-1]
    bt=(t-t0)/beat
    return gb, bt
def snap(t,k,rule):
    a,bpm=grid(k); beat=60/bpm; bar=4*beat
    if rule=='anchor': return a
    if rule=='down': n=round((t-a)/bar); return a+n*bar
    if rule=='down+': n=np.ceil((t-a)/bar-0.02); return a+n*bar
    if rule=='beat': n=round((t-a)/beat); return a+n*beat
    if rule=='8th': n=round((t-a)/(beat/2)); return a+n*beat/2
    return t
EV=json.load(open('events_in.json'))
out=[]
for e in EV:
    k=e.get('block') or blk(e['t'])
    tt=snap(e['t'],k,e['rule']) if e['rule']!='keep' else e['t']
    if 'force' in e:
        a,bpm=grid(k); beat=60/bpm; tt=a+e['force']*beat
    if 'abs' in e: tt=e['abs']
    gb,bt=pos(tt,k)
    beat_i=int(np.floor(bt+1e-6)); frac=bt-beat_i
    sub='' if abs(frac)<0.02 else ('.&' if abs(frac-0.5)<0.02 else f'+{frac:.2f}')
    out.append(dict(e, block=k, target=round(float(tt),3), delta_ms=int(round((tt-e['t'])*1000)), bar=int(gb), beat=beat_i+1, sub=sub, frame60=int(round(tt*60))))
json.dump(out,open('events_out.json','w'),indent=1)
# energy per bar
y,sr=librosa.load('audio.wav',sr=22050,mono=True)
eb=[]
for gb,k,t0,Lb in bar_starts:
    s0=max(0,int(t0*sr)); s1=int(min(84.867,t0+Lb)*sr)
    seg=y[s0:s1]
    if len(seg)<100: continue
    rms=np.sqrt(np.mean(seg**2)); eb.append(dict(bar=gb,block=k,t=round(max(0,t0),3),len=round(Lb,3),db=round(float(20*np.log10(rms+1e-9)),1)))
from scipy.signal import butter, sosfiltfilt
yl=sosfiltfilt(butter(4,[40,150],btype='band',fs=sr,output='sos'),y)
kt=np.load('lowhits.npy')[0]
for b in eb:
    s0=int(b['t']*sr); s1=int(min(84.867,b['t']+b['len'])*sr)
    b['low_db']=round(float(20*np.log10(np.sqrt(np.mean(yl[s0:s1]**2))+1e-9)),1)
    b['hits_per_beat']=round(float(((kt>=b['t'])&(kt<b['t']+b['len'])).sum()/(b['len']/ (240/135.09)*4)),2)
json.dump(dict(bars=eb),open('bars.json','w'),indent=1)
for e in out: print(f"{e['id']:4s} {e['rule']:6s} {e['t']:7.3f} -> {e['target']:7.3f} ({e['delta_ms']:+5d}ms)  {e['block']:2s} bar {e['bar']:3d}.{e['beat']}{e['sub']:5s} {e['what'][:70]}")
print()
print(' '.join(f"{b['bar']}:{b['db']}" for b in eb))
