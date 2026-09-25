// Frame-by-frame motion audit: node motion_audit.mjs [t0] [t1]
// Steps seek() at 60 Hz, records every visible element's screen-space box, and reports
// velocity kinks (sudden changes of speed/direction) per element.
import { chromium } from 'playwright';
import path from 'node:path'; import fs from 'node:fs'; import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url));
const t0 = +(process.argv[2] || 0), t1 = +(process.argv[3] || 84.86);
const exe = process.env.PW_CHROME || '/Users/marcelojansson/Library/Caches/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-mac-arm64/chrome-headless-shell';
const browser = await chromium.launch({ executablePath: exe });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
page.on('pageerror', e => console.error('PAGE ERROR', e.message));
await page.goto('file://' + path.join(here, '..', 'build', 'index.html'));
await page.evaluate(() => window.ready);
const res = await page.evaluate(async ([t0, t1]) => {
  const els = [...document.querySelectorAll('#sv circle, #sv ellipse, #sv path, #sv text, #sv rect, #sv image')].filter(e => !e.closest('mask, clipPath, filter, defs'));
  const label = e => {
    let s = e.closest('g[id]')?.id || '?';
    const txt = e.tagName === 'text' ? ':' + e.textContent.slice(0, 14) : '';
    return `${s}/${e.tagName}${txt}#${els.indexOf(e)}`;
  };
  const vis = e => { for (let n = e; n && n.id !== 'sv'; n = n.parentNode) { if (n.style && n.style.display === 'none') return false; const o = n.getAttribute && n.getAttribute('opacity'); if (o !== null && +o < 0.02) return false; } return true; };
  const N = Math.round((t1 - t0) * 60);
  const tracks = new Map();   // idx -> array of [frame, cx, cy, w, h]
  for (let i = 0; i <= N; i++) {
    const t = t0 + i / 60;
    await window.seek(t);
    for (let k = 0; k < els.length; k++) {
      const e = els[k];
      if (!vis(e)) continue;
      // measure through the element's own transform: local geometry centre -> screen, true scale
      const M = e.getScreenCTM(); if (!M) continue;
      let lx, ly, size;
      const tg = e.tagName;
      if (tg === 'circle') { lx = +e.getAttribute('cx') || 0; ly = +e.getAttribute('cy') || 0; size = +e.getAttribute('r') || 0; }
      else if (tg === 'ellipse') { lx = +e.getAttribute('cx') || 0; ly = +e.getAttribute('cy') || 0; size = Math.sqrt((+e.getAttribute('rx') || 0) * (+e.getAttribute('ry') || 0)); }
      else { const b = e.getBBox(); lx = b.x + b.width / 2; ly = b.y + b.height / 2; size = Math.hypot(b.width, b.height) / 2; }
      const det = Math.sqrt(Math.abs(M.a * M.d - M.b * M.c));
      const sx = M.a * lx + M.c * ly + M.e, sy = M.b * lx + M.d * ly + M.f, ss = size * det;
      if (!(ss > 0.5) || ss > 4000 || Math.abs(sx) > 6000 || Math.abs(sy) > 6000) continue;
      const rot = Math.atan2(M.b, M.a) * 180 / Math.PI;
      if (!tracks.has(k)) tracks.set(k, []);
      tracks.get(k).push([i, sx, sy, ss, rot]);
    }
  }
  // kinks: compare consecutive velocities over continuous runs (element visible in frames i-1, i, i+1)
  const out = [];
  for (const [k, a] of tracks) {
    for (let j = 1; j < a.length - 1; j++) {
      const [f0] = a[j - 1], [f1] = a[j], [f2] = a[j + 1];
      if (f1 !== f0 + 1 || f2 !== f1 + 1) continue;
      for (const [c, name] of [[1, 'x'], [2, 'y'], [3, 'size'], [4, 'rot']]) {
        let v0 = a[j][c] - a[j - 1][c], v1 = a[j + 1][c] - a[j][c];
        if (c === 4) { v0 = ((v0 + 540) % 360) - 180; v1 = ((v1 + 540) % 360) - 180; }
        const acc = Math.abs(v1 - v0), sp = Math.max(Math.abs(v0), Math.abs(v1));
        if (acc > (c === 4 ? 1.5 : 3) && acc > 0.45 * sp) out.push([+(t0 + f1 / 60).toFixed(3), label(els[k]), name, +v0.toFixed(1), +v1.toFixed(1)]);
      }
    }
  }
  return out;
}, [t0, t1]);
fs.writeFileSync(path.join(here, 'probe', `audit_${t0}_${t1}.json`), JSON.stringify(res));
// summarise: group by element, show worst
const by = {};
for (const r of res) (by[r[1]] ??= []).push(r);
const rows = Object.entries(by).sort((a, b) => b[1].length - a[1].length);
console.log(`kinks: ${res.length} across ${rows.length} elements`);
for (const [el, list] of rows.slice(0, 40)) {
  const worst = list.sort((a, b) => Math.abs(b[4] - b[3]) - Math.abs(a[4] - a[3]))[0];
  console.log(`${String(list.length).padStart(4)}  ${el.padEnd(46)} e.g. t=${worst[0]} ${worst[2]}: ${worst[3]} -> ${worst[4]} px/frame`);
}
await browser.close();
