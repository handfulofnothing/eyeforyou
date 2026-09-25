import librosa, numpy as np, json
from scipy.signal import butter, sosfiltfilt
y, sr = librosa.load('audio.wav', sr=44100, mono=True)
hop=64; fr=sr/hop
sos = butter(4, [40,150], btype='band', fs=sr, output='sos')
yk = sosfiltfilt(sos, y)
env = np.sqrt(np.convolve(yk**2, np.ones(512)/512, mode='same'))[::hop]
flux = np.maximum(0, np.diff(np.log(env+1e-6), prepend=0))
flux = np.convolve(flux, np.hanning(9)/np.hanning(9).sum(), mode='same')
# broadband onset too
ob = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
ob = ob/ob.max(); flux=flux/flux.max()
tt = np.arange(len(flux))/fr
def score(sig, bpm, phase, a, b):
    per=60/bpm; ts=np.arange(phase, b, per); ts=ts[ts>=a]
    idx=(ts*fr).astype(int); idx=idx[idx<len(sig)]
    return sig[idx].mean()
best=None
for bpm in np.arange(130,140,0.01):
    per=60/bpm
    for ph in np.arange(0, per, 0.002):
        s=score(flux,bpm,ph,13,84)
        if best is None or s>best[0]: best=(s,bpm,ph)
print('best global', best)
s,bpm,ph=best
# windowed phase check
per=60/bpm
for a in range(13,84,6):
    bs=None
    for p in np.arange(0,per,0.002):
        sc=score(flux,bpm,p,a,a+6)
        if bs is None or sc>bs[0]: bs=(sc,p)
    off=((bs[1]-ph+per/2)%per)-per/2
    print(f"win {a:2d}-{a+6:2d}: phase {bs[1]:.3f} offset vs global {off*1000:+6.1f} ms score {bs[0]:.3f}")
json.dump({'bpm':bpm,'phase':ph},open('grid_fit.json','w'))
np.save('kflux.npy', flux); np.save('bflux.npy', ob)
