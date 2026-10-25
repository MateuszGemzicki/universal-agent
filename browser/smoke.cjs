const { chromium } = require('playwright');
(async () => {
  const url = process.argv[2] || 'http://localhost:3000';
  if (!/^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?(\/|$)/.test(url)) throw new Error('Only localhost browser smoke URLs are permitted');
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', err => errors.push(String(err)));
    const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    console.log(JSON.stringify({ url, title: await page.title(), status: response?.status(), errors }, null, 2));
    if (!response || response.status() >= 400 || errors.length) process.exitCode = 1;
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
