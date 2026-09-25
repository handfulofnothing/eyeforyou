// Full render: node render.mjs [workers] [fromFrame] [toFrame]
// Each output frame = mean of NSUB subframes spanning t - 1/240 .. t + 1/240 (180 degree shutter),
// shot with Playwright and blended by ffmpeg tmix, 60 fps, 1920x1080.
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(here, '..');
const FPS = 60, NSUB = +(process.env.NSUB || 9);
// NSUB subframes evenly across the same 180-degree shutter window (t - 1/240 .. t + 1/240)
const SUB = Array.from({ length: NSUB }, (_, i) => (NSUB === 1 ? 0 : -1 / 240 + (i * 2) / 240 / (NSUB - 1)));
const DUR = 84.867;
const TOTAL = Math.floor(DUR * FPS);          // 5092 frames
const workers = +(process.argv[2] || 6);
const from = +(process.argv[3] || 0), to = +(process.argv[4] || TOTAL);
const outDir = path.join(root, 'out', 'chunks');
fs.mkdirSync(outDir, { recursive: true });
const exe = process.env.PW_CHROME || '/Users/marcelojansson/Library/Caches/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-mac-arm64/chrome-headless-shell';

function ffmpegFor(file) {
  const w = Array(NSUB).fill('1').join(' ');
  const vf = `tmix=frames=${NSUB}:weights='${w}',select='eq(mod(n\\,${NSUB})\\,${NSUB - 1})',setpts=N/(60*TB),scale=out_color_matrix=bt709:out_range=tv,format=yuv420p`;
  return spawn('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(60 * NSUB), '-c:v', 'png', '-i', '-',
    '-vf', vf, '-r', '60', '-c:v', 'libx264', '-preset', 'medium', '-crf', '12', '-g', '120',
    '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', file], { stdio: ['pipe', 'inherit', 'inherit'] });
}

async function run(w, a, b) {
  const browser = await chromium.launch({ executablePath: exe });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error(`[w${w}] PAGE ERROR`, e.message));
  await page.goto('file://' + path.join(root, 'build', 'index.html'));
  await page.evaluate(() => window.ready);
  const file = path.join(outDir, `chunk_${String(w).padStart(2, '0')}.mp4`);
  const ff = ffmpegFor(file);
  const done = new Promise((res, rej) => ff.on('close', c => (c === 0 ? res() : rej(new Error('ffmpeg ' + c)))));
  const t0 = Date.now();
  for (let i = a; i < b; i++) {
    for (const d of SUB) {
      const t = Math.min(DUR, Math.max(0, i / FPS + d));
      await page.evaluate(t => window.seek(t), t);
      const png = await page.screenshot({ type: 'png', clip: { x: 0, y: 0, width: 1920, height: 1080 } });
      if (!ff.stdin.write(png)) await new Promise(r => ff.stdin.once('drain', r));
    }
    if ((i - a) % 300 === 0) console.log(`[w${w}] frame ${i} (${(((i - a) / (b - a)) * 100).toFixed(0)}%) ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end();
  await done;
  await browser.close();
  return file;
}

const n = to - from, per = Math.ceil(n / workers), jobs = [];
for (let w = 0; w < workers; w++) {
  const a = from + w * per, b = Math.min(to, a + per);
  if (a < b) jobs.push(run(w, a, b));
}
const files = await Promise.all(jobs);
fs.writeFileSync(path.join(outDir, 'list.txt'), files.map(f => `file '${f}'`).join('\n') + '\n');
console.log('chunks done:', files.length);
