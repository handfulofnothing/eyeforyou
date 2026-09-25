"""Measure the mint-scene eye in every source frame by fitting an ellipse to its outer ring."""
import cv2, numpy as np, json
sr = json.load(open('analysis/scene_raw.json')); PD = {int(f): p for f, p, h in sr['diffs']}
rows = []
for f in range(int(15.40 * 30), int(17.10 * 30) + 1):
    im = cv2.imread(f'analysis/frames/f_{f+1:05d}.jpg'); hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(int)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    red = (((h <= 4) | (h >= 170)) & (s > 150) & (v > 90))
    orange = (h >= 5) & (h <= 20) & (s > 150) & (v > 150)
    white = (s < 45) & (v > 200)
    mint = (h >= 65) & (h <= 90) & (s > 120) & (v > 150)
    # the eye = red iris + orange/white touching it; start from the largest red blob
    n, lab, st, cen = cv2.connectedComponentsWithStats(red.astype(np.uint8))
    if n < 2: continue
    i = 1 + np.argmax(st[1:, 4]); irisA = st[i, 4]
    iris = (lab == i)
    eyeish = (red | orange | white).astype(np.uint8)
    n2, lab2 = cv2.connectedComponents(eyeish)
    ids = np.unique(lab2[iris]); ids = ids[ids > 0]
    comp = np.isin(lab2, ids)
    # drop the disc's own ring: pixels of the component must have mint within a short distance outside
    comp8 = comp.astype(np.uint8)
    cnts, _ = cv2.findContours(comp8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cnts, key=cv2.contourArea)
    pts = c[:, 0, :]
    inside = (pts[:, 0] > 1) & (pts[:, 0] < 852) & (pts[:, 1] > 1) & (pts[:, 1] < 478)   # ignore frame-border points
    pts = pts[inside]
    if len(pts) < 12: continue
    (cx, cy), (a, b), ang = cv2.fitEllipse(pts.reshape(-1, 1, 2).astype(np.float32))
    rx, ry = max(a, b) / 2, min(a, b) / 2
    rot = ang - 90 if a >= b else ang          # major-axis direction
    rot = ((rot + 90) % 180) - 90
    rows.append([round(f / 30, 4), round(cx, 2), round(cy, 2), round(rx, 2), round(ry, 2), round(rot, 2), int(PD.get(f, 99) > 0.3), int(inside.mean() * 100)])
    print(f"{f/30:7.3f} new={rows[-1][6]} centre ({cx:7.1f},{cy:7.1f}) rx {rx:7.1f} ry {ry:6.1f} rot {rot:6.1f}  contour-in-frame {inside.mean()*100:3.0f}%")
json.dump(rows, open('analysis/minteye_track.json', 'w'))
