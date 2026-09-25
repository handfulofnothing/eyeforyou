"""Side-by-side: source frame (left) vs rebuild probe (right) for the last probe run."""
import json, sys, pathlib
from PIL import Image, ImageDraw
R = pathlib.Path(__file__).resolve().parent.parent
rows = json.loads((R / 'render' / 'probe' / 'last.json').read_text())
out = sys.argv[1] if len(sys.argv) > 1 else str(R / 'render' / 'probe' / 'cmp.jpg')
w, h = 640, 360
sheet = Image.new('RGB', (2 * w, len(rows) * (h + 18)), (25, 25, 25))
d = ImageDraw.Draw(sheet)
for i, r in enumerate(rows):
    f = int(round(r['s'] * 30))
    src = Image.open(R / 'analysis' / 'frames' / f'f_{min(2544, f + 1):05d}.jpg').resize((w, h), Image.LANCZOS)
    reb = Image.open(r['file']).convert('RGB').resize((w, h), Image.LANCZOS)
    y = i * (h + 18)
    sheet.paste(src, (0, y + 18)); sheet.paste(reb, (w, y + 18))
    d.text((4, y + 3), f"SOURCE s={r['s']:.3f} (f{f})", fill='yellow')
    d.text((w + 4, y + 3), f"REBUILD t={r['t']:.3f}", fill='cyan')
sheet.save(out, quality=88)
print(out)
