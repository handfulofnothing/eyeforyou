"""Case-study page around the web player:  .venv/bin/python tools/site.py [--github URL]
Writes web/eyeforyou/ = index.html (this page) + fonts.css + img/ + media/, next to player/ (tools/build.py).
All numbers on the page come from the analysis files, not from prose."""
import base64, json, pathlib, re, shutil, subprocess, sys
import numpy as np
from PIL import Image

R = pathlib.Path(__file__).resolve().parent.parent
A = R / 'analysis'
OUT = R / 'web' / 'eyeforyou'
GITHUB = sys.argv[sys.argv.index('--github') + 1] if '--github' in sys.argv else ''
assert (OUT / 'player' / 'index.html').exists(), 'run tools/build.py first'
DUR = 84.867

# ---------------------------------------------------------------- data
blocks = json.loads((A / 'blocks.json').read_text())
bars = json.loads((A / 'bars.json').read_text())['bars']
events = json.loads((A / 'events_out.json').read_text())
tl = (R / 'src' / 'timeline.js').read_text()
step = float(re.search(r'WARP_STEP = ([\d.e-]+)', tl).group(1))
WS = np.array(json.loads(re.search(r'const WARP_S = (\[.*?\]);', tl, re.S).group(1)))
SRC = json.loads(re.search(r'const SRC=(\{.*?\});', tl, re.S).group(1))
TT = np.arange(len(WS)) * step
unwarp = lambda s: float(np.interp(s, WS, TT))      # source time -> rebuild (= audio) time

# beat grid from the fitted bars (bar length differs slightly per block)
beats = []
for i, b in enumerate(bars):
    L = b['len']
    start = b['t'] if i else bars[1]['t'] - L      # the first bar is clipped at 0
    for k in range(4):
        tb = start + k * L / 4
        if 0 <= tb <= DUR: beats.append([round(tb, 4), int(k == 0), b['bar'], k + 1])

kicks = np.load(A / 'kick_times.npy')
kflux = np.load(A / 'kflux.npy')
hz_in, HZ = len(kflux) / DUR, 200
n = int(DUR * HZ)
env = np.zeros(n)
for i in range(n):
    a, b = int(i / HZ * hz_in), int((i + 1) / HZ * hz_in) + 1
    env[i] = kflux[a:b].max() if b > a else 0
env = np.sqrt(np.clip(env, 0, 1))
env_b64 = base64.b64encode((env * 255).round().astype(np.uint8).tobytes()).decode()

# which events the warp anchors (same monotone selection as tools/smooth_warp.py)
pri = {'CUT': 3, 'HIT': 2, 'STAG': 1, 'MOVE': 0}
acc = [(0.0, 0.0), (DUR, DUR)]; anchored = set()
def fits(o, tg):
    pts = sorted(acc + [(o, tg)])
    return all(c > a + 1e-4 and d > b + 1e-4 and 0.33 <= (d - b) / (c - a) <= 4.0 for (a, b), (c, d) in zip(pts, pts[1:]))
for e in sorted(events, key=lambda e: (-pri[e['type']], e['t'])):
    if e['id'] != 'F30' and fits(e['t'], e['target']): acc.append((e['t'], e['target'])); anchored.add(e['id'])

quarters = np.array([b[0] for b in beats]); eighths = np.sort(np.concatenate([quarters, (quarters[:-1] + quarters[1:]) / 2]))
def off_grid(t, rule):                               # distance to the nearest beat (or eighth, for 8th-note events)
    g = eighths if rule == '8th' else quarters
    return t - g[np.abs(g - t).argmin()]
ev_rows, off_1998, off_now, cut_err, soft_dev = [], [], [], [], []
for e in events:
    at = unwarp(SRC.get(e['id'], e['t']))
    ev_rows.append([e['id'], e['scene'], e['type'], e['rule'], round(e['t'], 3), round(e['target'], 3), round(at, 3), e['what'], int(e['id'] in anchored)])
    if e['rule'] == 'keep': continue
    if e['type'] == 'CUT': cut_err.append(abs(at - e['target']) * 1000); continue
    off_1998.append(off_grid(e['t'], e['rule'])); off_now.append(off_grid(at, e['rule']))
    if e['id'] in anchored: soft_dev.append(abs(at - e['target']) * 1000)
ev_rows.sort(key=lambda r: r[6])

speed = np.load(A / 'warp_speed.npy')               # ds/dt at 1/120 s
speed20 = [round(float(x), 3) for x in speed[::6]]

ev_at = np.array([r[6] for r in ev_rows])
def jerk_series(name):
    j = np.array(json.loads((A / f'jank_{name}.json').read_text()))   # rows: time (s), jerk px, speed px
    J, V = j[:, 1], j[:, 2]
    Jc = np.minimum(J, 40)                            # one wild frame must not swallow a whole window
    out = []
    for w in range(int(np.ceil(DUR))):                # 1 s windows
        m = (j[:, 0] >= w) & (j[:, 0] < w + 1) & (V > 0)
        out.append(round(float(Jc[m].mean()), 2) if m.any() else 0)
    mv, big = V > 0, j[J > 10]
    near = int(sum(np.min(np.abs(ev_at - t)) < 0.15 for t in big[:, 0]))
    return out, dict(mean=round(float(J[mv].mean()), 1), over10=int(len(big)), over5=int((J > 5).sum()), near=round(100 * near / len(big)))
jb, jb_s = jerk_series('before')
ja, ja_s = jerk_series('release')

code_lines = sum(len(p.read_text().splitlines()) for d in ['src', 'tools', 'render'] for p in (R / d).glob('*')
                 if p.suffix in ('.js', '.py', '.mjs'))
types = {k: sum(1 for e in events if e['type'] == k) for k in ('HIT', 'MOVE', 'STAG', 'CUT')}
S = dict(
    events=len(events), **{k.lower(): v for k, v in types.items()},
    kicks=int(kicks.shape[1]), frames=len(list((A / 'frames').glob('f_*.jpg'))), blocks=len(blocks),
    res_lo=min(b['med_res_ms'] for b in blocks), res_hi=max(b['med_res_ms'] for b in blocks),
    now_med=round(float(np.median(np.abs(off_now)) * 1000)), now_max=round(float(np.max(np.abs(off_now)) * 1000)),
    old_med=round(float(np.median(np.abs(off_1998)) * 1000)), old_max=round(float(np.max(np.abs(off_1998)) * 1000)),
    cut_max=round(max(cut_err), 1), n_soft=len(off_now), n_anch=len(soft_dev), n_free=len(off_now) - len(soft_dev),
    soft_med=round(float(np.median(soft_dev))), soft_max=round(float(np.max(soft_dev))),
    spd_lo=round(float(speed.min()), 2), spd_hi=round(float(speed.max()), 2),
    jb=jb_s, ja=ja_s, code=code_lines,
)
DATA = dict(dur=DUR, blocks=[[b['key'], b['name'], b['start'], b['end'], b['bpm'], b['hits'], b['on_grid'], b['med_res_ms']] for b in blocks],
            bars=[[b['bar'], b['block'], b['t'], b['len'], b['db']] for b in bars], beats=beats,
            kicks=[[round(float(a), 3), round(float(s), 2)] for a, s in zip(*kicks)], env=env_b64, envHz=HZ,
            ev=ev_rows, speed=speed20, speedHz=20, jerk=[jb, ja], off=[[round(x * 1000) for x in off_1998], [round(x * 1000) for x in off_now]],
            stats=S)

# ---------------------------------------------------------------- assets
(OUT / 'img').mkdir(parents=True, exist_ok=True)
(OUT / 'media').mkdir(parents=True, exist_ok=True)
shutil.copy(R / 'src' / 'fonts.css', OUT / 'fonts.css')

def jpg(src, name, width=None, crop=None, q=84):
    im = Image.open(src).convert('RGB')
    if crop: im = im.crop(crop)
    if width and im.width > width: im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(OUT / 'img' / name, quality=q, optimize=True, progressive=True)
    return im.size

# the whole source at a glance: 50 frames, one every 1.7 s
cols, rows, tw, th = 10, 5, 192, 108
mos = Image.new('RGB', (cols * tw, rows * th), 'white')
nf = S['frames']
for i in range(cols * rows):
    f = min(nf, int((i + 0.5) / (cols * rows) * nf) + 1)
    im = Image.open(A / 'frames' / f'f_{f:05d}.jpg').convert('RGB').resize((tw, th), Image.LANCZOS)
    mos.paste(im, ((i % cols) * tw, (i // cols) * th))
mos.save(OUT / 'img' / 'mosaic.jpg', quality=84, optimize=True, progressive=True)
sizes = dict(mosaic=mos.size)
sizes['shapes'] = jpg(A / 'ref' / 'shapes_check.jpg', 'shapes.jpg', 1280, crop=(0, 0, 1281, 360))   # top row; the 4th cell is empty
sizes['flower_src'] = jpg(A / 'ref' / 'flower_onion_source.jpg', 'flower_src.jpg', 960)
sizes['flower_new'] = jpg(A / 'ref' / 'flower_onion_rebuild.jpg', 'flower_new.jpg', 960)
strip = Image.open(A / 'ref' / 'strips_blur9.jpg').convert('RGB')
px = np.asarray(strip).astype(int)
bars_y = np.where(((px < 70).all(axis=2)).mean(axis=1) > 0.9)[0]   # the near-black caption bars between rows
from PIL import ImageDraw
dr = ImageDraw.Draw(strip)
for y in bars_y: dr.line([(0, int(y)), (strip.width, int(y))], fill=(20, 20, 20))   # hide the debug captions
strip.save(A / 'ref' / '_strips_clean.jpg', quality=95)
sizes['strips'] = jpg(A / 'ref' / '_strips_clean.jpg', 'strips.jpg', 1600)

def remux(src, dst):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-c', 'copy', '-movflags', '+faststart', str(dst)], check=True)
remux(R / 'out' / 'eye4u_side_by_side.mp4', OUT / 'media' / 'eye4u_side_by_side.mp4')
remux(R / 'out' / 'eye4u_rebuild_1080p60.mp4', OUT / 'media' / 'eye4u_rebuild_1080p60.mp4')
shutil.copy(R / 'web' / 'eye4u.html', OUT / 'media' / 'eye4u.html')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '33.2', '-i', str(OUT / 'media' / 'eye4u_side_by_side.mp4'), '-frames:v', '1', '-q:v', '3',
                str(OUT / 'media' / 'sbs_poster.jpg')], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '33.2', '-i', str(R / 'out' / 'eye4u_rebuild_1080p60.mp4'), '-frames:v', '1', '-vf', 'scale=1200:-2',
                '-q:v', '3', str(OUT / 'media' / 'og.jpg')], check=True)
mb = lambda p: f"{(OUT / p).stat().st_size / 1e6:.0f} MB" if (OUT / p).stat().st_size > 2e6 else f"{(OUT / p).stat().st_size / 1e6:.1f} MB"

# ---------------------------------------------------------------- page
tpl = (R / 'tools' / 'site_tpl.html').read_text()
fill = dict(S)
fill.update(ja_near=S['ja']['near'], frames_fmt=f"{S['frames']:,}", jb_mean=S['jb']['mean'], ja_mean=S['ja']['mean'], jb_10=S['jb']['over10'], ja_10=S['ja']['over10'],
            size_mp4=mb('media/eye4u_rebuild_1080p60.mp4'), size_sbs=mb('media/eye4u_side_by_side.mp4'), size_html=mb('media/eye4u.html'),
            github=GITHUB, **{f'{k}_w': v[0] for k, v in sizes.items()}, **{f'{k}_h': v[1] for k, v in sizes.items()})
html = re.sub(r'\{\{(\w+)\}\}', lambda m: str(fill[m.group(1)]), tpl)
if not GITHUB:                                      # no public repo yet: drop the GitHub links
    html = re.sub(r'<a [^>]*data-gh[^>]*>.*?</a>', '', html, flags=re.S)
html = html.replace('/*__DATA__*/null', json.dumps(DATA, separators=(',', ':'), ensure_ascii=False))
(OUT / 'index.html').write_text(html)
total = sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
print(OUT / 'index.html', (OUT / 'index.html').stat().st_size // 1024, 'KB;', 'site total', total // (1 << 20), 'MB')
print(json.dumps({k: v for k, v in S.items()}, indent=None))
