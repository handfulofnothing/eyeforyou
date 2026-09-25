// Probe frames: node probe.mjs [--rebuild] t1 t2 ...
// Default: times are SOURCE seconds; each is mapped to rebuild time with unwarp().
import { chromium } from 'playwright';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const rebuild = args[0] === '--rebuild';
const times = (rebuild ? args.slice(1) : args).map(Number);
const out = path.join(here, 'probe');
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ executablePath: process.env.PW_CHROME || '/Users/marcelojansson/Library/Caches/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-mac-arm64/chrome-headless-shell' });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
page.on('pageerror', e => console.error('PAGE ERROR', e.message));
page.on('console', m => { if (m.type() === 'error') console.error('console', m.text()); });
await page.goto('file://' + path.join(here, '..', 'build', 'index.html'));
await page.evaluate(() => window.ready);
const stage = await page.$('#stage');
const rows = [];
for (const x of times) {
  const t = rebuild ? x : await page.evaluate(s => window.unwarp(s), x);
  const s = await page.evaluate(async t => await window.seek(t), t);
  const file = path.join(out, `p_${s.toFixed(3)}.png`);
  await stage.screenshot({ path: file });
  rows.push({ t: +t.toFixed(4), s: +s.toFixed(4), file });
}
fs.writeFileSync(path.join(out, 'last.json'), JSON.stringify(rows, null, 1));
console.log(rows.map(r => `t=${r.t} s=${r.s}`).join('\n'));
await browser.close();
