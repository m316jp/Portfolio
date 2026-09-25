// 15秒ショーリールの書き出し。
//   node render.mjs stills 0.5 3.2 ...   → 指定秒のPNGを out/ に保存
//   node render.mjs video                → モーションブラー付きMP4（音声は audio.wav があれば合成）
// 必要なもの: playwright-core, ffmpeg（環境変数 FFMPEG で指定可）, Chromium（環境変数 CHROME で指定可）
import { chromium } from 'playwright-core';
import { spawn } from 'node:child_process';
import { mkdirSync, existsSync, writeFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const OUT = process.env.OUT || path.join(here, '../exports/showreel');
const FFMPEG = process.env.FFMPEG || 'ffmpeg';
const CHROME = process.env.CHROME || undefined;
const FPS = 60, DURATION = 15, SUB = 4, WORKERS = Number(process.env.WORKERS || 4);
const page_url = pathToFileURL(path.join(here, 'showreel.html')).href;
mkdirSync(OUT, { recursive: true });

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await page.goto(page_url);
  await page.waitForFunction('window.READY === true', null, { timeout: 60000 });
  return page;
}
const shot = page => page.locator('#stage').screenshot({ type: 'png', animations: 'disabled', caret: 'initial' });

async function stills(times) {
  const browser = await chromium.launch({ executablePath: CHROME });
  const page = await openPage(browser);
  for (const t of times) {
    await page.evaluate(t => window.render(t), Number(t));
    writeFileSync(path.join(OUT, `still-${String(t).padStart(5, '0')}.png`), await shot(page));
  }
  await browser.close();
}

function run(args) {
  return new Promise((res, rej) => {
    const p = spawn(FFMPEG, args, { stdio: ['pipe', 'inherit', 'inherit'] });
    p.on('exit', c => c === 0 ? res() : rej(new Error('ffmpeg ' + c)));
  });
}

// Each output frame averages SUB sub-frames spread over 0.45 frame (≈160° shutter),
// always starting at the frame time so hard cuts on frame boundaries stay clean.
async function segment(browser, idx, f0, f1) {
  const page = await openPage(browser);
  const file = path.join(OUT, `seg-${idx}.mkv`);
  const ff = spawn(FFMPEG, ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS * SUB), '-c:v', 'png', '-i', '-',
    '-vf', `tmix=frames=${SUB},select='not(mod(n+1\\,${SUB}))',setpts=N/${FPS}/TB`, '-r', String(FPS),
    '-c:v', 'libx264rgb', '-crf', '0', '-preset', 'ultrafast', file], { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise((res, rej) => ff.on('exit', c => c === 0 ? res() : rej(new Error('ffmpeg ' + c))));
  for (let f = f0; f < f1; f++) {
    for (let k = 0; k < SUB; k++) {
      await page.evaluate(t => window.render(t), (f + k * 0.45 / SUB) / FPS);
      const buf = await shot(page);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    }
    if (f % 60 === 0) console.log(`worker ${idx}: frame ${f}`);
  }
  ff.stdin.end();
  await done;
  await page.close();
  return file;
}

async function video() {
  const total = FPS * DURATION, per = Math.ceil(total / WORKERS);
  const browsers = await Promise.all(Array.from({ length: WORKERS }, () => chromium.launch({ executablePath: CHROME })));
  const files = await Promise.all(browsers.map((b, i) => segment(b, i, i * per, Math.min(total, (i + 1) * per))));
  await Promise.all(browsers.map(b => b.close()));
  const list = path.join(OUT, 'segments.txt');
  writeFileSync(list, files.map(f => `file '${f}'`).join('\n'));
  const audio = path.join(here, '../exports/showreel/audio.wav');
  const hasAudio = existsSync(audio);
  const final = path.join(OUT, 'miyazakimari-showreel-2026.mp4');
  await run(['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, ...(hasAudio ? ['-i', audio] : []),
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-tune', 'animation',
    '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-vf', 'scale=out_color_matrix=bt709',
    ...(hasAudio ? ['-c:a', 'aac', '-b:a', '256k', '-shortest'] : []), '-movflags', '+faststart', final]);
  console.log('wrote', final);
}

const [mode, ...rest] = process.argv.slice(2);
if (mode === 'stills') await stills(rest);
else if (mode === 'video') await video();
else console.log('usage: node render.mjs stills <t...> | video');
