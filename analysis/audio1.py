import librosa, numpy as np, json
y, sr = librosa.load('audio.wav', sr=44100, mono=True)
dur = len(y)/sr
hop=256
rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop)[0]
t = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)
# per-second loudness overview
for s in range(0, int(dur)+1):
    m = rms[(t>=s)&(t<s+1)]
    if len(m): print(f"{s:3d}s  rms={20*np.log10(m.mean()+1e-9):6.1f} dB  peak={20*np.log10(m.max()+1e-9):6.1f}", '#'*int(max(0,(20*np.log10(m.mean()+1e-9)+60))))
