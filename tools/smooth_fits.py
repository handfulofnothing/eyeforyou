"""Smooth the per-frame camera fits and export dense tracks (1/60 s) to src/fits.js."""
import json, numpy as np, matplotlib
from scipy.interpolate import UnivariateSpline
matplotlib.use('Agg'); import matplotlib.pyplot as plt

_sr = json.load(open('analysis/scene_raw.json'))
_PD = {int(f): p for f, p, h in _sr['diffs']}
def dedupe(rows, cols=None):
    """Keep only capture frames that show a NEW Flash frame (pixel change vs previous capture)."""
    out = []
    for r in rows:
        f = int(round(r[0] * 30))
        if _PD.get(f, 99) <= 0.3: continue      # duplicate of the previous capture
        out.append(r)
    return out

def flash_clock(t0, t1):
    """Capture frame -> retimed Flash-frame time, for every new frame in [t0, t1]."""
    frames = [f for f in range(int(round(t0 * 30)), int(round(t1 * 30)) + 1) if _PD.get(f, 99) > 0.3]
    T = flash_time([f / 30 for f in frames])
    return {f: float(x) for f, x in zip(frames, T)}

def retime(rows, clock):
    out = []
    for r in rows:
        f = int(round(r[0] * 30))
        if f in clock: out.append([clock[f]] + list(r[1:]))
    return out

def flash_time(tcap):
    """Smooth monotone map Flash-frame index -> time. The 1998 player ran at an irregular
    16-20 fps; the authored animation advances one step per Flash frame, so we fit a smooth
    clock through the capture times of the new frames and re-time every sample onto it."""
    k = np.arange(len(tcap), dtype=float)
    sp_ = UnivariateSpline(k, np.asarray(tcap) - 1 / 60, k=3, s=len(k) * 0.012 ** 2)
    T = sp_(k); T = np.maximum.accumulate(T + np.arange(len(T)) * 1e-6)
    return T

def spline(t, y, sigma, w=None):
    t = np.asarray(t, float); y = np.asarray(y, float)
    return UnivariateSpline(t, y, k=3, s=len(t) * sigma ** 2, w=w)

from scipy.interpolate import PchipInterpolator
def smooth(t, y, sigma, mono=0, pin=None, step=1/30, rel=0.0):
    """Smoothing spline -> knots every `step` -> optional monotone (+1/-1) -> PCHIP (no overshoot)."""
    t = np.asarray(t, float); y = np.asarray(y, float)
    o = np.argsort(t, kind='stable'); t, y = t[o], y[o]
    keep = np.r_[True, np.diff(t) > 1e-4]; t, y = t[keep], y[keep]
    sig = np.maximum(sigma, rel * np.abs(y))          # noise grows with distance when zoomed far in
    sp_ = UnivariateSpline(t, y, k=3, w=1 / sig, s=len(t))
    kt = np.arange(t[0], t[-1] + 1e-9, step); kt[-1] = min(kt[-1], t[-1])
    kv = sp_(kt)
    if pin:
        for tp, vp in pin: kv[np.argmin(np.abs(kt - tp))] = vp
    if mono > 0: kv = np.maximum.accumulate(kv)
    if mono < 0: kv = np.minimum.accumulate(kv)
    f = PchipInterpolator(kt, kv, extrapolate=True); df = f.derivative()
    s0, s1 = float(df(kt[0])), float(df(kt[-1]))
    def g(T):
        T = np.asarray(T, float); y = f(np.clip(T, kt[0], kt[-1]))
        y = np.where(T > kt[-1], kv[-1] + s1 * (T - kt[-1]), y)
        return np.where(T < kt[0], kv[0] + s0 * (T - kt[0]), y)
    return g

def unwrap_deg(a, period=360):
    a = np.asarray(a, float).copy()
    for i in range(1, len(a)):
        while a[i] - a[i - 1] > period / 2: a[i] -= period
        while a[i] - a[i - 1] < -period / 2: a[i] += period
    return a

dense = lambda a, b: np.round(np.arange(a, b + 1e-9, 1 / 60), 4)
out = {}; fig, axs = plt.subplots(4, 1, figsize=(16, 13))

# ---------------- drop: parametrise by the mark point under screen centre ----------------
rows = json.load(open('analysis/fit_drop.json'))
rows = [r for r in rows if not (13.94 < r[0] < 14.13)]            # all-orange frames carry no pose
rows = retime(rows, flash_clock(12.85, 14.7))
t = np.array([r[0] for r in rows]); cx = np.array([r[1] for r in rows]); cy = np.array([r[2] for r in rows])
ls = np.array([r[3] for r in rows]); th = unwrap_deg([r[4] for r in rows])
# local point at screen centre: F = R^-1 ((427,240) - C) / s
c, sn = np.cos(np.radians(th)), np.sin(np.radians(th)); S = np.exp(ls)
dx, dy = (427 - cx) / S, (240 - cy) / S
fx, fy = c * dx + sn * dy, -sn * dx + c * dy
# start at the logo (s = 1) just before the first zoomed frame
t = np.r_[12.83, t]; ls = np.r_[0.0, ls]; th = np.r_[0.0, th]; fx = np.r_[(427 - 496), fx]; fy = np.r_[(240 - 205), fy]
spl_ls = smooth(t, ls, 0.05, mono=1, pin=[(12.83, 0.0)], step=1/60)
spl_th = smooth(t, th, 1.5, mono=-1, pin=[(12.83, 0.0)], step=1/60)
spl_fx, spl_fy = smooth(t, fx, 0.35), smooth(t, fy, 0.25)
T = dense(12.83, 14.62)
LS, TH, FX, FY = spl_ls(T), spl_th(T), spl_fx(T), spl_fy(T)
cc, ss = np.cos(np.radians(TH)), np.sin(np.radians(TH)); SS = np.exp(LS)
CX = 427 - SS * (cc * FX - ss * FY); CY = 240 - SS * (ss * FX + cc * FY)
out['FIT_DROP'] = [[float(a), round(float(b), 2), round(float(c_), 2), round(float(d), 4), round(float(e), 3)] for a, b, c_, d, e in zip(T, CX, CY, SS, TH)]
axs[0].plot(t, ls, 'o', ms=3); axs[0].plot(T, LS); axs[0].plot(t, th / 60, 'x', ms=3); axs[0].plot(T, TH / 60); axs[0].set_title('drop: log scale (o) and rotation/60 (x)')

# ---------------- mint disc + eye ----------------
fit = json.load(open('analysis/fit_mint.json')); small = json.load(open('analysis/mint_eye_small.json'))
MC = flash_clock(15.35, 17.2)
fit = retime(fit, MC); small = retime(small, MC)
d2 = retime([r for r in json.load(open('analysis/fit_disc2.json')) if r[4] < 0.05], MC)
dr = [[r[0], r[1], r[2], r[3]] for r in fit if r[0] < 15.94] + [[r[0], r[1], r[2], np.log(r[3])] for r in d2]
td = np.array([r[0] for r in dr]); dX = np.array([r[1] for r in dr]); dY = np.array([r[2] for r in dr]); dR = np.array([r[3] for r in dr])
td = np.r_[min(15.36, td.min() - 0.02), td]; dX = np.r_[267.5, dX]; dY = np.r_[46.7, dY]; dR = np.r_[np.log(0.5), dR]
# early part is a pure zoom about the disc centre: smooth R in log space, centre gently
sX, sY, sR = smooth(td, dX, 12), smooth(td, dY, 12), smooth(td, dR, 0.08, mono=1)
T = dense(15.38, 17.12)
out['FIT_DISC'] = [[float(a), round(float(b), 1), round(float(c_), 1), round(float(np.exp(d)), 2)] for a, b, c_, d in zip(T, sX(T), sY(T), sR(T))]
# ---- mint eye: three Flash tweens, fitted per FLASH FRAME (the 1998 player showed frames at
# jittery times; the authored motion is smooth per frame), mapped to time with a steady clock ----
from math import comb
from scipy.ndimage import gaussian_filter1d
tr = [r for r in json.load(open('analysis/minteye_track.json')) if r[6] == 1 and 15.49 <= r[0] <= 16.44]
kk = []; kc = 0; prv = None
for r in tr:
    if prv is not None: kc += 2 if (prv < 15.94 and r[0] > 15.99) else 1     # one dropped frame at the tween change
    kk.append(kc); prv = r[0]
kk = np.array(kk, float); tcap = np.array([r[0] for r in tr])
p3 = [r for r in fit if 16.44 < r[0] <= 17.07 and _PD.get(int(round(r[0] * 30)), 99) > 0.3]
k3 = []; kc = kk[-1]; prv = tcap[-1]
for r in p3: kc += max(1, int(round((r[0] - prv) / 0.048))); k3.append(kc); prv = r[0]
k3 = np.array(k3, float)
cb, ca = np.polyfit(np.r_[kk, k3], np.r_[tcap, [r[0] for r in p3]], 1)      # t = ca + cb * k
print('eye Flash clock %.2f fps' % (1 / cb))
def bezN(Cp, u):
    n = len(Cp) - 1
    B = np.array([[comb(n, j) * (1 - uu) ** (n - j) * uu ** j for j in range(n + 1)] for uu in np.atleast_1d(u)]); return B @ Cp
# phase 1: straight line (PCA), quadratic progress and size per frame, constant tilt
P1 = np.array([[r[1], r[2]] for r in tr if r[0] <= 15.94]); K1 = kk[:len(P1)]
mu = P1.mean(0); dirv = np.linalg.svd(P1 - mu)[2][0]; dirv = dirv if dirv[0] > 0 else -dirv
d1 = (P1 - mu) @ dirv
cd1 = np.polyfit(K1, d1, 2); kv = -cd1[1] / (2 * cd1[0])                   # frame where it comes to rest
rx1 = np.array([r[3] for r in tr if r[0] <= 15.94]); m_ = K1 >= 1
cr1 = np.polyfit(K1[m_], rx1[m_], 2)
ks = np.roots(np.r_[cd1[:2], cd1[2] - np.polyval(cd1, K1[0]) + 113.8])      # where the tween starts (eye leaves the disc centre)
ks = float(np.max(ks[np.isreal(ks)].real[ks[np.isreal(ks)].real < 0])) if np.any(np.isreal(ks)) else -1.0
print('eye phase 1: progress rms %.2f px, size rms %.2f px, rest at frame %.2f, start frame %.2f' % (
    np.sqrt(np.mean((np.polyval(cd1, K1) - d1) ** 2)), np.sqrt(np.mean((np.polyval(cr1, K1[m_]) - rx1[m_]) ** 2)), kv, ks))
P1end = mu + dirv * np.polyval(cd1, kv); rx1end = float(np.polyval(cr1, kv)); th1 = 37.5 - 90
# phase 2: Bezier hook pinned at the phase-1 rest point; progress / size / tilt as smooth functions of frame
p2 = [r for r in tr if r[0] > 15.99]; K2 = kk[len(P1):]
C2 = np.vstack([P1end, [[r[1], r[2]] for r in p2]]); K2a = np.r_[kv, K2]
dd = np.r_[0, np.cumsum(np.hypot(*np.diff(C2, axis=0).T))]; uu = dd / dd[-1]
for _ in range(300):
    B = np.array([[comb(3, j) * (1 - x) ** (3 - j) * x ** j for j in range(4)] for x in uu])
    Cp2 = np.linalg.lstsq(B[:, 1:], C2 - np.outer(B[:, 0], P1end), rcond=None)[0]; Cp2 = np.vstack([P1end, Cp2])
    g = np.linspace(0, 1, 2001); Q = bezN(Cp2, g); uu = np.maximum.accumulate(np.array([g[np.argmin(((Q - q) ** 2).sum(1))] for q in C2]))
ug2 = np.linspace(0, 1.15, 4601); Qg = bezN(Cp2, ug2); lg2 = np.r_[0, np.cumsum(np.hypot(*np.diff(Qg, axis=0).T))]
L2 = np.interp(uu, ug2, lg2)
cl2 = np.polyfit(K2a, L2, 3); rx2 = np.r_[rx1end, [r[3] for r in p2]]; cr2 = np.polyfit(K2a, rx2, 3)
th2 = np.r_[th1, [r[5] - 90 for r in p2]]; ct2 = np.polyfit(K2a, th2, 3)
print('eye phase 2: path rms %.2f px, progress rms %.2f px, size rms %.2f px, tilt rms %.2f deg' % (
    np.sqrt(np.mean(np.hypot(*(bezN(Cp2, uu) - C2).T) ** 2)), np.sqrt(np.mean((np.polyval(cl2, K2a) - L2) ** 2)),
    np.sqrt(np.mean((np.polyval(cr2, K2a) - rx2) ** 2)), np.sqrt(np.mean((np.polyval(ct2, K2a) - th2) ** 2))))
k2e = K2[-1]
P2end = bezN(Cp2, float(np.interp(np.polyval(cl2, k2e), lg2, ug2)))[0]; s2e = float(np.polyval(cr2, k2e)) / 100; th2e = float(np.polyval(ct2, k2e))
# phase 3: camera push; focus point in eye coords + monotone zoom, as smooth functions of frame
def focus_of(c, s_, th_):
    d_ = (np.array([427.0, 240.0]) - c) / s_; a_ = np.radians(-th_)
    return np.array([np.cos(a_) * d_[0] - np.sin(a_) * d_[1], np.sin(a_) * d_[0] + np.cos(a_) * d_[1]])
keep = [i for i, r in enumerate(p3) if r[8] < 0.07]
K3 = np.r_[k2e, k3[keep]]
F3 = np.array([focus_of(P2end, s2e, th2e)] + [focus_of(np.array([p3[i][4], p3[i][5]]), np.exp(p3[i][6]), p3[i][7]) for i in keep])
LS3 = np.r_[np.log(s2e), [p3[i][6] for i in keep]]; TH3 = np.r_[th2e, [p3[i][7] for i in keep]]
sF3x, sF3y = smooth(K3, F3[:, 0], 3.0, step=0.5), smooth(K3, F3[:, 1], 2.0, step=0.5)
sLS3 = smooth(K3, LS3, 0.05, mono=1, step=0.5); sTH3 = smooth(K3, TH3, 1.2, step=0.5)
# ---- compose per frame on a fine grid, round the two hand-offs, then map frames -> time ----
kg = np.arange(ks - 0.5, (17.14 - ca) / cb, 0.02); X = []; Y = []; LSx = []; THx = []
for k_ in kg:
    if k_ <= kv:
        kc_ = max(k_, ks); pos = mu + dirv * np.polyval(cd1, kc_); sc = max(np.polyval(cr1, kc_), 1.0) / 100; th_ = th1
    elif k_ <= k2e:
        u_ = float(np.interp(np.polyval(cl2, k_), lg2, ug2)); pos = bezN(Cp2, u_)[0]; sc = np.polyval(cr2, k_) / 100; th_ = np.polyval(ct2, k_)
    else:
        sc = float(np.exp(sLS3(k_))); th_ = float(sTH3(k_)); F = np.array([float(sF3x(k_)), float(sF3y(k_))])
        a_ = np.radians(th_); Rm = np.array([[np.cos(a_), -np.sin(a_)], [np.sin(a_), np.cos(a_)]]); pos = np.array([427.0, 240.0]) - sc * (Rm @ F)
    X.append(pos[0]); Y.append(pos[1]); LSx.append(np.log(sc)); THx.append(th_)
# ~0.7 Flash frame everywhere; ~1.8 frames across the push-in start so the zoom eases in
wj = np.clip((kg - (k2e - 2.5)) / 4.0, 0, 1); wj = wj * wj * (3 - 2 * wj)
def blend(v):
    v = np.array(v); a1 = gaussian_filter1d(v, 0.7 / 0.02, mode='nearest'); a2 = gaussian_filter1d(v, 1.8 / 0.02, mode='nearest')
    return a1 * (1 - wj) + a2 * wj
X, Y, LSx, THx = [blend(v) for v in (X, Y, LSx, THx)]
tg = ca + cb * kg
T = dense(15.38, 17.12)
rows = [[float(t_), round(float(np.interp(t_, tg, X)), 2), round(float(np.interp(t_, tg, Y)), 2), round(float(np.exp(np.interp(t_, tg, LSx))), 5), round(float(np.interp(t_, tg, THx)), 3)] for t_ in T]
out['FIT_MINTEYE'] = rows
t_start_eye = float(ca + cb * ks); print('eye appears at %.3f s' % t_start_eye)
te = np.array([r[0] for r in rows]); ex = np.array([r[1] for r in rows]); ey = np.array([r[2] for r in rows]); es = np.log(np.array([r[3] for r in rows]))
sEx = lambda T_: np.interp(T_, te, ex); sEy = lambda T_: np.interp(T_, te, ey); sEs = lambda T_: np.interp(T_, te, es)
t3 = np.array([r[0] for r in p3]); s3 = np.exp(np.array([r[6] for r in p3]))
fig3, ax3 = plt.subplots(1, 2, figsize=(15, 5))
ax3[0].plot([r[1] for r in tr if r[0] < 16.45], [r[2] for r in tr if r[0] < 16.45], 'o'); ax3[0].plot(ex[te < 16.45], ey[te < 16.45], '-'); ax3[0].invert_yaxis(); ax3[0].set_aspect('equal'); ax3[0].set_title('eye centre path, phases 1-2 (measured o, rebuild -)')
ax3[1].plot([r[0] for r in tr if r[0] < 16.45], np.log([r[3] / 100 for r in tr if r[0] < 16.45]), 'o'); ax3[1].plot(t3, np.log(s3), 'x'); ax3[1].plot(te, es, '-'); ax3[1].set_title('eye log scale')
fig3.tight_layout(); fig3.savefig('analysis/ref/eye_fit.png', dpi=60)
axs[1].plot(te, es, 'o', ms=3); axs[1].plot(T, sEs(T)); axs[1].plot(td, dR / 3, 'x', ms=3); axs[1].plot(T, sR(T) / 3); axs[1].set_title('mint: eye log scale (o), disc logR/3 (x)')
axs[2].plot(te, ex, 'o', ms=3); axs[2].plot(T, sEx(T)); axs[2].plot(te, ey, 'x', ms=3); axs[2].plot(T, sEy(T)); axs[2].set_title('mint eye x (o), y (x)')

# ---------------- sunburst ----------------
pol = json.load(open('analysis/fit_sun_polar.json')); tail = json.load(open('analysis/fit_sun_tail.json'))
SC = flash_clock(17.05, 20.1)
pol = retime(pol, SC); tail = [r for r in tail if r[1] is not None]; tail = retime(tail, SC)
P = [r for r in pol if r[3] is not None and r[0] <= 19.09]
tp = np.array([r[0] for r in P]); px = np.array([r[1] for r in P], float); py = np.array([r[2] for r in P], float)
rw = unwrap_deg([r[3] for r in P], 72)
ro_t = [r[0] for r in P if r[4] is not None and r[0] <= 18.01]; ro_v = unwrap_deg([r[4] for r in P if r[4] is not None and r[0] <= 18.01], 72)
Tl = [r for r in tail if r[0] < 19.95]
tt = np.array([r[0] for r in Tl]); tx = np.array([r[1] for r in Tl]); ty = np.array([r[2] for r in Tl])
trw = np.array([r[3] for r in Tl]); tro = np.array([r[4] for r in Tl])
# join: rotations continue across the join (unwrap relative to the polar end)
trw = trw + 72 * np.round((rw[-1] - trw[0]) / 72); tro_join = tro + 72 * np.round(((ro_v[-1] - 49) - tro[0]) / 72)
allt = np.r_[17.07, tp, tt]; allx = np.r_[475, px, tx]; ally = np.r_[160, py, ty]; allw = np.r_[45, rw, trw]
allot = np.r_[17.07, ro_t, tt]; allo = np.r_[40, ro_v, tro_join]
sx_, sy_ = smooth(allt, allx, 3.0, rel=0.06), smooth(allt, ally, 3.0, rel=0.06)
sw_, so_ = smooth(allt, allw, 0.8, mono=1), smooth(allot, allo, 1.5, mono=-1)
T = dense(17.06, 20.08)
out['FIT_SUN'] = [[float(a), round(float(b), 1), round(float(c_), 1), round(float(d), 2), round(float(e), 2)] for a, b, c_, d, e in zip(T, sx_(T), sy_(T), sw_(T), so_(T))]
axs[3].plot(allt, allw, 'o', ms=3); axs[3].plot(T, sw_(T)); axs[3].plot(allot, allo, 'x', ms=3); axs[3].plot(T, so_(T)); axs[3].set_title('sun: white rotation (o), orange rotation (x)')
# ---------------- flower: measured path (tools/track_flower.py) ----------------
fl = [r for r in json.load(open('analysis/flower_track.json')) if r[5] == 1 and r[0] < 15.35]
fl = retime(fl, flash_clock(14.40, 15.36))
ft = np.array([r[0] for r in fl]); fxs = np.array([r[1] for r in fl]); fys = np.array([r[2] for r in fl])
ftip = np.log(np.array([r[3] for r in fl]))
# spin: unwrap the 4-fold tip angle assuming the smallest forward step, then one constant rate
ang = [fl[0][4]]
for r in fl[1:]:
    exp_ = ang[-1] + 25.5 * max(1, round((r[0] - fl[fl.index(r) - 1][0]) / 0.05))
    cands = [r[4] + 90 * k for k in range(-2, 12)]
    ang.append(min(cands, key=lambda c: abs(c - exp_)))
ang = np.array(ang)
rate, off = np.polyfit(ft, ang, 1)
print('flower spin %.1f deg/s' % rate)
# path: one cubic Bezier (Flash motion guide) fitted to the measured centres, rms 2 px
from math import comb
PP = np.c_[fxs, fys]
def bez(Cp, u):
    B = np.array([[comb(3, k) * (1 - uu) ** (3 - k) * uu ** k for k in range(4)] for uu in np.atleast_1d(u)]); return B @ Cp, B
dd = np.r_[0, np.cumsum(np.hypot(*np.diff(PP, axis=0).T))]; uu_ = dd / dd[-1]
for _ in range(400):
    _, B = bez(np.zeros((4, 2)), uu_); Cp, *_ = np.linalg.lstsq(B, PP, rcond=None)
    grid = np.linspace(-0.08, 1.08, 4641); Q, _ = bez(Cp, grid)
    uu_ = np.maximum.accumulate(np.array([grid[np.argmin(((Q - q) ** 2).sum(1))] for q in PP]))
res_ = np.hypot(*(bez(Cp, uu_)[0] - PP).T); print('flower bezier rms %.2f max %.2f' % (np.sqrt(np.mean(res_ ** 2)), res_.max()))
# progress along the arc = one Flash ease-out tween: quadratic in (capture) time, rms 6 px along the arc
tcap = np.array([r[0] for r in [q for q in json.load(open('analysis/flower_track.json')) if q[5] == 1 and q[0] < 15.35]]) - 1 / 60
# arc-length parametrisation of the guide: Flash moves along a motion guide by distance travelled
ug = np.linspace(-0.2, 1.2, 14001); Qg, _ = bez(Cp, ug)
lg = np.r_[0, np.cumsum(np.hypot(*np.diff(Qg, axis=0).T))]; lg -= np.interp(0, ug, lg)
Lm = np.interp(uu_, ug, lg)                                   # measured distance along the arc
cl = np.polyfit(tcap, Lm, 2)                                   # ease-out in distance
rl = np.polyval(cl, tcap) - Lm; print('flower ease-out in arc length: rms %.1f px  max %.1f px' % (np.sqrt(np.mean(rl ** 2)), np.abs(rl).max()))
su = lambda T_: np.interp(np.polyval(cl, np.asarray(T_, float)), lg, ug)
cs_ = np.polyfit(tcap, ftip, 2); sft = lambda T_: np.polyval(cs_, np.asarray(T_, float))
rate, off = np.polyfit(tcap, ang, 1)          # constant spin on the same clock
ft = tcap
T = dense(14.40, 15.38)
UU = su(T); XY, _ = bez(Cp, UU)
out['FIT_FLOWER'] = [[float(a), round(float(p_[0]), 2), round(float(p_[1]), 2), round(float(np.exp(d)), 2), round(float(rate * a + off), 2)] for a, p_, d in zip(T, XY, sft(T))]
sfx = lambda T_: bez(Cp, su(T_))[0][:, 0]; sfy = lambda T_: bez(Cp, su(T_))[0][:, 1]
fig2, ax2 = plt.subplots(1, 2, figsize=(14, 5))
ax2[0].plot(fxs, fys, 'o'); ax2[0].plot(sfx(T), sfy(T), '-'); ax2[0].invert_yaxis(); ax2[0].set_title('flower path (measured o, rebuild -)'); ax2[0].set_aspect('equal')
ax2[1].plot(ft, uu_, 'o'); ax2[1].plot(T, UU); ax2[1].set_title('progress along the arc u(t)')
fig2.tight_layout(); fig2.savefig('analysis/ref/flower_fit.png', dpi=60)
plt.tight_layout(); plt.savefig('analysis/ref/fits_smooth.png', dpi=55)
js = "// generated by tools/smooth_fits.py: smoothed per-frame camera fits, dense 1/60 s\n" + ''.join(f"const {k}={json.dumps(v)};\n" for k, v in out.items())
open('src/fits.js', 'w').write(js)
print({k: len(v) for k, v in out.items()})
