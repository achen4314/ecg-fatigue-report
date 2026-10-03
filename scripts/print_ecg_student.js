// print_ecg_student.js — export student-version PDF + 2x PNG
const puppeteer = require('puppeteer-core');

(async () => {
  const exe = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
  const html = 'file:///C:/Users/admin/AppData/Local/Temp/ecg_work/build/report_student.html';
  const outPdf = 'C:/Users/admin/AppData/Local/Temp/ecg_work/build/连晨阳-一周心率与恢复状态报告-学员版.pdf';
  const outPng = 'C:/Users/admin/AppData/Local/Temp/ecg_work/build/连晨阳-一周心率与恢复状态报告-学员版.png';
  const browser = await puppeteer.launch({ executablePath: exe, headless: true,
    args: ['--no-sandbox', '--disable-gpu', '--allow-file-access-from-files'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 750, height: 1200, deviceScaleFactor: 2 });
  await page.goto(html, { waitUntil: 'networkidle0', timeout: 120000 });
  await page.evaluate(() => document.fonts.ready);
  await new Promise(r => setTimeout(r, 1200));
  await page.screenshot({ path: outPng, fullPage: true, type: 'png', captureBeyondViewport: true });
  console.log('png ok');
  await page.pdf({ path: outPdf, format: 'A4', printBackground: true,
    margin: { top: '10mm', bottom: '10mm', left: '6mm', right: '6mm' } });
  console.log('pdf ok');
  await browser.close();
})().catch(e => { console.error('FAIL', e.message); process.exit(1); });
