"""Assemble the page.
  build/index.html  - render/dev build (fonts inline; eye photo + audio as files in build/assets)
  web/eye4u.html    - web build: ONE self-contained file (fonts, eye photo and soundtrack inlined), for offline use
  web/eyeforyou/player/ - web build for hosting: small page + the soundtrack as its own file (tools/site.py wraps it)
Both carry the same scenes and the same pure seek(t). The player UI only runs in a normal
browser; under Playwright (navigator.webdriver) or with ?render the page is a bare 1080p stage."""
import base64, json, pathlib, shutil, urllib.parse
R = pathlib.Path(__file__).resolve().parent.parent
src = R / 'src'
order = ['timeline.js', 'fits.js', 'core.js', 'prims.js', 'scene_intro.js', 'scene_hub.js', 'scene_special.js',
         'scene_showroom.js', 'scene_info.js', 'cursor.js', 'main.js']
shapes = json.loads((R / 'analysis' / 'shapes.json').read_text())
js = ['const SHAPES = ' + json.dumps(shapes) + ';']
for f in order:
    p = src / f
    if p.exists():
        js.append(f'// ===== {f} =====\n' + p.read_text())
ENGINE = '\n'.join(js).replace('let ROOT, OVER, PENDING = [];', "let ROOT = document.getElementById('root'), OVER = document.getElementById('over'), PENDING = [];")

PLAYER_CSS = r"""
#ui{position:fixed;inset:0;z-index:10;pointer-events:none;font-family:Barlow,system-ui,-apple-system,sans-serif;color:#fff;user-select:none;-webkit-user-select:none}
body.idle,body.idle *{cursor:none!important}
#big{pointer-events:auto;position:absolute;left:50%;top:71%;width:112px;height:112px;margin:-56px 0 0 -56px;border:0;border-radius:50%;
  background:#F15D08;color:#fff;cursor:pointer;display:grid;place-items:center;box-shadow:0 10px 40px rgba(0,0,0,.35);transition:transform .15s ease}
#big:hover{transform:scale(1.06)}
#big svg{width:44px;height:44px;margin-left:6px}
#big[hidden]{display:none}
#bar{pointer-events:auto;position:absolute;left:0;right:0;bottom:0;display:flex;align-items:center;gap:14px;padding:30px 22px 16px;
  background:linear-gradient(to top,rgba(0,0,0,.72),rgba(0,0,0,0));transition:opacity .35s ease}
body.idle #bar{opacity:0;pointer-events:none}
#bar button{flex:none;width:40px;height:40px;border:0;border-radius:8px;background:transparent;color:#fff;cursor:pointer;display:grid;place-items:center}
#bar button:hover{background:rgba(255,255,255,.14)}
#bar button:focus-visible,#big:focus-visible,#scrub:focus-visible{outline:2px solid #fff;outline-offset:2px}
#bar svg{width:22px;height:22px}
#time{flex:none;font-variant-numeric:tabular-nums;font-size:15px;font-weight:600;letter-spacing:.02em;min-width:92px;opacity:.92}
#scrub{flex:1;min-width:60px;margin:0;-webkit-appearance:none;appearance:none;height:22px;background:transparent;cursor:pointer;--p:0%}
#scrub::-webkit-slider-runnable-track{height:5px;border-radius:3px;background:linear-gradient(to right,#F15D08 var(--p),rgba(255,255,255,.3) var(--p))}
#scrub::-moz-range-track{height:5px;border-radius:3px;background:rgba(255,255,255,.3)}
#scrub::-moz-range-progress{height:5px;border-radius:3px;background:#F15D08}
#scrub::-webkit-slider-thumb{-webkit-appearance:none;width:15px;height:15px;margin-top:-5px;border-radius:50%;background:#fff;border:0}
#scrub::-moz-range-thumb{width:15px;height:15px;border-radius:50%;background:#fff;border:0}
#load{position:absolute;left:50%;top:calc(71% + 80px);transform:translateX(-50%);font-size:14px;opacity:.7;letter-spacing:.05em;color:#555}
@media (max-width:600px){#bar{gap:6px;padding:24px 8px 8px}#time{min-width:0;font-size:12px}#big{width:84px;height:84px;margin:-42px 0 0 -42px}#big svg{width:34px;height:34px}}
"""

PLAYER_HTML = r"""
<div id="ui">
  <button id="big" aria-label="Play"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 4.5v15l12.5-7.5z"/></svg></button>
  <div id="load">loading…</div>
  <div id="bar">
    <button id="pp" aria-label="Play"><svg viewBox="0 0 24 24" fill="currentColor"><path id="ppicon" d="M7 4.5v15l12.5-7.5z"/></svg></button>
    <span id="time">0:00 / 1:24</span>
    <input id="scrub" type="range" min="0" max="84.867" step="0.001" value="0" aria-label="Position">
    <button id="fs" aria-label="Full screen"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg></button>
  </div>
</div>
"""

PLAYER_JS = r"""
// ---------------------------------------------------------------------------
// Web player. seek(t) stays a pure function of time; this wrapper only decides t.
// Sound: the track is decoded once and played through Web Audio, so a seek is instant and
// exact on any server. Picture: a performance.now() clock (smooth, sub-ms) slaved to the time
// the listener actually hears (AudioContext.getOutputTimestamp, output latency included).
// Small drift is absorbed by nudging the clock rate by at most 1 %, so the picture never jumps.
// ---------------------------------------------------------------------------
(function () {
  const ui = document.getElementById('ui');
  if (navigator.webdriver || /render/.test(location.search)) { ui.remove(); return; }
  const DUR = window.DURATION, POSTER = 12, st = document.getElementById('stage'), body = document.body;
  const $ = id => document.getElementById(id);
  const big = $('big'), pp = $('pp'), icon = $('ppicon'), scrub = $('scrub'), timeEl = $('time'), fsBtn = $('fs'), load = $('load');
  const PLAY = 'M7 4.5v15l12.5-7.5z', PAUSE = 'M6.5 4.5h4v15h-4zM13.5 4.5h4v15h-4z';
  scrub.max = DUR;
  document.documentElement.style.cssText = 'height:100%;background:#000';
  body.style.cssText = 'margin:0;height:100%;background:#000;overflow:hidden';
  const fit = () => {                                   // letterbox the 1920x1080 stage into any window
    const k = Math.min(innerWidth / 1920, innerHeight / 1080);
    Object.assign(st.style, { position: 'absolute', transformOrigin: '0 0', transform: `scale(${k})`,
      left: (innerWidth - 1920 * k) / 2 + 'px', top: (innerHeight - 1080 * k) / 2 + 'px' });
  };
  fit(); addEventListener('resize', fit);

  // ---- sound ------------------------------------------------------------------------------
  const SRC = window.AUDIO_SRC || 'assets/eye4u.m4a';
  try { if (navigator.audioSession) navigator.audioSession.type = 'playback'; } catch (e) {}   // iOS: play with the silent switch on
  const snd = (() => {
    const AC = window.AudioContext || window.webkitAudioContext;
    let ctx = null, buf = null, node = null, when = 0, from = 0, el = null;
    try { ctx = AC ? new AC({ latencyHint: 'playback' }) : null; } catch (e) { ctx = null; }   // created now, resumed on a gesture
    const ready = (async () => {
      try {
        if (!ctx) throw new Error('no Web Audio');
        const ab = await (await fetch(SRC)).arrayBuffer();
        buf = await new Promise((ok, no) => { const p = ctx.decodeAudioData(ab, ok, no); if (p && p.catch) p.catch(no); });
      } catch (e) {                                     // fall back to a media element (e.g. fetch blocked on file://)
        buf = null; el = new Audio(SRC); el.preload = 'auto';
      }
    })();
    const heardCtx = () => {                            // context time reaching the speakers right now
      const ts = ctx.getOutputTimestamp && ctx.getOutputTimestamp();
      if (ts && ts.performanceTime > 0) return ts.contextTime + (performance.now() - ts.performanceTime) / 1000;
      return ctx.currentTime - (ctx.outputLatency || ctx.baseLatency || 0);
    };
    return {
      ready,
      get exact() { return !!buf; },
      unlock() { if (ctx && ctx.state !== 'running') ctx.resume().catch(() => {}); },   // call inside a user gesture
      async start(t) {                                  // play from t; resolves to ms until t is heard
        this.stop();
        if (buf) {
          if (ctx.state !== 'running') await ctx.resume();
          node = ctx.createBufferSource(); node.buffer = buf; node.connect(ctx.destination);
          when = ctx.currentTime + 0.05; from = t;
          node.start(when, Math.min(t, buf.duration));
          return Math.max(0, (when - heardCtx()) * 1000);
        }
        if (el) { try { el.currentTime = t; await el.play(); } catch (e) {} }
        return 0;
      },
      stop() {
        if (node) { try { node.stop(); } catch (e) {} node.disconnect(); node = null; }
        if (el && !el.paused) el.pause();
      },
      heard() {                                         // media time being heard, or null if silent
        if (node) return from + (heardCtx() - when);
        if (el && !el.paused && !el.seeking) return el.currentTime;
        return null;
      },
    };
  })();

  // ---- clock ------------------------------------------------------------------------------
  let playing = false, started = false, dragging = false, resumeAfterDrag = false, starting = null;
  let anchorT = 0, anchorNow = 0, rate = 1, lastSync = 0;
  const now = () => performance.now();
  const clock = () => (playing ? anchorT + (Math.max(0, now() - anchorNow) / 1000) * rate : anchorT);
  const reanchor = (t, r = 1, lead = 0) => { anchorT = t; anchorNow = now() + lead; rate = r; };
  function sync() {
    const n = now();
    if (n < anchorNow + 150 || n - lastSync < 200) return;
    lastSync = n;
    const h = snd.heard(); if (h === null) return;
    const t = clock(), err = h - t;
    if (Math.abs(err) > (snd.exact ? 0.12 : 0.3)) reanchor(h);                    // after stalls: snap
    else reanchor(t, 1 + Math.max(-0.01, Math.min(0.01, err * 0.5)));           // otherwise glide
  }

  let busy = false, want = null;                        // never overlap seeks; always land on the newest t
  async function draw(t) {
    want = t; if (busy) return; busy = true;
    while (want !== null) { const x = want; want = null; await window.seek(x); }
    busy = false;
  }
  const fmt = t => { t = Math.max(0, t); return `${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, '0')}`; };
  function paint(t) {
    timeEl.textContent = `${fmt(t)} / ${fmt(DUR)}`;
    if (!dragging) scrub.value = t;
    scrub.style.setProperty('--p', ((t / DUR) * 100).toFixed(3) + '%');
  }
  function frame() {
    if (!playing) return;
    sync();
    const t = clock();
    if (t >= DUR) { draw(DUR); paint(DUR); stop(true); return; }
    draw(t); paint(t);
    requestAnimationFrame(frame);
  }

  // ---- transport --------------------------------------------------------------------------
  function play() {
    snd.unlock();                                       // synchronously, while we are still inside the gesture
    if (playing || starting) return starting;
    started = true; big.hidden = true;
    if (anchorT >= DUR - 0.02) anchorT = 0;
    starting = (async () => {
      await window.ready;
      if (load.isConnected) load.textContent = 'loading sound…';
      await snd.ready;
      const t0 = anchorT, lead = await snd.start(t0);
      reanchor(t0, 1, lead); playing = true; lastSync = 0;
      icon.setAttribute('d', PAUSE); pp.setAttribute('aria-label', 'Pause');
      poke(); requestAnimationFrame(frame);
      starting = null;
    })();
    return starting;
  }
  function stop(ended) {
    if (!playing) return;
    const t = ended ? DUR : clock();
    playing = false; snd.stop(); reanchor(t);
    icon.setAttribute('d', PLAY); pp.setAttribute('aria-label', 'Play');
    if (ended) big.hidden = false;
    poke();
  }
  const toggle = () => (playing ? stop() : play());
  async function jump(t) {
    started = true; big.hidden = true;
    t = Math.min(DUR, Math.max(0, t));
    draw(t); paint(t);
    if (!playing) { reanchor(t); return; }
    reanchor(t, 1, 1e6);                                // hold the picture at t until the sound is there
    const lead = await snd.start(t);
    reanchor(t, 1, lead); lastSync = 0;
  }

  big.addEventListener('click', e => { e.stopPropagation(); play(); });
  pp.addEventListener('click', e => { e.stopPropagation(); toggle(); });
  $('bar').addEventListener('click', e => e.stopPropagation());
  document.addEventListener('click', () => { if (started) toggle(); });   // click the picture to pause/resume
  scrub.addEventListener('input', () => {
    if (!dragging) { dragging = true; resumeAfterDrag = playing; stop(); }
    started = true; big.hidden = true; reanchor(+scrub.value); draw(+scrub.value); paint(+scrub.value);
  });
  scrub.addEventListener('change', () => {
    dragging = false; reanchor(+scrub.value); paint(+scrub.value);
    if (resumeAfterDrag) { resumeAfterDrag = false; play(); }
  });
  fsBtn.addEventListener('click', e => {
    e.stopPropagation();
    const d = document, el = d.documentElement;
    if (d.fullscreenElement || d.webkitFullscreenElement) (d.exitFullscreen || d.webkitExitFullscreen).call(d);
    else (el.requestFullscreen || el.webkitRequestFullscreen)?.call(el);
  });
  addEventListener('keydown', e => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    snd.unlock();
    if (e.code === 'Space' || e.key === 'k') { e.preventDefault(); toggle(); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); jump(clock() - 5); }
    else if (e.key === 'ArrowRight') { e.preventDefault(); jump(clock() + 5); }
    else if (e.key === 'f') fsBtn.click();
    else if (e.key === 'Home' || e.key === '0') { e.preventDefault(); jump(0); }
    else return;
    poke();
  });

  let hideTimer = 0;                                    // controls auto-hide while playing
  function poke() {
    body.classList.remove('idle'); clearTimeout(hideTimer);
    hideTimer = setTimeout(() => { if (playing && !dragging) body.classList.add('idle'); }, 2200);
  }
  addEventListener('mousemove', poke); addEventListener('touchstart', poke, { passive: true });

  // scripting handle for embedding: player.play(), player.pause(), player.seek(t), player.time
  window.player = { play, pause: () => stop(), seek: t => jump(t), get time() { return clock(); }, get playing() { return playing; },
    heard: () => snd.heard(), get exact() { return snd.exact; } };
  window.ready.then(async () => { await window.seek(POSTER); paint(0); });
  Promise.all([window.ready, snd.ready]).then(() => load.remove());
})();
"""


ICON = ("data:image/svg+xml," + urllib.parse.quote('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-40 -40 80 80">'
        '<ellipse rx="38" ry="20" fill="#F15D08"/><ellipse cx="-1" rx="26" ry="11" fill="#fff"/>'
        '<circle cx="-2" r="13" fill="#C0000E"/></svg>'))


def page(eye_src=None, audio_src=None, title='EYE4U, rebuilt'):
    pre = ''
    if eye_src: pre += f"window.EYE_SRC = {json.dumps(eye_src)};\n"
    if audio_src: pre += f"window.AUDIO_SRC = {json.dumps(audio_src)};\n"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="The 1998 EYE4U Flash intro, rebuilt frame by frame as live SVG, locked to its soundtrack.">
<meta property="og:title" content="{title}">
<meta property="og:description" content="The 1998 EYE4U Flash intro, rebuilt frame by frame as live SVG.">
<link rel="icon" href="{ICON}">
<style>
{(src / 'fonts.css').read_text()}
html,body{{margin:0;padding:0;background:#000;overflow:hidden}}
#stage{{position:relative;width:1920px;height:1080px;overflow:hidden;background:#fff}}
#sv{{position:absolute;left:0;top:0;display:block}}
text{{font-kerning:normal;text-rendering:geometricPrecision}}
{PLAYER_CSS}
</style></head>
<body>
<div id="stage"><svg id="sv" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 854 480" width="1920" height="1080" preserveAspectRatio="none"><g id="root"></g><g id="over"></g></svg></div>
{PLAYER_HTML}
<script>
{pre}{ENGINE}
</script>
<script>{PLAYER_JS}</script>
</body></html>
"""


out = R / 'build' / 'index.html'
out.write_text(page())
print(out, out.stat().st_size // 1024, 'KB')

# single-file web build
b64 = lambda p, mime: f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()
eye = R / 'build' / 'assets' / 'eye' / 'eye_00.jpg'
aud = R / 'build' / 'assets' / 'eye4u.m4a'
(R / 'web').mkdir(exist_ok=True)
web = R / 'web' / 'eye4u.html'
web.write_text(page(b64(eye, 'image/jpeg'), b64(aud, 'audio/mp4')))
print(web, web.stat().st_size // 1024, 'KB')

# hosted build: page (~0.5 MB) paints the poster at once while the audio loads alongside it
site = R / 'web' / 'eyeforyou' / 'player'          # the case-study page (tools/site.py) frames this
if site.exists(): shutil.rmtree(site)
(site / 'assets' / 'eye').mkdir(parents=True)
shutil.copy(eye, site / 'assets' / 'eye' / 'eye_00.jpg')
shutil.copy(aud, site / 'assets' / 'eye4u.m4a')
(site / 'index.html').write_text(page())
print(site, sum(f.stat().st_size for f in site.rglob('*') if f.is_file()) // 1024, 'KB')
