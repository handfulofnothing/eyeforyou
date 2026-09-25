"""Frame-by-frame smoothness meter for a rendered video.
For each frame: dense optical flow (Farneback) vs the previous frame at 320x180.
jerk[i] = |v[i] - (v[i-1] + v[i+1]) / 2| per pixel (median over moving pixels), in 1080p px/frame.
Smooth motion -> jerk ~ 0; stutter / jumps -> spikes. Hard cuts are excluded."""
import sys, subprocess, numpy as np, cv2, json
path = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else None
t0 = float(sys.argv[3]) if len(sys.argv) > 3 else 0; t1 = float(sys.argv[4]) if len(sys.argv) > 4 else 1e9
W, H = 320, 180
cmd = ['ffmpeg', '-v', 'error', '-ss', str(t0), '-i', path] + (['-t', str(t1 - t0)] if t1 < 1e8 else []) + ['-vf', f'scale={W}:{H},format=gray', '-f', 'rawvideo', '-']
raw = subprocess.run(cmd, capture_output=True).stdout
F = np.frombuffer(raw, np.uint8).reshape(-1, H, W)
flows = [None]
for i in range(1, len(F)):
    flows.append(cv2.calcOpticalFlowFarneback(F[i - 1], F[i], None, 0.5, 4, 21, 5, 7, 1.5, 0))
diff = np.array([0] + [np.abs(F[i].astype(np.int16) - F[i - 1]).mean() for i in range(1, len(F))])
scale = 1920 / W
res = []
for i in range(2, len(F) - 1):
    if diff[i] > 40 or diff[i + 1] > 40 or diff[i - 1] > 40:  # hard cut nearby
        res.append((i, 0.0, 0.0)); continue
    a, b, c = flows[i - 1], flows[i], flows[i + 1]
    mov = (np.linalg.norm(b, axis=2) > 0.15)
    if mov.mean() < 0.01: res.append((i, 0.0, 0.0)); continue
    j = np.linalg.norm(b - (a + c) / 2, axis=2)[mov]
    v = np.linalg.norm(b, axis=2)[mov]
    res.append((i, float(np.median(j)) * scale, float(np.median(v)) * scale))
fps = 60
J = np.array([r[1] for r in res]); V = np.array([r[2] for r in res])
print(f'frames {len(F)}  mean jerk {J.mean():.2f}px  p95 {np.percentile(J,95):.2f}px  frames with jerk>2px: {(J>2).sum()}  >5px: {(J>5).sum()}')
bad = sorted(res, key=lambda r: -r[1])[:25]
print('worst frames (t, jerk px, speed px/frame):')
for i, j, v in sorted(bad): print(f'  {t0 + i / fps:7.3f}s  jerk {j:6.2f}  speed {v:6.2f}')
if out: json.dump([[t0 + i / fps, j, v] for i, j, v in res], open(out, 'w'))
