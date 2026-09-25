// ---------------------------------------------------------------------------
// INFO & CONTACT: letters fly past -> page zooms out from the watermark "o"
// (match cut with the hub label) -> nav -> about / contact cards -> home
// ---------------------------------------------------------------------------
function extendPts(pts, d = 400) {
  const a = pts[0], b = pts[1], y = pts[pts.length - 1], z = pts[pts.length - 2];
  const ext = (p, q) => { const dx = p[0] - q[0], dy = p[1] - q[1], L = Math.hypot(dx, dy) || 1; return [p[0] + (dx / L) * d, p[1] + (dy / L) * d]; };
  return [ext(a, b), ...pts, ext(y, z)];
}

function infoPage(parent) {
  const g = E('g', {}, parent);
  const bg = E('rect', { x: -1500, y: -1500, width: 4000, height: 3500, fill: '#fff' }, g);
  const wm = E('text', { ...F_LABEL, x: 100, y: 112, 'font-size': 128, textLength: 655, lengthAdjust: 'spacingAndGlyphs', fill: C.watermark, style: 'mix-blend-mode:multiply' }, g);
  ['info', '&', 'contact'].forEach((t, i) => { const sp = E('tspan', i === 1 ? { fill: '#EFEEF1' } : {}, wm); sp.textContent = t; });
  // band: top edge left->right, bottom edge right->left (the red corner covers its lower right)
  const top = extendPts(SHAPES.info_band_top), bot = extendPts(SHAPES.info_band_bottom).reverse();
  const band = E('path', { d: 'M' + top.map(p => p.join(' ')).join(' L') + ' L' + bot.map(p => p.join(' ')).join(' L') + ' Z', fill: C.orange }, g);
  const red = SHAPES.info_red_left.filter(p => p[0] < 854);
  const redP = E('path', { d: 'M' + [[1300, red[0][1] - 60], ...red, [red[red.length - 1][0] - 40, 900], [1300, 900]].map(p => p.join(' ')).join(' L') + ' Z', fill: C.red }, g);
  const blob = E('circle', { r: 0, fill: '#C6F4FB' }, g);
  const logoG = E('g', {}, g);
  const logo = wordmark(logoG, 105, 175, 31.25);
  const card = E('circle', { r: 0, fill: '#FDE4D8', opacity: 0.82 }, g);
  // black copy of the hub label, exactly over the watermark (match-cut layer)
  const inkWm = E('text', { ...F_LABEL, x: 100, y: 112, 'font-size': 128, textLength: 655, lengthAdjust: 'spacingAndGlyphs', fill: '#111' }, g);
  [['inf', 0], ['o', 1], ['&contact', 0]].forEach(([t, a]) => { const sp = E('tspan', { 'fill-opacity': a }, inkWm); sp.textContent = t; });
  // nav
  const nav = {};
  const navWord = (k, str, x, y, w) => { nav[k] = txt(g, str, { ...F_LABEL, x, y, 'font-size': 31, textLength: w, lengthAdjust: 'spacingAndGlyphs', fill: '#fff' }); };
  navWord('news', 'news', 225, 367, 67); navWord('about', 'about', 375, 324, 80); navWord('contact', 'contact', 537, 290, 95);
  navWord('home', 'home', 667, 459, 73); navWord('back', 'back', 665, 459, 66);
  const subA = txt(g, 'EYE4U ACTIVE MEDIA', { ...F_BOLD, x: 378, y: 334, 'font-size': 7.5, textLength: 70, lengthAdjust: 'spacingAndGlyphs', fill: '#111' });
  const subC = txt(g, 'MAIL, PHONE, ADDRESS', { ...F_BOLD, x: 540, y: 300, 'font-size': 7.5, textLength: 76, lengthAdjust: 'spacingAndGlyphs', fill: '#111' });
  // about copy
  const about = E('g', {}, g);
  const aboutLines = [[98, 'EYE4U active media web design is', 589], [121, 'located in Munich, Germany. Our', 586], [144, 'main background is the highly', 560], [166, 'competitive television market.', 552],
    [213, 'People switch channels as soon as', 589], [236, 'they get bored, just as they do in the', 604], [259, 'World Wide Web.', 463],
    [304, 'Our experiences in producing', 555], [328, 'entertainment and infotainment for', 594], [351, 'the television market ensure that we', 600], [373, 'deliver leading-edge web sites and', 593], [396, 'presentations.', 437]];
  aboutLines.forEach(([y, str, x2]) => txt(about, str, { ...F_BODY, x: 335, y, 'font-size': 17, textLength: x2 - 335, lengthAdjust: 'spacingAndGlyphs', fill: '#1a1a1a' }));
  txt(about, 'Ralf Maier', { ...F_BODY, x: 441, y: 442, 'font-size': 16, textLength: 76, lengthAdjust: 'spacingAndGlyphs', fill: '#1a1a1a' });
  txt(about, 'Reinhard Marscha Jr.', { ...F_BODY, x: 441, y: 465, 'font-size': 16, textLength: 155, lengthAdjust: 'spacingAndGlyphs', fill: '#1a1a1a' });
  // contact card
  const contact = E('g', {}, g);
  const cb = { ...F_BOLD, 'font-size': 16.5, fill: '#222' };
  txt(contact, 'info@eye4u.com', { ...F_BOLD, x: 338, y: 211, 'font-size': 17, textLength: 159, lengthAdjust: 'spacingAndGlyphs', fill: C.orange });
  const line = (y, parts, x2) => { const t = E('text', { x: 336, y, textLength: x2 - 336, lengthAdjust: 'spacingAndGlyphs' }, contact); parts.forEach(([s_, c]) => { const sp = E('tspan', { ...cb, fill: c }, t); sp.textContent = s_; }); };
  line(262, [['+49 (89) 26 0 26 6 ', '#222'], ['26', C.orange]], 520);
  line(285, [['+49 (89) 26 0 26 6 ', '#222'], ['27 fax', C.orange]], 552);
  wordmark(contact, 335, 331, 12.3);
  txt(contact, 'active media', { ...cb, x: 447, y: 331, textLength: 110, lengthAdjust: 'spacingAndGlyphs' });
  txt(contact, 'Schwere-Reiter-Str. 35/7', { ...cb, x: 335, y: 354, textLength: 209, lengthAdjust: 'spacingAndGlyphs' });
  txt(contact, 'D - 80797 Munich, Germany', { ...cb, x: 335, y: 377, textLength: 242, lengthAdjust: 'spacingAndGlyphs' });
  const fx = circlePool(g, 6);
  g.parts = { bg, wm, band, redP, blob, card, logoG, logo, inkWm, nav, subA, subC, about, contact, fx };
  return g;
}

// letters of "info" and the "@" flying past, above the zooming hub (63.2-64.53)
scene('infoIn', [[63.3, 63.96]], g => {
  const mk = str => txt(g, str, { ...F_LABEL, x: 0, y: 0, 'text-anchor': 'middle', 'font-size': 100, fill: C.orange });
  const i = mk('i'), n = mk('n'), at = mk('@');
  const fly = (el, t0, t1, keys, s) => {
    const on = s >= t0 && s < t1; show(el, on); if (!on) return;
    const x = track(keys.map(k => [k[0], k[1]]), s), y = track(keys.map(k => [k[0], k[2]]), s), sc = track(keys.map(k => [k[0], k[3]]), s, true), r = track(keys.map(k => [k[0], k[4]]), s);
    A(el, { transform: `translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${r.toFixed(1)}) scale(${sc.toFixed(3)})` });
  };
  return s => {
    fly(i, 63.33, 63.46, [[63.33, 380, 330, 2.2, 8], [63.4, 420, 420, 4.2, 8], [63.46, 470, 520, 7, 8]], s);
    fly(n, 63.44, 63.57, [[63.44, 460, 330, 2.6, 6], [63.5, 455, 440, 4.4, 6], [63.57, 470, 560, 7.5, 6]], s);
    fly(at, 63.8, 63.94, [[63.8, 420, 330, 3.2, -15], [63.87, 400, 390, 5.5, -15], [63.94, 380, 470, 9, -15]], s);
  };
});

scene('info', [[64.53, 79.2]], g => {
  const page = infoPage(g);
  const P = page.parts, N = P.nav;
  const bubbles = circlePool(g, 5);
  const cyan = sunburst(g, makeRays(31, 12, [C.cyan], 5, 7, 0.3));
  return s => {
    // ---- page camera: zoom out from the watermark "o" (64.53-65.35), home exit pan (78.8-79.13)
    let k = 1, r = 0, x = 272, y = 72, fxp = 272, fyp = 72, pageA = 1;
    if (s < 65.35) {
      k = track([[64.53, 6], [64.87, 3.5], [65.0, 2.6], [65.1, 1.8], [65.25, 1.15], [65.35, 1]], s, true);
      r = track([[64.53, 0], [64.87, 5], [65.1, 3], [65.35, 0]], s);
      fxp = track([[64.53, 255], [65.0, 262], [65.35, 272]], s);
      x = track([[64.53, 470], [64.87, 430], [65.1, 340], [65.35, 272]], s);
      y = track([[64.53, 240], [64.87, 230], [65.1, 130], [65.35, 72]], s);
    } else if (s >= 78.8) {
      const p = EASE.io2(inv(78.78, 79.12, s));
      k = lerp(1, 1.3, p); x = lerp(272, -320, p); y = lerp(72, 40, p); pageA = 1 - inv(78.95, 79.1, s);
    }
    cam(page, x, y, k, r, fxp, fyp);
    op(page, pageA);
    show(P.bg, s < 78.85);
    op(P.inkWm, track([[64.53, 1], [64.87, 0.5], [65.0, 0]], s));
    const m = track([[64.53, 1], [64.7, 2.2], [64.87, 4], [65.0, 5]], s, true);
    A(P.inkWm, { transform: `translate(255 72) scale(${m.toFixed(3)}) translate(-255 -72)` });
    // ---- build
    op(P.logoG, s < 78.8 ? inv(65.38, 65.5, s) : 1 - inv(79.0, 79.13, s));
    if (s >= 78.8) {
      const p = EASE.o2(inv(78.8, 78.95, s));
      A(P.logoG, { transform: `translate(318 160) scale(${lerp(1, 2.2, p).toFixed(3)}) translate(${lerp(-318, -250, p).toFixed(1)} ${lerp(-160, -130, p).toFixed(1)})` });
      A(P.logo.parts.eye, { fill: mixColor(C.logoRed, '#F0A0B0', p) }); A(P.logo.parts.four, { fill: mixColor(C.logoOrange, '#F8C0A0', p) });
    } else { A(P.logoG, { transform: '' }); A(P.logo.parts.eye, { fill: C.logoRed }); A(P.logo.parts.four, { fill: C.logoOrange }); }
    const pop = (el, t) => op(el, inv(t, t + 0.04, s));
    // nav state machine
    const aboutOpen = s >= 69.0 && s < 72.4, contactOpen = s >= 74.4 && s < 76.7;
    const navOn = !(aboutOpen || contactOpen) || false;
    pop(N.news, 65.25); pop(N.about, 65.38); pop(N.contact, 65.5);
    const showNav = s < 69.0 || (s >= 72.4 && s < 74.4) || s >= 76.7;
    op(N.news, showNav ? inv(65.25, 65.29, s) : 0);
    op(N.about, showNav || (s >= 68.8 && s < 69.0) ? inv(65.38, 65.42, s) : 0);
    op(N.contact, showNav ? inv(65.5, 65.54, s) : 0);
    op(N.home, (s < 69.0 || (s >= 72.4 && s < 74.4) || s >= 76.7) ? inv(65.6, 65.64, s) : 0);
    op(N.back, (aboutOpen || contactOpen) ? 1 : 0);
    A(N.about, { fill: s >= 68.8 && s < 69.0 ? C.red : (s >= 68.13 && s < 68.8 ? '#111' : '#fff') });
    A(N.contact, { fill: s >= 74.27 && s < 74.4 ? C.red : (s >= 73.6 && s < 74.27 ? '#111' : '#fff') });
    A(N.home, { fill: s >= 78.17 ? '#111' : '#fff' });
    A(N.back, { fill: (s >= 71.9 && s < 72.4) || (s >= 75.87 && s < 76.7) ? '#111' : '#fff' });
    op(P.subA, s >= 68.13 && s < 69.0 ? 1 : 0);
    op(P.subC, s >= 73.6 && s < 74.4 ? 1 : 0);
    // cards: pale cyan bubble grows into the peach circle, then shrinks away
    let cardR = 0, cardX = 460, cardY = 290, cardC = '#FDE4D8';
    if (s >= 68.85 && s < 72.42) {
      cardX = track([[68.85, 330], [69.0, 337], [69.1, 405], [69.2, 433], [69.3, 461], [69.4, 460], [72.0, 460], [72.15, 430], [72.3, 405], [72.42, 390]], s);
      cardY = track([[68.85, 60], [69.0, 128], [69.1, 128], [69.2, 168], [69.3, 200], [69.4, 290], [72.0, 290], [72.15, 250], [72.3, 128], [72.42, 90]], s);
      cardR = track([[68.85, 10], [69.0, 30], [69.1, 60], [69.2, 90], [69.3, 150], [69.4, 200], [72.0, 200], [72.15, 150], [72.3, 55], [72.42, 20]], s);
      cardC = track([[68.85, C.cyan], [69.05, '#8FE9F8'], [69.25, '#D8EFEF'], [69.4, '#FDE4D8'], [72.0, '#FDE4D8'], [72.12, '#D8EFEF'], [72.3, '#8FE9F8'], [72.42, C.cyan]], s);
    } else if (s >= 74.45 && s < 76.62) {
      cardX = track([[74.45, 300], [74.6, 330], [74.7, 430], [74.8, 455], [74.9, 455], [76.27, 455], [76.4, 430], [76.52, 330], [76.62, 300]], s);
      cardY = track([[74.45, 50], [74.6, 120], [74.7, 250], [74.8, 300], [74.9, 320], [76.27, 320], [76.4, 260], [76.52, 120], [76.62, 50]], s);
      cardR = track([[74.45, 20], [74.6, 45], [74.7, 90], [74.8, 140], [74.9, 180], [76.27, 180], [76.4, 150], [76.52, 45], [76.62, 15]], s);
      cardC = track([[74.45, '#BFF2FB'], [74.8, '#D8EFEF'], [74.9, '#FDE4D8'], [76.27, '#FDE4D8'], [76.4, '#D8EFEF'], [76.62, '#BFF2FB']], s);
    }
    A(P.card, { cx: cardX, cy: cardY, r: cardR, fill: cardC });
    op(P.about, s >= 69.4 && s < 72.0 ? 1 : 0);
    op(P.contact, s >= 74.9 && s < 76.27 ? 1 : 0);
    // ambient bubble on the about card
    A(P.blob, { cx: 600, cy: 120, r: s >= 70.8 && s < 72.0 ? track([[70.8, 0], [71.7, 75], [72.0, 80]], s) : 0 });
    // zoom-out bubbles and exit burst
    const za = inv(64.93, 65.0, s) * (1 - inv(65.1, 65.35, s));
    bubbles.draw(s < 65.35 ? [{ x: 300, y: 120, r: 90, c: '#5BE4C0', a: 0.8 * za }, { x: 470, y: 30, r: 70, c: '#6DE89C', a: 0.8 * za }, { x: 150, y: 300, r: 70, c: '#58E0DF', a: 0.8 * za }] : []);
    cyan.draw(318, 160, track([[78.77, 0], [79.1, 40]], s), s >= 78.77 && s < 78.86 ? track([[78.77, 60], [78.83, 300], [78.86, 420]], s) : 0, 1);
  };
});
