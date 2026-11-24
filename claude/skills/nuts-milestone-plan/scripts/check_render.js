// 正本の HTML を headless Chrome で開き、帯・項目一覧・根拠のパネル・タブが動くかと JS エラーの有無を出す。
// 使い方: NODE_PATH=<playwright を持つ node_modules> node check_render.js <正本.html>
const pw = require('playwright');
(async () => {
  const file = process.argv[2];
  const browser = await pw.chromium.launch({ channel: 'chrome' }).catch(() => pw.chromium.launch());
  const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
  const errs = [];
  page.on('pageerror', (e) => errs.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
  await page.goto('file://' + file);
  await page.waitForTimeout(500);
  const info = await page.evaluate(() => ({
    options: [...document.querySelectorAll('#plan-select option')].map((o) => o.textContent),
    bars: document.querySelectorAll('#gantt .bar').length,
    keyedBars: document.querySelectorAll('#gantt .bar[data-key]').length,
    matrixHits: document.querySelectorAll('#matrix .hit[data-key]').length,
    items: document.querySelectorAll('#items tr[data-key]').length,
    h2: [...document.querySelectorAll('h2')].filter((h) => h.offsetParent !== null).map((h) => h.textContent),
    hash: location.hash,
  }));
  console.log(JSON.stringify(info, null, 1));
  // 帯を押すとパネルが開く
  await page.click('#gantt .bar[data-key="NTMS-44"]');
  await page.waitForTimeout(250);
  const p1 = await page.evaluate(() => ({ open: document.querySelector('.panel').classList.contains('open'), title: document.querySelector('.panel h3')?.textContent, epics: document.querySelectorAll('.panel table tr').length, notes: document.querySelectorAll('.panel ul li').length }));
  console.log('panel after bar click:', JSON.stringify(p1));
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);
  // 1 の図を押す
  await page.click('#matrix .hit[data-key="NTMS-35"]');
  await page.waitForTimeout(250);
  const p2 = await page.evaluate(() => document.querySelector('.panel h3')?.textContent);
  console.log('panel after matrix click:', p2);
  // 根拠タブ
  await page.click('.tab[data-tab="basis"]');
  await page.waitForTimeout(250);
  const b = await page.evaluate(() => ({ panelOpen: document.querySelector('.panel').classList.contains('open'), h2: [...document.querySelectorAll('h2')].filter((h) => h.offsetParent !== null).map((h) => h.textContent) }));
  console.log('basis tab:', JSON.stringify(b));
  await page.click('#items tr[data-key="NTMS-43"]');
  await page.waitForTimeout(250);
  console.log('panel after row click:', await page.evaluate(() => document.querySelector('.panel h3')?.textContent));
  await page.setViewportSize({ width: 400, height: 800 });
  await page.waitForTimeout(200);
  console.log('phone overflow:', await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth));
  await page.screenshot({ path: process.argv[3] || '/dev/null', fullPage: false }).catch(() => {});
  console.log('errors:', errs);
  await browser.close();
})().catch((e) => { console.error('FAIL', e.message); process.exit(1); });
