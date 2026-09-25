// ---------------------------------------------------------------------------
// EYE4U rebuild - core. Every visual property is a pure function of time.
// Authoring happens in SOURCE time (seconds of the 1998 capture); seek(t)
// warps rebuild time -> source time through the storyboard anchors (WARP),
// so each event's source moment lands on its snapped beat.
// Design space is the capture's 854x480; the SVG viewBox scales it to 1080p.
// ---------------------------------------------------------------------------
const NS = 'http://www.w3.org/2000/svg';
const DUR = 84.867;
const W = 854, H = 480;

const C = {
  orange: '#F15D08', red: '#B90002', mint: '#14E398', green: '#10EA37', cyan: '#14DCFC',
  paleCyan: '#6FE8FC', peach: '#F5A679', peachLight: '#FDD4C1', teal1: '#12B1C8', teal2: '#0D8495',
  teal3: '#095863', teal4: '#063138', label: '#5D5D63', labelDim: '#C9C9CE', ink: '#141414',
  watermark: '#E2E0E5', logoRed: '#B5000C', logoOrange: '#EC6A1C', white: '#FFFFFF', black: '#000000',
};

// ---- math -----------------------------------------------------------------
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, t) => a + (b - a) * t;
const inv = (a, b, x) => clamp((x - a) / (b - a));
const EASE = {
  lin: t => t,
  i: t => t * t * t, o: t => 1 - Math.pow(1 - t, 3),
  io: t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  i2: t => t * t, o2: t => 1 - (1 - t) * (1 - t),
  io2: t => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2),
  back: t => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
  pop: t => (t <= 0 ? 0 : t >= 1 ? 1 : 1 + 0.22 * Math.sin(Math.PI * t) * (1 - t) * 2.2 - (1 - t) * (1 - t) * (1 - t)),
  step: t => (t >= 1 ? 1 : 0),
};
const rad = d => (d * Math.PI) / 180;

// keyframe track: keys = [[t, value, ease?], ...]; value: number | array | '#rrggbb'.
// Numbers/arrays use cubic Hermite with Bessel tangents: C1-smooth, velocity carries through
// every key (no stop-and-go). mono=true uses PCHIP (no overshoot) for fitted monotone data.
// Ends ease into the held values (zero velocity) unless free=true (fitted camera paths).
// A key with an explicit ease name uses that ease for the segment ending at it.
function besselSlopes(ts, vs) {
  const n = ts.length, d = [], m = new Array(n).fill(0);
  for (let i = 0; i < n - 1; i++) d.push((vs[i + 1] - vs[i]) / (ts[i + 1] - ts[i] || 1e-9));
  if (n === 2) return [d[0], d[0]];
  for (let i = 1; i < n - 1; i++) { const h0 = ts[i] - ts[i - 1], h1 = ts[i + 1] - ts[i]; m[i] = (h1 * d[i - 1] + h0 * d[i]) / (h0 + h1); }
  // natural-ish ends: continue the neighbouring curvature
  m[0] = 1.5 * d[0] - 0.5 * m[1]; m[n - 1] = 1.5 * d[n - 2] - 0.5 * m[n - 2];
  return m;
}
function pchipSlopes(ts, vs) {
  const n = ts.length, d = [], m = new Array(n).fill(0);
  for (let i = 0; i < n - 1; i++) d.push((vs[i + 1] - vs[i]) / (ts[i + 1] - ts[i] || 1e-9));
  if (n === 2) return [d[0], d[0]];
  for (let i = 1; i < n - 1; i++) {
    if (d[i - 1] * d[i] <= 0) { m[i] = 0; continue; }
    const h0 = ts[i] - ts[i - 1], h1 = ts[i + 1] - ts[i], w1 = 2 * h1 + h0, w2 = h1 + 2 * h0;
    m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i]);
  }
  const end = (h0, h1, d0, d1) => { let v = ((2 * h0 + h1) * d0 - h0 * d1) / (h0 + h1); if (v * d0 <= 0) v = 0; else if (d0 * d1 <= 0 && Math.abs(v) > Math.abs(3 * d0)) v = 3 * d0; return v; };
  m[0] = end(ts[1] - ts[0], ts[2] - ts[1], d[0], d[1]);
  m[n - 1] = end(ts[n - 1] - ts[n - 2], ts[n - 2] - ts[n - 3], d[n - 2], d[n - 3]);
  return m;
}
const _slopeCache = new WeakMap();
function track(keys, s, logScale = false, mono = false, free = false) {
  if (s <= keys[0][0]) return keys[0][1];
  const n = keys.length;
  if (s >= keys[n - 1][0]) return keys[n - 1][1];
  let i = 0;
  while (i < n - 2 && s >= keys[i + 1][0]) i++;
  const [t0, v0] = keys[i], [t1, v1, e] = keys[i + 1];
  const u = clamp((s - t0) / (t1 - t0));
  if (typeof v0 === 'string') return mixColor(v0, v1, (EASE[e || 'lin'])(u));
  if (e) return mixAny(v0, v1, EASE[e](u), logScale);
  // PCHIP per component (log domain for scales)
  let cache = _slopeCache.get(keys);
  const key = (logScale ? 'log' : 'lin') + (mono ? 'M' : 'B') + (free ? 'F' : 'H');
  if (!cache) { cache = {}; _slopeCache.set(keys, cache); }
  if (!cache[key]) {
    const ts = keys.map(k => k[0]);
    const comps = Array.isArray(v0) ? v0.length : 1;
    cache[key] = [];
    for (let c = 0; c < comps; c++) {
      const vs = keys.map(k => { const v = Array.isArray(k[1]) ? k[1][c] : k[1]; return logScale ? Math.log(v) : v; });
      const m = mono ? pchipSlopes(ts, vs) : besselSlopes(ts, vs);
      if (!free) { m[0] = 0; m[m.length - 1] = 0; }     // ease into / out of the held values
      cache[key].push({ vs, m });
    }
  }
  const h = t1 - t0, h00 = 2 * u ** 3 - 3 * u ** 2 + 1, h10 = u ** 3 - 2 * u ** 2 + u, h01 = -2 * u ** 3 + 3 * u ** 2, h11 = u ** 3 - u ** 2;
  const out = cache[key].map(({ vs, m }) => {
    const y = h00 * vs[i] + h10 * h * m[i] + h01 * vs[i + 1] + h11 * h * m[i + 1];
    return logScale ? Math.exp(y) : y;
  });
  return Array.isArray(v0) ? out : out[0];
}
function mixAny(a, b, p, logScale) {
  if (typeof a === 'number') return logScale ? Math.exp(lerp(Math.log(a), Math.log(b), p)) : lerp(a, b, p);
  if (typeof a === 'string') return mixColor(a, b, p);
  return a.map((v, k) => (typeof v === 'string' ? mixColor(v, b[k], p) : lerp(v, b[k], p)));
}
function hexRgb(h) { const x = parseInt(h.slice(1), 16); return [(x >> 16) & 255, (x >> 8) & 255, x & 255]; }
function mixColor(a, b, p) {
  const A = hexRgb(a), B = hexRgb(b);
  const r = A.map((v, k) => Math.round(lerp(v, B[k], clamp(p))));
  return '#' + r.map(v => v.toString(16).padStart(2, '0')).join('');
}
// deterministic pseudo-random
function rng(seed) { let s = seed >>> 0; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }

// ---- time warp (rebuild t -> source s) ---------------------------------------
// Dense minimum-curvature warp (tools/smooth_warp.py): speed changes are C2-smooth.
function warp(t) {
  const x = clamp(t / WARP_STEP, 0, WARP_S.length - 1), k = Math.min(WARP_S.length - 2, Math.floor(x)), f = x - k;
  // Catmull-Rom on the dense grid keeps the warp C1 between samples too
  const p0 = WARP_S[Math.max(0, k - 1)], p1 = WARP_S[k], p2 = WARP_S[k + 1], p3 = WARP_S[Math.min(WARP_S.length - 1, k + 2)];
  return 0.5 * (2 * p1 + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f + (-p0 + 3 * p1 - 3 * p2 + p3) * f * f * f);
}
function unwarp(s) {
  let lo = 0, hi = WARP_S.length - 1;
  if (s <= WARP_S[0]) return 0;
  if (s >= WARP_S[hi]) return hi * WARP_STEP;
  while (hi - lo > 1) { const m = (lo + hi) >> 1; if (WARP_S[m] <= s) lo = m; else hi = m; }
  return (lo + (s - WARP_S[lo]) / (WARP_S[hi] - WARP_S[lo])) * WARP_STEP;
}

// ---- svg helpers -------------------------------------------------------------
function E(tag, attrs = {}, parent = null) {
  const e = document.createElementNS(NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(e);
  return e;
}
function A(e, attrs) { for (const k in attrs) e.setAttribute(k, attrs[k]); return e; }
function show(e, on) { e.style.display = on ? '' : 'none'; }
function op(e, a) { e.setAttribute('opacity', clamp(a).toFixed(4)); show(e, a > 0.001); }
// camera: map local point (fx,fy) to screen (x,y), rotate r degrees, scale s (sy optional)
function cam(e, x, y, s = 1, r = 0, fx = 0, fy = 0, sy = null) {
  e.setAttribute('transform', `translate(${x.toFixed(3)} ${y.toFixed(3)}) rotate(${r.toFixed(3)}) scale(${s.toFixed(5)} ${(sy ?? s).toFixed(5)}) translate(${(-fx).toFixed(3)} ${(-fy).toFixed(3)})`);
}
function txt(parent, str, attrs) {
  const e = E('text', attrs, parent);
  e.textContent = str;
  return e;
}
const F_LABEL = { 'font-family': 'Barlow Condensed', 'font-weight': 800, 'font-style': 'italic' };
const F_LOGO = { 'font-family': 'Archivo', 'font-weight': 900, 'font-stretch': '125%' };
const F_BODY = { 'font-family': 'Barlow', 'font-weight': 400 };
const F_BOLD = { 'font-family': 'Barlow', 'font-weight': 700 };
const F_COND = { 'font-family': 'Barlow Condensed', 'font-weight': 500 };

// polyline from traced points, smoothed with Catmull-Rom -> cubic beziers
function smoothPath(pts, close = false) {
  const p = pts.map(q => [q[0], q[1]]);
  let d = `M${p[0][0]} ${p[0][1]}`;
  for (let i = 0; i < p.length - 1; i++) {
    const p0 = p[Math.max(0, i - 1)], p1 = p[i], p2 = p[i + 1], p3 = p[Math.min(p.length - 1, i + 2)];
    const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
    const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
    d += ` C${c1[0].toFixed(1)} ${c1[1].toFixed(1)} ${c2[0].toFixed(1)} ${c2[1].toFixed(1)} ${p2[0]} ${p2[1]}`;
  }
  return close ? d + ' Z' : d;
}

// wedge polygon (sunburst ray) from centre, angle a (deg), half width hw (deg), radii r0..r1
function wedge(cx, cy, a, hw, r1, r0 = 0) {
  const a0 = rad(a - hw), a1 = rad(a + hw);
  const p = (r, t) => `${(cx + r * Math.cos(t)).toFixed(2)} ${(cy + r * Math.sin(t)).toFixed(2)}`;
  return r0 > 0 ? `M${p(r0, a0)} L${p(r1, a0)} L${p(r1, a1)} L${p(r0, a1)} Z` : `M${cx.toFixed(2)} ${cy.toFixed(2)} L${p(r1, a0)} L${p(r1, a1)} Z`;
}

// ---- scene registry ------------------------------------------------------------
const SCENES = [];
let ROOT, OVER, PENDING = [];
function scene(name, windows, build) {
  const g = E('g', { id: name }, ROOT);
  const draw = build(g);
  SCENES.push({ name, windows, g, draw });
}
function active(windows, s) { return windows.some(([a, b]) => s >= a && s < b); }

// eye photo: one sharp plate (temporal-median still, upscaled) under a continuous
// horizontal-smear blur, so blur-in/out is perfectly smooth. seek awaits its decode.
const EYE_LEVELS = 24;
const EYE_SRC = (typeof window !== 'undefined' && window.EYE_SRC) || 'assets/eye/eye_00.jpg';
let _eyeFilterId = 0;
function eyeImage(parent, x = 180, y = 150, w = 240, h = 140) {
  const id = 'eyeblur' + (_eyeFilterId++);
  const f = E('filter', { id, x: '-35%', y: '-25%', width: '170%', height: '150%', 'color-interpolation-filters': 'sRGB' }, parent);
  const gb = E('feGaussianBlur', { stdDeviation: '0 0', edgeMode: 'none' }, f);
  const wrap = E('g', { style: 'mix-blend-mode:multiply' }, parent);
  const img = E('image', { x, y, width: w, height: h, preserveAspectRatio: 'none', href: EYE_SRC }, wrap);
  if (img.decode) PENDING.push(img.decode().catch(() => {}));
  wrap.setEye = (blur01, alpha) => {
    const b = clamp(blur01);
    const sx = Math.pow(b, 1.3) * 16.9, sy = sx * 0.28;   // up to ~38 px @1080p horizontally
    if (sx < 0.02) wrap.removeAttribute('filter'); else { A(gb, { stdDeviation: `${sx.toFixed(3)} ${sy.toFixed(3)}` }); wrap.setAttribute('filter', `url(#${id})`); }
    op(wrap, alpha);
  };
  return wrap;
}
