"""Compact probe grid: pairs (source | rebuild) at 400x225, two pairs per row."""
import json, sys, pathlib
from PIL import Image, ImageDraw
R = pathlib.Path(__file__).resolve().parent.parent
rows = json.loads((R / 'render' / 'probe' / 'last.json').read_text())
w, h = 400, 225; per = 2
n = len(rows); nr = (n + per - 1) // per
S = Image.new('RGB', (per * (2 * w + 12), nr * (h + 16)), (20, 20, 20)); d = ImageDraw.Draw(S)
for i, r in enumerate(rows):
    f = int(round(r['s'] * 30))
    src = Image.open(R / 'analysis' / 'frames' / f'f_{min(2544, f + 1):05d}.jpg').resize((w, h), Image.LANCZOS)
    reb = Image.open(r['file']).convert('RGB').resize((w, h), Image.LANCZOS)
    x0 = (i % per) * (2 * w + 12); y0 = (i // per) * (h + 16)
    S.paste(src, (x0, y0 + 16)); S.paste(reb, (x0 + w, y0 + 16))
    d.text((x0 + 3, y0 + 2), f"src {r['s']:.2f}s", fill='yellow'); d.text((x0 + w + 3, y0 + 2), f"rebuild t={r['t']:.2f}s", fill='cyan')
out = sys.argv[1] if len(sys.argv) > 1 else str(R / 'render' / 'probe' / 'grid.jpg')
S.save(out, quality=86); print(out)
