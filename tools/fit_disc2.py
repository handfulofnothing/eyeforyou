"""Re-fit the mint disc centre after 15.95 s with its radius on a smooth schedule (only an arc is visible)."""
import numpy as np, json, cv2
from scipy.optimize import minimize
exec(open('tools/fit_mint.py').read().split("init={")[0])   # classes(), W, H, X, Y
sr = json.load(open('analysis/scene_raw.json')); PD = {int(f): p for f, p, h in sr['diffs']}
fit = json.load(open('analysis/fit_mint.json'))
def disc_model(dx, dy, R, eye):
    out = np.zeros((H, W), int)   # 0 = black outside
    r = np.hypot(X - dx, Y - dy)
    out[r < R] = 3; out[r < 0.898 * R] = 2; out[r < 0.795 * R] = 1
    # paint the fitted eye on top so it does not bias the disc
    m = model(eye); ey = (m == 4) | ((m == 3) & (np.hypot(X - eye[3], Y - eye[4]) < 200 * np.exp(eye[5])))
    out[ey] = m[ey]
    return out
res = []; prev = np.array([245.0, 43.0])
eyeRows = {round(r[0], 3): r for r in fit}
for k in range(0, 36):
    t = round(15.95 + k / 30, 4); f = int(round(t * 30))
    if PD.get(f, 99) <= 0.3: continue
    R = float(np.exp(np.interp(t, [15.95, 16.3, 16.8, 17.1], np.log([770, 1500, 2300, 2600]))))
    cls = classes(t); r0 = eyeRows.get(t)
    eye = np.array(r0[1:8]) if r0 else None
    def loss(p):
        m = disc_model(p[0], p[1], R, eye if eye is not None else [0, 0, 0, -99, -99, np.log(1e-3), 0])
        sel = cls != 4
        return np.mean(m[sel] != cls[sel])
    best = None
    for x0 in [prev] + [prev + np.random.RandomState(k * 7 + j).uniform(-250, 250, 2) for j in range(12)]:
        r = minimize(loss, x0, method='Nelder-Mead', options={'xatol': 0.5, 'fatol': 1e-5, 'maxiter': 400})
        if best is None or r.fun < best.fun: best = r
    prev = best.x
    res.append([t, float(best.x[0]), float(best.x[1]), R, float(best.fun)])
    print(f"{t:7.3f} centre ({best.x[0]:8.1f},{best.x[1]:8.1f}) R {R:7.1f} err {best.fun:.3f}")
json.dump(res, open('analysis/fit_disc2.json', 'w'))
