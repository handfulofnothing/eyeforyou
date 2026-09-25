import librosa, numpy as np, json
y, sr = librosa.load('audio.wav', sr=44100, mono=True)
H,P = librosa.effects.hpss(y, margin=(1.0,3.0))
hop=64; fr=sr/hop
op = librosa.onset.onset_strength(y=P, sr=sr, hop_length=hop, n_mels=64, fmax=8000, lag=2, max_size=3)
op=op/np.percentile(op,99.5)
np.save('pflux.npy',op)
import soundfile as sf; sf.write('perc.wav',P,sr); sf.write('harm.wav',H,sr)
# tempogram global
tg = librosa.feature.tempo(onset_envelope=op, sr=sr, hop_length=hop, start_bpm=135, max_tempo=200)
print('tempo percussive', tg)
def score(bpm, ph, a, b):
    per=60/bpm; ts=np.arange(ph%per, b, per); ts=ts[ts>=a]
    idx=np.round(ts*fr).astype(int); idx=idx[idx<len(op)]
    # max within +-5ms
    return np.mean([op[max(0,i-3):i+4].max() for i in idx])
# fine BPM on whole 13-85 via 8th-note grid (half beat)
best=None
for bpm in np.arange(133.5,136.5,0.01):
    per=60/bpm/2
    for ph in np.arange(0,per,0.002):
        s=score(bpm*2,ph,13,84.5)
        if best is None or s>best[0]: best=(s,bpm,ph)
print('best 8th grid', best)
bpm=best[1]; per=60/bpm/2
res=[]
for a in np.arange(12,83,1.0):
    bs=max(((score(bpm*2,p,a,a+3),p) for p in np.arange(0,per,0.002)))
    off=((bs[1]-best[2]+per/2)%per)-per/2
    res.append((a,off*1000,bs[0]))
    print(f"{a:5.1f}-{a+3:5.1f}: phase off {off*1000:+6.1f} ms  score {bs[0]:.3f}")
json.dump({'bpm':bpm,'phase8':best[2]},open('grid_fit2.json','w'))
