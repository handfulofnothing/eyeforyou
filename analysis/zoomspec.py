import librosa, numpy as np, matplotlib, sys
matplotlib.use('Agg'); import matplotlib.pyplot as plt
y, sr = librosa.load('audio.wav', sr=22050, mono=True)
wins=[(13.0,17.0),(33.0,37.0),(50.0,54.0),(66.0,70.0)]
fig,axes=plt.subplots(len(wins),1,figsize=(26,16))
for ax,(a,b) in zip(axes,wins):
    seg=y[int(a*sr):int(b*sr)]
    S=librosa.amplitude_to_db(np.abs(librosa.stft(seg,n_fft=1024,hop_length=64)),ref=np.max)
    f=librosa.fft_frequencies(sr=sr,n_fft=1024)
    # log-ish freq display: take up to 8k
    ax.imshow(S[:372], origin='lower', aspect='auto', extent=[a,b,0,f[371]], cmap='magma', vmin=-75, vmax=0)
    ax.set_yscale('symlog', linthresh=200)
    ax.set_ylim(30,8000)
    ax.set_xticks(np.arange(a,b+0.001,0.1),minor=True); ax.set_xticks(np.arange(a,b+0.001,0.5)); ax.grid(which='major',color='w',alpha=0.4); ax.grid(which='minor',color='w',alpha=0.1)
plt.tight_layout(); plt.savefig('zoomspec.png',dpi=55)
