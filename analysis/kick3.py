import librosa, numpy as np, json
from scipy.signal import butter, sosfiltfilt, find_peaks, correlate
y, sr = librosa.load('audio.wav', sr=22050, mono=True)
sos=butter(4,400,btype='low',fs=sr,output='sos'); yl=sosfiltfilt(sos,y)
# locate kick near 33.4 via low-band flux
S=np.abs(librosa.stft(yl,n_fft=512,hop_length=32)); f=librosa.fft_frequencies(sr=sr,n_fft=512)
band=S[(f>=120)&(f<=350)].sum(0); lb=np.log(band+1e-4); d=np.maximum(0,np.diff(lb,prepend=lb[0]))
t=np.arange(len(d))*32/sr
for c in [33.4,35.2,16.0,51.2]:
    m=(t>c-0.2)&(t<c+0.2); i=np.argmax(d*m); print('onset near',c,'->',round(t[i],4))
c0=t[np.argmax(d*((t>33.2)&(t<33.6)))]
s0=int((c0-0.005)*sr); tpl=yl[s0:s0+int(0.09*sr)]
tpl=(tpl-tpl.mean())/np.linalg.norm(tpl)
# normalized xcorr
L=len(tpl)
xc=correlate(yl,tpl,mode='valid')
e=np.sqrt(np.convolve(yl**2,np.ones(L),mode='valid'))+1e-9
ncc=xc/e
tt=(np.arange(len(ncc))+int(0.005*sr))/sr
pk,pr=find_peaks(ncc,height=0.55,distance=int(0.2*sr))
kt=tt[pk]; kv=ncc[pk]
print('kicks found',len(kt))
np.save('kick_times.npy',np.stack([kt,kv]))
for a in range(0,85,5):
    m=(kt>=a)&(kt<a+5)
    print(f"{a:2d}-{a+5:2d}:", ' '.join(f"{x:.3f}({v:.2f})" for x,v in zip(kt[m],kv[m])))
