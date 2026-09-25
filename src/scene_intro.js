// ---------------------------------------------------------------------------
// Intro -> drop -> flower -> mint iris -> red sunburst -> welcome (source 0-22s)
// ---------------------------------------------------------------------------

// ----- INTRO: logo builds on white, tagline morphs --------------------------
scene('intro', [[0, 14.35]], g => {
  E('rect', { x: -20, y: -20, width: W + 40, height: H + 40, fill: '#fff' }, g);
  const logo = E('g', {}, g);
  const wm = wordmark(logo, 324, 215, 25);
  const { eye, four, mark, mg } = wm.parts;
  const almond = E('ellipse', { rx: 36, ry: 12.5, fill: '#000' }, mg);
  mg.insertBefore(almond, mark);
  const bar = E('g', {}, logo);
  txt(bar, 'ACTIVE  MEDIA', { ...F_LOGO, x: 325, y: 236.2, 'font-size': 9.6, textLength: 205, lengthAdjust: 'spacing', fill: '#2c2c2c' });
  E('rect', { x: 325, y: 238.5, width: 205, height: 7.9, fill: '#C3101E' }, bar);
  txt(bar, 'WEB  DESIGN', { ...F_LOGO, x: 327, y: 245.6, 'font-size': 8.2, textLength: 200, lengthAdjust: 'spacing', fill: '#fff' });

  // shimmer: soft white band sweeping the logo
  const defs = E('defs', {}, g);
  const lg = E('linearGradient', { id: 'shim', x1: 0, x2: 1, y1: 0, y2: 0 }, defs);
  E('stop', { offset: 0, 'stop-color': '#fff', 'stop-opacity': 0 }, lg);
  E('stop', { offset: 0.5, 'stop-color': '#fff', 'stop-opacity': 1 }, lg);
  E('stop', { offset: 1, 'stop-color': '#fff', 'stop-opacity': 0 }, lg);
  const shim = E('rect', { y: 180, height: 72, width: 110, fill: 'url(#shim)' }, g);

  // tagline with ghost copies for the Flash-style smeared cross-morph
  const tagG = E('g', {}, g);
  function tagline(parts, width) {
    const grp = E('g', {}, tagG), copies = [];
    for (let k = 0; k < 3; k++) {
      const t = E('text', { ...F_LABEL, x: 429, y: 347, 'text-anchor': 'middle', 'font-size': 34, textLength: width, lengthAdjust: 'spacingAndGlyphs' }, grp);
      for (const [s, f] of parts) { const sp = E('tspan', { fill: f }, t); sp.textContent = s; }
      copies.push(t);
    }
    grp.set = (alpha, smear) => {
      op(grp, alpha > 0.001 ? 1 : 0);
      A(copies[0], { x: 429, opacity: alpha.toFixed(3) });
      A(copies[1], { x: (429 - 11 * smear).toFixed(2), opacity: (alpha * 0.45 * (smear > 0.02 ? 1 : 0)).toFixed(3) });
      A(copies[2], { x: (429 + 7 * smear).toFixed(2), opacity: (alpha * 0.35 * (smear > 0.02 ? 1 : 0)).toFixed(3) });
    };
    return grp;
  }
  const t1 = tagline([['Open your eyes', C.label]], 211);
  const t2 = tagline([['see and hear...', C.label]], 200);
  const t3 = tagline([['the web ', C.label], ['eye', C.logoOrange], [' like!', C.label]], 234);

  return s => {
    show(eye, s >= 0.8);
    show(four, s >= 3.367);
    A(four, { fill: mixColor('#111111', C.logoOrange, EASE.io2(inv(3.367, 4.35, s))) });
    // eye mark: black almond -> maroon -> full colour mark
    show(mg, s >= 5.933);
    A(almond, { fill: mixColor('#000000', '#5E0A0A', inv(5.933, 6.17, s)) });
    op(almond, 1 - inv(6.3, 6.4, s));
    op(mark, inv(6.17, 6.37, s));
    show(bar, s >= 6.367);
    // shimmer passes
    let sa = 0, sx = 0;
    if (s >= 7.733 && s < 8.8) { const p = inv(7.733, 8.8, s); sx = lerp(270, 560, EASE.io2(p)); sa = 0.9 * Math.sin(Math.PI * p); }
    if (s >= 9.4 && s < 10.03) { const p = inv(9.4, 10.03, s); sx = lerp(290, 560, EASE.io2(p)); sa = 0.55 * Math.sin(Math.PI * p); }
    A(shim, { x: sx.toFixed(2) }); op(shim, sa);
    // taglines
    const m1 = inv(3.133, 3.367, s), m2 = inv(6.03, 6.167, s);
    t1.set(1 - m1, m1 > 0 && m1 < 1 ? m1 : 0);
    t2.set(m1 * (1 - m2), (m1 > 0 && m1 < 1 ? 1 - m1 : 0) + (m2 > 0 && m2 < 1 ? m2 : 0));
    t3.set(m2 * (1 - inv(10.5, 10.667, s)), m2 > 0 && m2 < 1 ? 1 - m2 : 0);
  };
});

// ----- DROP: the eye mark spins and zooms through the camera ----------------
scene('drop', [[12.83, 14.62]], g => {
  const m = E('g', {}, g);
  const mask = E('mask', { id: 'dropNotch', maskUnits: 'userSpaceOnUse', x: -60, y: -60, width: 120, height: 120 }, m);
  E('rect', { x: -60, y: -60, width: 120, height: 120, fill: '#fff' }, mask);
  E('path', { d: 'M-8.4 -14 L-5.3 -14 L-5.9 -7.0 L-8.9 -7.0 Z', fill: '#000' }, mask);
  const body = E('g', { mask: 'url(#dropNotch)' }, m);
  E('ellipse', { rx: 36, ry: 12.5, fill: C.orange }, body);
  E('ellipse', { cx: -0.5, rx: 24.6, ry: 8.5, fill: '#000' }, body);
  // camera fitted per source frame against the capture (tools/fit_drop.py): t, x, y, scale, rotation
  const K = FIT_DROP;
  const keys = i => K.map(k => [k[0], k[i]]);
  const X = keys(1), Y = keys(2), S = keys(3), R = keys(4);
  return s => {
    cam(m, track(X, s, false, false, true), track(Y, s, false, false, true), track(S, s, true, false, true), track(R, s, false, false, true));
  };
});

// ----- FLOWER on black: path, size and spin measured per source frame ------------
scene('flower', [[14.40, 15.42]], g => {
  const bg = E('rect', { x: -20, y: -20, width: W + 40, height: H + 40, fill: '#000' }, g);
  const f = flower(g);
  // tools/track_flower.py -> tools/smooth_fits.py: t, x, y, tip radius, spin
  const k = i => FIT_FLOWER.map(q => [q[0], q[i]]);
  const X = k(1), Y = k(2), R = k(3), ROT = k(4);
  return s => {
    show(bg, s >= 14.6);
    show(f, s >= 14.42 && s < 15.345);
    cam(f, track(X, s, false, false, true), track(Y, s, false, false, true), track(R, s, true, false, true), track(ROT, s, false, false, true));
  };
});

// ----- MINT: iris opens, eye floats in and zooms through to red ---------------
scene('mint', [[15.38, 17.12]], g => {
  const bg = E('rect', { x: -20, y: -20, width: W + 40, height: H + 40, fill: '#000' }, g);
  const disc = E('g', {}, g);
  E('circle', { r: 44, fill: C.orange }, disc);
  E('circle', { r: 39.5, fill: '#fff' }, disc);
  E('circle', { r: 35, fill: C.mint }, disc);
  const eyeG = E('g', {}, g);
  // eye at rx = 100 units; iris centred (measured at 16.4s: iris r = 0.37 rx)
  E('ellipse', { rx: 100, ry: 34.8, fill: C.orange }, eyeG);
  E('ellipse', { rx: 66, ry: 20.5, fill: '#fff' }, eyeG);
  const cp = E('clipPath', { id: 'mintIris' }, eyeG); E('ellipse', { rx: 100, ry: 34.8 }, cp);
  E('circle', { r: 37, fill: C.red, 'clip-path': 'url(#mintIris)' }, eyeG);
  E('path', { d: 'M-16 -37 L-7 -37 L-9 -22 L-14 -22 Z', fill: C.mint }, eyeG);
  // cameras fitted per source frame (tools/fit_mint.py)
  const d = i => FIT_DISC.map(q => [q[0], q[i]]);
  const DX = d(1), DY = d(2), DR = d(3);
  const e = i => FIT_MINTEYE.map(q => [q[0], q[i]]);
  const EX = e(1), EY = e(2), ES = e(3), ER = e(4);
  return s => {
    show(bg, s < 15.8);
    cam(disc, track(DX, s, false, false, true), track(DY, s, false, false, true), track(DR, s, true, false, true) / 44);
    show(eyeG, s >= 15.43);   // appears as its tween launches from the disc centre
    cam(eyeG, track(EX, s, false, false, true), track(EY, s, false, false, true), track(ES, s, true, false, true), track(ER, s, false, false, true));
  };
});

// ----- RED SUNBURST: two 5-ray sets (white over orange) turning at different rates ---
scene('sunburst', [[17.06, 20.08]], g => {
  const bg = E('rect', { x: -20, y: -20, width: W + 40, height: H + 40, fill: C.red }, g);
  const five = (c, hw) => [0, 72, 144, 216, 288].map(a => ({ a, hw, c, l: 1 }));
  const O = sunburst(g, five(C.orange, 7.8)), Wt = sunburst(g, five('#FFFFFF', 6.5));
  // centre + rotations measured from the capture (tools/fit_sun*.py)
  const k = i => FIT_SUN.map(q => [q[0], q[i]]);
  const CX = k(1), CY = k(2), RW = k(3), RO = k(4);
  const LEN = [[17.06, 22], [17.2, 190], [17.433, 470], [17.7, 3000], [20.1, 9000]];
  return s => {
    show(bg, s >= 17.095);
    const cx = track(CX, s, false, false, true), cy = track(CY, s, false, false, true), L = track(LEN, s, true);
    O.draw(cx, cy, track(RO, s, false, false, true), s < 17.12 ? 0 : L, 1);
    Wt.draw(cx, cy, track(RW, s, false, false, true), L, 1);
  };
});

// ----- WELCOME: text, echoing eye rings, ring grows into the hub frame -------------
scene('welcome', [[19.98, 21.95]], g => {
  const wbg = E('rect', { x: -20, y: -20, width: W + 40, height: H + 40, fill: '#fff' }, g);
  const ring = growRing(g);
  // eye rings: 3 echo copies + main, each with blur filter
  const defs = E('defs', {}, g);
  const mk = (id) => { const f = E('filter', { id, x: '-50%', y: '-80%', width: '200%', height: '260%' }, defs); return E('feGaussianBlur', { stdDeviation: 0 }, f); };
  const eyes = [], blurs = [];
  for (let k = 0; k < 4; k++) {
    blurs.push(mk('wblur' + k));
    const eg = E('g', { filter: `url(#wblur${k})` }, g);
    const inner = E('g', {}, eg);
    E('ellipse', { rx: 100, ry: 33, fill: C.orange }, inner);
    E('ellipse', { rx: 66, ry: 16.5, fill: '#fff' }, inner);
    E('circle', { r: 36, fill: '#C8102A' }, inner);
    E('path', { d: 'M-10 -64 L1 -64 L-1.5 -20 L-3 -20 Z', fill: '#fff' }, inner);
    eyes.push({ eg, inner });
  }
  const wtxt = txt(g, 'welcome!', { ...F_LABEL, x: 0, y: 0, 'text-anchor': 'middle', 'font-size': 31, textLength: 126, lengthAdjust: 'spacingAndGlyphs', fill: C.label });
  const EYE_RX = [[20.3, 280], [20.6, 230], [20.85, 195], [21.0, 150], [21.05, 137], [21.2, 112], [21.35, 98], [21.55, 104], [21.8, 150], [21.95, 190]];
  const EYE_A = [[20.3, 0.0], [20.45, 0.22], [20.6, 0.32], [20.8, 0.42], [20.95, 0.7], [21.0, 1], [21.55, 0.95], [21.8, 0.35], [21.95, 0.0]];
  const EYE_BL = [[20.3, 8], [20.6, 5], [20.9, 1.5], [21.0, 0], [21.55, 0], [21.8, 6], [21.95, 9]];
  const ECHO_A = [[20.85, 0], [21.0, 1], [21.6, 1], [21.9, 0.4], [21.95, 0]];
  const RING = [[21.28, 150], [21.35, 237], [21.45, 290], [21.55, 360], [21.7, 440], [21.8, 490], [21.9, 529], [21.95, 529]];
  const RING_C = [[21.28, '#FDE3D4'], [21.35, '#FBC6A6'], [21.55, '#F58C58'], [21.8, '#F27A2C'], [21.9, C.orange]];
  return s => {
    show(wbg, s >= 20.075);
    // text: slides from upper left, darkens, fades out before the ring rush
    const p = EASE.o2(inv(20.0, 20.3, s));
    const tx = lerp(298, 430, p), ty = lerp(90, 117, p), ts = lerp(0.86, 1, p);
    A(wtxt, { transform: `translate(${tx.toFixed(2)} ${ty.toFixed(2)}) scale(${ts.toFixed(4)})`, fill: mixColor('#B8B8BD', C.label, inv(20.0, 20.2, s)) });
    op(wtxt, 1 - inv(21.2, 21.33, s));
    const rx = track(EYE_RX, s), a = track(EYE_A, s), bl = track(EYE_BL, s), ec = track(ECHO_A, s);
    const echo = [1.65, 1.4, 1.2, 1.0], ea = [0.12 * ec, 0.2 * ec, 0.32 * ec, 1.0];
    eyes.forEach((e, k) => {
      cam(e.eg, 428, 240, (rx / 100) * echo[k]);
      op(e.eg, a * ea[k]);
      A(blurs[k], { stdDeviation: (bl / ((rx / 100) * echo[k]) + (k < 3 ? 1.2 : 0)).toFixed(3) });
    });
    // ring grows into the hub frame
    if (s >= 21.28) {
      const irx = track(RING, s);
      ring.set(428, 240, irx, irx * (HUB.ry / HUB.rx), 1.49, track(RING_C, s), clamp(inv(21.28, 21.36, s) * 1));
    } else op(ring, 0);
  };
});
