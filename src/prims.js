// ---------------------------------------------------------------------------
// Shared vector primitives. All geometry in 854x480 source units.
// ---------------------------------------------------------------------------

// Hub notch in coordinates normalised to the hub's inner white ellipse (529 x 195)
const HUB = { cx: 427, cy: 240, rx: 529, ry: 195, outer: 1.62 };
const NOTCH_N = [[-0.285, -1.75], [-0.14, -1.75], [-0.134, -0.96], [-0.223, -0.96]];

// orange ring with white centre + notch. Scaled around its centre by k.
function hubRing(parent) {
  const g = E('g', {}, parent);
  const outer = E('ellipse', { cx: 0, cy: 0, rx: HUB.rx * HUB.outer, ry: HUB.ry * HUB.outer * 1.05, fill: C.orange }, g);
  const inner = E('ellipse', { cx: 0, cy: 0, rx: HUB.rx, ry: HUB.ry, fill: '#fff' }, g);
  const notch = E('path', { d: 'M' + NOTCH_N.map(([u, v]) => `${u * HUB.rx} ${v * HUB.ry}`).join(' L') + ' Z', fill: '#fff' }, g);
  g.set = (x, y, k, colour = C.orange, alpha = 1) => {
    cam(g, x, y, k); A(outer, { fill: colour }); op(g, alpha);
  };
  g.parts = { outer, inner, notch };
  return g;
}

// variable-size ring used by the welcome growth (inner radii rx, ry; outer = factor)
function growRing(parent) {
  const g = E('g', {}, parent);
  const outer = E('ellipse', { cx: 0, cy: 0, fill: C.orange }, g);
  const inner = E('ellipse', { cx: 0, cy: 0, fill: '#fff' }, g);
  const notch = E('path', { fill: '#fff' }, g);
  g.set = (x, y, rx, ry, factor, colour, alpha) => {
    cam(g, x, y, 1);
    A(outer, { rx: rx * factor, ry: ry * factor, fill: colour });
    A(inner, { rx, ry });
    A(notch, { d: 'M' + NOTCH_N.map(([u, v]) => `${u * rx} ${v * ry}`).join(' L') + ' Z' });
    op(g, alpha);
  };
  return g;
}

// EYE4U wordmark: "EYE" + "4U" + eye mark. variant: 'intro' | 'white' | 'small'
function eyeMark(parent, o = {}) {
  // local coords: ring centre at 0,0; ring rx 36, ry 12.5
  const g = E('g', {}, parent);
  const ring = E('ellipse', { rx: 36, ry: 12.5, fill: o.ring || C.logoOrange }, g);
  const white = E('ellipse', { cx: -1, rx: 25, ry: 7.4, fill: o.inner || '#fff' }, g);
  const clipId = 'cm' + Math.random().toString(36).slice(2, 8);
  const cp = E('clipPath', { id: clipId }, g); E('ellipse', { rx: 36, ry: 12.5 }, cp);
  const iris = E('circle', { cx: -2, cy: -0.5, r: 11.8, fill: o.iris || '#C0000E', 'clip-path': `url(#${clipId})` }, g);
  const notch = E('path', { d: 'M-7.5 -13.5 L-3.2 -13.5 L-4.6 -2.5 L-5.4 -2.5 Z', fill: o.notch || '#fff' }, g);
  g.parts = { ring, white, iris, notch };
  return g;
}

function wordmark(parent, x, y, size, o = {}) {
  // x,y = left baseline of "EYE"; size = cap height reference (logo on intro = 25)
  const g = E('g', {}, parent);
  const k = size / 25;
  const inner = E('g', { transform: `translate(${x} ${y}) scale(${k})` }, g);
  const eye = txt(inner, 'EYE', { ...F_LOGO, x: 0, y: 0, 'font-size': 34.5, textLength: 76, lengthAdjust: 'spacingAndGlyphs', fill: o.eye || C.logoRed });
  const four = txt(inner, '4U', { ...F_LOGO, x: 81, y: 0, 'font-size': 34.5, textLength: 47, lengthAdjust: 'spacingAndGlyphs', fill: o.four || C.logoOrange });
  const mg = E('g', { transform: 'translate(172 -10)' }, inner);
  const mark = eyeMark(mg, o);
  g.parts = { eye, four, mark, mg, inner };
  return g;
}

// white hub logo (top right): EYE4U + WEB DESIGN
function hubLogo(parent) {
  const g = E('g', {}, parent);
  txt(g, 'EYE4U', { ...F_LOGO, x: 613, y: 32, 'font-size': 26.5, textLength: 78, lengthAdjust: 'spacingAndGlyphs', fill: '#fff' });
  const m = E('g', { transform: 'translate(722.5 22) scale(0.63 0.66)' }, g);
  E('ellipse', { rx: 36, ry: 12.5, fill: '#fff' }, m);
  E('ellipse', { cx: -1, rx: 25, ry: 7.4, fill: C.orange }, m);
  E('circle', { cx: -1.5, r: 11.5, fill: '#fff' }, m);
  E('path', { d: 'M-8 -13.5 L-3 -13.5 L-4.6 -2 L-5.6 -2 Z', fill: C.orange }, m);
  txt(g, 'WEB DESIGN', { ...F_LOGO, x: 614, y: 42.5, 'font-size': 9, textLength: 130, lengthAdjust: 'spacing', fill: '#fff', 'font-weight': 700 });
  return g;
}

function footer(parent) {
  const g = E('g', {}, parent);
  const y = 479;
  txt(g, 'www.eye4u.com', { ...F_BOLD, x: 107, y, 'font-size': 14.5, textLength: 117, lengthAdjust: 'spacingAndGlyphs', fill: '#fff' });
  txt(g, 'Site content is copyright ©1998', { 'font-family': 'Barlow Condensed', 'font-weight': 400, x: 229, y, 'font-size': 14, textLength: 138, lengthAdjust: 'spacingAndGlyphs', fill: '#fff' });
  txt(g, 'EYE4U active media, munich', { ...F_BOLD, x: 371, y, 'font-size': 14.5, textLength: 207, lengthAdjust: 'spacingAndGlyphs', fill: '#fff' });
  txt(g, 'info@eye4u.com', { ...F_BOLD, x: 625, y, 'font-size': 14.5, textLength: 121, lengthAdjust: 'spacingAndGlyphs', fill: '#fff' });
  return g;
}

// big italic label (hub menu words etc). anchor at right edge (x2) / baseline y
function label(parent, str, x2, y, width, size = 34, fill = C.label) {
  return txt(parent, str, { ...F_LABEL, x: x2, y, 'text-anchor': 'end', 'font-size': size, textLength: width, lengthAdjust: 'spacingAndGlyphs', fill });
}

// info&contact with the lighter ampersand
function infoLabel(parent, x2, y, width, size, fill, ampFill) {
  const t = E('text', { ...F_LABEL, x: x2, y, 'text-anchor': 'end', 'font-size': size, textLength: width, lengthAdjust: 'spacingAndGlyphs', fill }, parent);
  const a = E('tspan', {}, t); a.textContent = 'info';
  const b = E('tspan', { fill: ampFill }, t); b.textContent = '&';
  const c = E('tspan', {}, t); c.textContent = 'contact';
  t.amp = b;
  return t;
}

// pool of circles
function circlePool(parent, n) {
  const cs = [];
  for (let i = 0; i < n; i++) cs.push(E('circle', { r: 0, fill: '#000' }, parent));
  cs.draw = list => {
    for (let i = 0; i < n; i++) {
      const d = list[i];
      if (!d || !(d.r > 0.05) || (d.a ?? 1) <= 0.001) { show(cs[i], false); continue; }
      show(cs[i], true);
      A(cs[i], { cx: d.x.toFixed(2), cy: d.y.toFixed(2), r: d.r.toFixed(2), fill: d.c, opacity: (d.a ?? 1).toFixed(3) });
    }
  };
  return cs;
}

// sunburst: n wedges; rays = [{a, hw, c}] ; draw(cx, cy, rot, len, alpha, len0)
function sunburst(parent, rays) {
  const g = E('g', {}, parent);
  const ps = rays.map(r => E('path', { fill: r.c }, g));
  g.draw = (cx, cy, rot, len, alpha = 1, len0 = 0, colour = null, hwScale = 1) => {
    if (len <= 0.2 || alpha <= 0.001) { show(g, false); return; }
    show(g, true); A(g, { opacity: clamp(alpha).toFixed(3) });
    rays.forEach((r, i) => {
      A(ps[i], { d: wedge(cx, cy, r.a + rot, r.hw * hwScale, len * (r.l || 1), len0), fill: colour || r.c });
    });
  };
  return g;
}
function makeRays(seed, n, colours, hwMin, hwMax, jitter = 0.35) {
  const R = rng(seed), out = [];
  for (let i = 0; i < n; i++) {
    const a = (360 / n) * i + (R() - 0.5) * (360 / n) * jitter;
    out.push({ a, hw: lerp(hwMin, hwMax, R()), c: colours[i % colours.length], l: 0.85 + 0.3 * R() });
  }
  return out;
}

// gerbera daisy on a cyan four-point star (drawn procedurally so it stays crisp at 1080p)
function flower(parent) {
  const g = E('g', {}, parent);
  // star: 4 tips at radius 1, concave sides
  let d = '';
  for (let i = 0; i < 4; i++) {
    const a = rad(i * 90 - 45), b = rad(i * 90 + 45);
    const tip = [Math.cos(a), Math.sin(a)], nxt = [Math.cos(b), Math.sin(b)];
    const mid = rad(i * 90), c = [0.28 * Math.cos(mid), 0.28 * Math.sin(mid)];
    d += (i === 0 ? `M${tip[0]} ${tip[1]}` : '') + ` Q${c[0]} ${c[1]} ${nxt[0]} ${nxt[1]}`;
  }
  E('path', { d: d + 'Z', fill: '#1ADBF5' }, g);
  E('path', { d: d + 'Z', fill: '#0B98B5', transform: 'scale(0.62) rotate(8)', opacity: 0.35 }, g);
  const R = rng(7);
  const fl = E('g', { transform: 'scale(0.6)' }, g);
  for (let layer = 0; layer < 3; layer++) {
    const n = [26, 22, 16][layer], len = [1.0, 0.82, 0.6][layer], wdt = [0.17, 0.16, 0.14][layer];
    const cols = [['#E23A10', '#D12C0A', '#EC4A17'], ['#C8260A', '#DD3410', '#B51E08'], ['#A8180A', '#C0220C', '#9A1206']][layer];
    for (let i = 0; i < n; i++) {
      const a = (360 / n) * i + layer * 7 + (R() - 0.5) * 6;
      const L = len * (0.9 + 0.2 * R());
      E('ellipse', { cx: L * 0.55, cy: 0, rx: L * 0.47, ry: wdt, fill: cols[i % 3], transform: `rotate(${a.toFixed(1)})` }, fl);
    }
  }
  E('circle', { r: 0.3, fill: '#7A1208' }, fl);
  E('circle', { r: 0.2, fill: '#3A0604' }, fl);
  for (let i = 0; i < 14; i++) { const a = rad(i * 25.7); E('circle', { cx: 0.25 * Math.cos(a), cy: 0.25 * Math.sin(a), r: 0.035, fill: '#E9C24A', opacity: 0.8 }, fl); }
  return g;
}
