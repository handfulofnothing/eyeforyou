"""Track the flower (red gerbera on a cyan 4-point star, on black) in every source frame."""
import cv2, numpy as np, json
sr = json.load(open('analysis/scene_raw.json')); PD = {int(f): p for f, p, h in sr['diffs']}
rows = []
for f in range(int(14.40 * 30), int(15.45 * 30) + 1):
    im = cv2.imread(f'analysis/frames/f_{f+1:05d}.jpg'); hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(int)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    dark = v < 40
    if dark[:300].mean() < 0.45: continue                # not the black flower scene (orange strip may linger at the bottom)
    cyan = (h >= 80) & (h <= 100) & (s > 120) & (v > 120)
    red = (((h <= 12) | (h >= 170)) & (s > 120) & (v > 90))
    m = (cyan | red).astype(np.uint8)
    m[440:, 660:] = 0                                    # ignore the "skip" link
    m[300:, :] = 0                                       # the flower never goes below y=300; the orange strip does
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n < 2: continue
    i = 1 + np.argmax(st[1:, 4])
    ys, xs = np.nonzero(lab == i)
    cx, cy = xs.mean(), ys.mean()
    # star tip radius = 97th percentile distance of cyan pixels; tip angle from 4-fold circular mean
    cm = cyan & (lab == i)
    cyx, cxx = np.nonzero(cm)
    if len(cxx) < 5: continue
    d = np.hypot(cxx - cx, cyx - cy); R = np.percentile(d, 97)
    far = d > 0.6 * R
    ang = np.arctan2(cyx[far] - cy, cxx[far] - cx)
    rot = np.degrees(np.angle(np.mean(np.exp(4j * ang))) / 4)   # 4-fold symmetric tip direction
    rows.append([round(f / 30, 4), round(float(cx), 2), round(float(cy), 2), round(float(R), 2), round(float(rot), 2), int(PD.get(f, 99) > 0.3)])
    print(f"{f/30:7.3f} new={rows[-1][5]}  centre ({cx:6.1f},{cy:6.1f})  tipR {R:6.1f}  tipAngle {rot:7.2f}")
json.dump(rows, open('analysis/flower_track.json', 'w'))
