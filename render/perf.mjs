import { chromium } from 'playwright'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url));
const b = await chromium.launch({ executablePath: '/Users/marcelojansson/Library/Caches/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-mac-arm64/chrome-headless-shell' });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } }); await p.goto('file://' + path.join(here, '..', 'build', 'index.html')); await p.evaluate(() => window.ready);
const r = await p.evaluate(async () => {
  const worst = []; let tot = 0; const n = 5092;
  for (let i = 0; i < n; i++) { const t0 = performance.now(); await window.seek(i / 60); const dt = performance.now() - t0; tot += dt; worst.push([dt, i / 60]); }
  worst.sort((a, b) => b[0] - a[0]);
  return { mean: tot / n, p99: worst[Math.floor(n * 0.01)][0], worst: worst.slice(0, 5) };
});
console.log(JSON.stringify(r)); await b.close();
