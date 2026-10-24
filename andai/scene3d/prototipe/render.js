// Renders scene.html frame by frame in headless Chromium (WebGL on SwiftShader) and pipes JPEGs to ffmpeg.
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');
// Usage: node render.js out.mp4 [seconds=3] [fps=30] [w=1080] [h=1920] [ao=0]
const [,, out, secs = '3', fps = '30', w = '1080', h = '1920', ao = '0'] = process.argv;
(async () => {
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await b.newPage({ viewport: { width: +w, height: +h } });
  await page.route('http://local/**', r => {
    const f = path.join(__dirname, decodeURIComponent(new URL(r.request().url()).pathname));
    r.fulfill({ body: fs.readFileSync(f), contentType: f.endsWith('.js') ? 'text/javascript' : 'text/html' });
  });
  page.on('console', m => console.log('page:', m.text()));
  page.on('pageerror', e => console.log('pageerror:', e.message));
  await page.goto(`http://local/scene.html?w=${w}&h=${h}&ao=${ao}`);
  await page.waitForFunction(() => window.ready === true);
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', fps, '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const n = Math.round(+secs * +fps), t0 = Date.now();
  for (let i = 0; i < n; i++) {
    await page.evaluate(t => window.renderFrame(t), i / +fps);
    const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
    if (i === Math.floor(n / 2)) fs.writeFileSync(out.replace('.mp4', '_mid.jpg'), buf);
    ff.stdin.write(buf);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  console.log(`frames=${n} total=${((Date.now() - t0) / 1000).toFixed(1)}s per_frame=${((Date.now() - t0) / n).toFixed(0)}ms`);
  await b.close();
})();
