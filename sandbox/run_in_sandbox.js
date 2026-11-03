// Открывает ссылки из shares.json в песочнице qumir.dev, нажимает «Запустить» и сохраняет снимки до и после.
// Запуск: npm i playwright && npx playwright install chromium && node sandbox/run_in_sandbox.js <папка-для-снимков>
const { chromium } = require('playwright');
const fs = require('fs');
const shares = JSON.parse(fs.readFileSync(require('path').join(__dirname, 'shares.json'), 'utf8'));
const out = process.argv[2];
(async () => {
  const b = await chromium.launch();
  for (const [key, s] of Object.entries(shares)) {
    const pg = await b.newPage({ viewport: { width: 1500, height: 950 } });
    await pg.goto('https://qumir.dev/s/' + s.id, { waitUntil: 'networkidle', timeout: 90000 });
    await pg.waitForTimeout(2500);
    await pg.screenshot({ path: `${out}/${key}_before.png` });
    await pg.click('#btn-run');
    // ждём, пока робот закончит: кнопка Стоп снова неактивна или статус сменился
    let status = '';
    for (let i = 0; i < 120; i++) {
      await pg.waitForTimeout(500);
      status = await pg.evaluate(() => {
        const st = document.getElementById('status'); const stop = document.getElementById('btn-stop');
        return (st ? st.innerText : '') + ' | stop.disabled=' + (stop ? stop.disabled : '?');
      });
      if (i > 4 && /stop.disabled=true/.test(status)) break;
    }
    await pg.waitForTimeout(1500);
    const errs = await pg.evaluate(() => { const e = document.querySelector('#errors, .errors, #stderr'); return e ? e.innerText.slice(0, 300) : ''; });
    await pg.screenshot({ path: `${out}/${key}_after.png` });
    console.log(key, '|', status.replace(/\s+/g, ' ').slice(0, 160), '| ошибки:', errs.replace(/\s+/g, ' ').slice(0, 200));
    await pg.close();
  }
  await b.close();
})();
