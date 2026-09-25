import librosa, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
y, sr = librosa.load('audio.wav', sr=22050, mono=True)
hop=256
S = librosa.amplitude_to_db(np.abs(librosa.stft(y, n_fft=2048, hop_length=hop)), ref=np.max)
M = librosa.power_to_db(librosa.feature.melspectrogram(y=y, sr=sr, n_fft=2048, hop_length=hop, n_mels=96), ref=np.max)
oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
t = librosa.frames_to_time(np.arange(M.shape[1]), sr=sr, hop_length=hop)
segs=[(0,22),(21,43),(42,64),(63,85)]
fig, axes = plt.subplots(8,1, figsize=(26,22), gridspec_kw={'height_ratios':[3,1]*4})
for i,(a,b) in enumerate(segs):
    m=(t>=a)&(t<b)
    ax=axes[2*i]; ax.imshow(M[:,m], origin='lower', aspect='auto', extent=[a,b,0,96], cmap='magma', vmin=-70, vmax=0)
    ax.set_xticks(np.arange(a,b+0.01,0.5), minor=True); ax.set_xticks(np.arange(a,b+0.01,1)); ax.grid(which='both', color='w', alpha=0.15)
    ax2=axes[2*i+1]; ax2.plot(t[m], oenv[m], lw=0.7); ax2.set_xlim(a,b); ax2.set_xticks(np.arange(a,b+0.01,1)); ax2.grid(alpha=0.3)
plt.tight_layout(); plt.savefig('spectro.png', dpi=60)
