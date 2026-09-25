import librosa, numpy as np, json
from scipy.signal import butter, sosfiltfilt, find_peaks
y, sr = librosa.load('audio.wav', sr=44100, mono=True)
hop=128
oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop, aggregate=np.median)
tempo_g, beats = librosa.beat.beat_track(onset_envelope=oenv, sr=sr, hop_length=hop, units='time')
print('global tempo', tempo_g)
# local tempo over windows
ac_tempo = librosa.feature.tempo(onset_envelope=oenv, sr=sr, hop_length=hop, aggregate=None)
tt = librosa.frames_to_time(np.arange(len(ac_tempo)), sr=sr, hop_length=hop)
for s in range(0,85,3):
    m=ac_tempo[(tt>=s)&(tt<s+3)]
    print(f"{s:3d}s local tempo median {np.median(m):6.1f}")
# kick band
sos = butter(4, [35,130], btype='band', fs=sr, output='sos')
yk = sosfiltfilt(sos, y)
env = librosa.feature.rms(y=yk, frame_length=1024, hop_length=hop)[0]
envt = librosa.frames_to_time(np.arange(len(env)), sr=sr, hop_length=hop)
d = np.maximum(0, np.diff(env, prepend=env[0]))
pk,_ = find_peaks(d, height=np.percentile(d,97), distance=int(0.2*sr/hop))
kt = envt[pk]
print('kick candidates', len(kt))
print(np.round(kt,3).tolist())
json.dump({'beats':list(map(float,beats)),'kicks':list(map(float,kt)),'tempo':float(np.atleast_1d(tempo_g)[0])},open('beats_raw.json','w'))
