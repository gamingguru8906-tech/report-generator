// Renders the summary card HTML (one 720x1280 slide) to a 1080x1920 PNG for WhatsApp.
// node card.mjs <in.html> <out.png>   -> prints one JSON line: { ok, ms } or { ok: false, error }
import fs from 'node:fs';
import path from 'node:path';
import puppeteer from 'puppeteer-core';

const [, , htmlIn, pngOut] = process.argv;
const t0 = Date.now();

async function chromePath() {
  if (process.env.CHROME_PATH && fs.existsSync(process.env.CHROME_PATH)) return { exe: process.env.CHROME_PATH, args: [] };
  const chromium = (await import('@sparticuz/chromium')).default;
  return { exe: await chromium.executablePath(), args: chromium.args.filter(a => !a.startsWith('--headless') && !a.startsWith('--window-size')) };
}

let browser;
try {
  const { exe, args } = await chromePath();
  browser = await puppeteer.launch({
    executablePath: exe, headless: 'shell',
    args: [...new Set([...args, '--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu',
      '--no-zygote', '--single-process', '--disable-extensions', '--mute-audio', '--hide-scrollbars', '--font-render-hinting=none',
      '--renderer-process-limit=1', '--js-flags=--max-old-space-size=64'])],
    defaultViewport: { width: 720, height: 1280, deviceScaleFactor: 1.5 }, protocolTimeout: 240000
  });
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(htmlIn), { waitUntil: 'load', timeout: 240000 });
  await page.evaluate(() => document.fonts.ready);
  // A long line can run into the bottom: shrink the flow a little until it fits (like the PDF does).
  await page.evaluate(() => {
    const s = document.querySelector('section.slide'); if (!s) return;
    const flow = [...s.children].filter(el => getComputedStyle(el).position !== 'absolute');
    const bottom = () => Math.max(...flow.map(el => el.getBoundingClientRect().bottom), 0) - s.getBoundingClientRect().top;
    let z = 1;
    while (bottom() > 1240 && z > 0.75) { z = Math.round((z - 0.03) * 100) / 100; flow.forEach(el => (el.style.zoom = z)); }
  });
  const el = await page.$('section.slide');
  await (el || page).screenshot({ path: pngOut, type: 'png' });
  await browser.close();
  console.log(JSON.stringify({ ok: true, ms: Date.now() - t0 }));
} catch (e) {
  try { await browser?.close(); } catch {}
  console.log(JSON.stringify({ ok: false, error: String(e && e.stack || e) }));
  process.exit(1);
}
