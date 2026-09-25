import librosa, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.signal import find_peaks
y, sr = librosa.load('audio.wav', sr=22050, mono=True)
hop=64; nfft=1024
S=np.abs(librosa.stft(y,n_fft=nfft,hop_length=hop)); f=librosa.fft_frequencies(sr=sr,n_fft=nfft)
band=(f>=40)&(f<=500)
L=np.log1p(100*S[band])
flux=np.maximum(0,L[:,3:]-L[:,:-3]).sum(0); flux=np.concatenate([[0,0,0],flux])
flux=np.convolve(flux,np.hanning(7)/np.hanning(7).sum(),mode='same')
# adaptive threshold
med=np.array([np.median(flux[max(0,i-400):i+400]) for i in range(0,len(flux),50)]); med=np.interp(np.arange(len(flux)),np.arange(0,len(flux),50),med)
nf=flux/(med+1e-6)
t=np.arange(len(flux))*hop/sr
pk,pp=find_peaks(nf,height=2.2,distance=int(0.12*sr/hop),prominence=1.0)
kt=t[pk]; kv=nf[pk]
np.save('lowflux.npy',np.stack([t,nf])); np.save('lowhits.npy',np.stack([kt,kv]))
wins=[(13.0,17.0),(33.0,37.0),(50.0,54.0),(66.0,70.0)]
fig,axes=plt.subplots(len(wins)*2,1,figsize=(26,20),gridspec_kw={'height_ratios':[3,1]*4})
for i,(a,b) in enumerate(wins):
    m=(t>=a)&(t<b)
    ax=axes[2*i]; ax.imshow(librosa.amplitude_to_db(S[:47,m],ref=np.max), origin='lower',aspect='auto',extent=[a,b,0,f[46]],cmap='magma',vmin=-70,vmax=0)
    for x in kt[(kt>=a)&(kt<b)]: ax.axvline(x,color='c',lw=0.8,alpha=0.8)
    ax.set_xticks(np.arange(a,b+0.001,0.1),minor=True)
    ax2=axes[2*i+1]; ax2.plot(t[m],nf[m],lw=0.7); ax2.set_xlim(a,b)
plt.tight_layout(); plt.savefig('kick4.png',dpi=55)
for a in range(0,85,5):
    m=(kt>=a)&(kt<a+5)
    print(f"{a:2d}-{a+5:2d}:", ' '.join(f"{x:.3f}({v:.1f})" for x,v in zip(kt[m],kv[m])))
