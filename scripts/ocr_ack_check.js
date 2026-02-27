#!/usr/bin/env node
const { createWorker } = require('tesseract.js');
const fs = require('fs');

function norm(s) {
  return (s || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9\s:]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

(async () => {
  const img = process.argv[2];
  const ack = process.argv[3] || 'ok';
  if (!img || !fs.existsSync(img)) {
    console.log('ACK_FOUND=0');
    console.log('REASON=no_image');
    process.exit(0);
  }

  const worker = await createWorker('eng');
  const { data } = await worker.recognize(img);
  await worker.terminate();

  const t = norm(data.text || '');
  const ackNorm = norm(ack);

  let found = false;

  if (ackNorm === 'ok') {
    const okCount = (t.match(/\bok\b/g) || []).length;
    const hintCount = (t.match(/xac nhan hom nay\s*:?\s*ok/g) || []).length;
    // Incoming standalone "ok" should add extra count beyond reminder hints.
    found = okCount > hintCount;
  } else {
    const esc = ackNorm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    found = new RegExp(`(^|\\s)${esc}($|\\s)`).test(t);
  }

  console.log(`ACK_FOUND=${found ? 1 : 0}`);
  console.log(`OCR_TEXT=${t.slice(0, 800)}`);
})().catch((e) => {
  console.log('ACK_FOUND=0');
  console.log('REASON=ocr_error');
  console.log(String(e.message || e));
});