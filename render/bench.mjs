import { chromium } from 'playwright';
import path from 'node:path'; import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url));
const browser = await chromium.launch({ executablePath: process.env.PW_CHROME || '/Users/marcelojansson/Library/Caches/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-mac-arm64/chrome-headless-shell' });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
page.on('pageerror', e => console.error('PAGE ERROR', e.message));
await page.goto('file://' + path.join(here, '..', 'build', 'index.html'));
await page.evaluate(() => window.ready);
for (const type of ['jpeg', 'png']) {
  const t0 = Date.now(); let bytes = 0;
  for (let i = 0; i < 40; i++) {
    await page.evaluate(t => window.seek(t), 30 + i / 60);
    const b = await page.screenshot({ type, quality: type === 'jpeg' ? 100 : undefined, clip: { x: 0, y: 0, width: 1920, height: 1080 } });
    bytes += b.length;
  }
  console.log(type, ((Date.now() - t0) / 40).toFixed(1), 'ms/frame', (bytes / 40 / 1024).toFixed(0), 'KB');
}
await browser.close();
