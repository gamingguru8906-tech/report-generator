// Prints the forecast deck HTML to a 9:16 PDF.
// node render.mjs <in.html> <out.pdf>   -> prints one JSON line: { ok, pages, fit: [...], overflow: [...], ms }
// Chromium comes from @sparticuz/chromium (a self-contained build that needs no system libraries), or from
// CHROME_PATH when that is set. Before printing, any page whose text runs into the footer is scaled down a
// little (flow content only, never the decorations) so that variable-length readings always fit.

import fs from 'node:fs';
import path from 'node:path';
import puppeteer from 'puppeteer-core';

const [, , htmlIn, pdfOut] = process.argv;
const t0 = Date.now();

async function chromePath() {
  if (process.env.CHROME_PATH && fs.existsSync(process.env.CHROME_PATH)) return { exe: process.env.CHROME_PATH, args: [] };
  const chromium = (await import('@sparticuz/chromium')).default;
  return { exe: await chromium.executablePath(), args: chromium.args.filter(a => !a.startsWith('--headless') && !a.startsWith('--window-size')) };
}

const FIT = `(() => {
  const H = 1280, SAFE = H - 66;
  const out = [];
  document.querySelectorAll('section.slide').forEach((s, i) => {
    const flow = [...s.children].filter(el => !el.classList.contains('abs') && !el.classList.contains('foot') && el.tagName !== 'svg' && getComputedStyle(el).position !== 'absolute');
    const bottom = () => {
      const top = s.getBoundingClientRect().top; let b = 0;
      for (const el of flow) { const r = el.getBoundingClientRect(); if (r.height) b = Math.max(b, r.bottom - top); }
      return b;
    };
    let z = 1, b = bottom();
    while (b > SAFE && z > 0.72) { z = Math.round((z - 0.03) * 100) / 100; flow.forEach(el => (el.style.zoom = z)); b = bottom(); }
    out.push({ page: i + 1, zoom: z, bottom: Math.round(b), over: b > SAFE });
  });
  return out;
})()`;

let browser;
try {
  const { exe, args } = await chromePath();
  browser = await puppeteer.launch({
    executablePath: exe, headless: 'shell',
    args: [...new Set([...args, '--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu',
      '--no-zygote', '--single-process', '--disable-extensions', '--mute-audio', '--hide-scrollbars', '--font-render-hinting=none',
      '--disable-features=site-per-process,IsolateOrigins', '--renderer-process-limit=1', '--js-flags=--max-old-space-size=64'])],
    defaultViewport: { width: 720, height: 1280 }, protocolTimeout: 600000
  });
  const page = await browser.newPage();
  page.setDefaultTimeout(600000);
  await page.goto('file://' + path.resolve(htmlIn), { waitUntil: 'load', timeout: 600000 });
  await page.evaluate(() => document.fonts.ready);
  const fit = await page.evaluate(FIT);
  await page.pdf({ path: pdfOut, width: '720px', height: '1280px', printBackground: true, preferCSSPageSize: true, timeout: 600000 });
  await browser.close();
  console.log(JSON.stringify({ ok: true, pages: fit.length, fit: fit.filter(f => f.zoom < 1), overflow: fit.filter(f => f.over), ms: Date.now() - t0 }));
} catch (e) {
  try { await browser?.close(); } catch {}
  console.log(JSON.stringify({ ok: false, error: String(e && e.stack || e) }));
  process.exit(1);
}
