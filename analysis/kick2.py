import librosa, numpy as np, json
y, sr = librosa.load('audio.wav', sr=44100, mono=True)
hop=128; fr=sr/hop
S=np.abs(librosa.stft(y,n_fft=2048,hop_length=hop))
f=librosa.fft_frequencies(sr=sr,n_fft=2048)
low=S[(f>=35)&(f<=110)].sum(0); mid=S[(f>=150)&(f<=400)].sum(0); hi=S[(f>=5000)&(f<=12000)].sum(0); snr=S[(f>=1500)&(f<=4000)].sum(0)
def fl(x):
    lx=np.log(x+1e-3); d=np.maximum(0,lx[2:]-lx[:-2]); d=np.concatenate([[0,0],d]); return d/np.percentile(d,99.5)
K=fl(low); H=fl(hi); SN=fl(snr)
np.save('K.npy',K); np.save('Hh.npy',H); np.save('SN.npy',SN)
t=np.arange(len(K))/fr
# sections with anchors to test
secs=[(12.6,20.4),(20.6,27.3),(27.5,42.6),(42.8,56.1),(56.3,71.9),(72.1,76.2),(76.4,84.8)]
out=[]
for a,b in secs:
    best=None
    for bpm in np.arange(134.0,136.2,0.02):
        per=60/bpm/4  # 16th grid
        for ph in np.arange(0,per,0.002):
            ts=np.arange(a+((ph-a)%per),b,per)
            idx=np.round(ts*fr).astype(int)
            s=(K[idx]+0.5*H[idx]+0.5*SN[idx]).mean()
            if best is None or s>best[0]: best=(s,bpm,ts[0])
    s,bpm,t0=best
    # bar-gram: 16 slots per bar, start from t0 aligned to 16th; find which 16th offset (0..15) makes kicks land on slot 0
    per16=60/bpm/4
    n=int((b-t0)/per16)
    ts=t0+np.arange(n)*per16; idx=np.round(ts*fr).astype(int)
    kv=np.array([K[max(0,i-2):i+3].max() for i in idx]); hv=np.array([H[max(0,i-2):i+3].max() for i in idx]); sv=np.array([SN[max(0,i-2):i+3].max() for i in idx])
    prof_k=np.array([kv[o::16].mean() for o in range(16)]); prof_s=np.array([sv[o::16].mean() for o in range(16)])
    print(f"\nSEC {a}-{b}: bpm {bpm:.2f} first16th {t0:.3f} score {s:.3f}")
    print(' kick prof  ', ' '.join(f"{v:.2f}" for v in prof_k))
    print(' snare prof ', ' '.join(f"{v:.2f}" for v in prof_s))
    out.append(dict(a=a,b=b,bpm=float(bpm),t0=float(t0),pk=prof_k.tolist(),ps=prof_s.tolist()))
json.dump(out,open('sections_fit.json','w'),indent=1)
