import { chromium } from 'playwright'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url));
const b = await chromium.launch({ executablePath: '/Users/marcelojansson/Library/Caches/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-mac-arm64/chrome-headless-shell' });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } }); await p.goto('file://' + path.join(here, '..', 'build', 'index.html')); await p.evaluate(() => window.ready);
const [a, z, sel] = [+process.argv[2], +process.argv[3], process.argv[4]];
const rows = await p.evaluate(async ([a, z, sel]) => { const out = []; const cs = [...document.querySelectorAll(sel)];
  for (let t = a; t <= z + 1e-9; t += 1 / 60) { const s = await window.seek(t); out.push([t.toFixed(3), s.toFixed(3), ...cs.slice(0, 5).map(c => c.style.display === 'none' ? '-' : (+c.getAttribute('cx')).toFixed(1) + ',' + (+c.getAttribute('cy')).toFixed(1))]); } return out; }, [a, z, sel]);
rows.forEach(r => console.log(r.join('  '))); await b.close();
