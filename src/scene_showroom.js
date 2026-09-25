// ---------------------------------------------------------------------------
// SHOWROOM: dot burst -> iris to black -> bubble snakes -> eye close-up becomes
// the page -> page -> zoom back out -> disc + bursts into the hub ring
// The page IS an extreme close-up of an eye mark: red arc = iris, white = the
// inner ellipse, orange = the ring (edges traced from the capture).
// ---------------------------------------------------------------------------
const SR_EYE = { cx: -600, cy: 77, rx: 1403.5, ry: 506.2, rot: 1.67 };

function showroomEye(parent) {
  const g = E('g', {}, parent);
  const outer = E('ellipse', { cx: SR_EYE.cx, cy: SR_EYE.cy, rx: 1754, ry: 900, fill: C.orange, transform: `rotate(${SR_EYE.rot} ${SR_EYE.cx} ${SR_EYE.cy})` }, g);
  const inner = E('ellipse', { cx: SR_EYE.cx, cy: SR_EYE.cy, rx: SR_EYE.rx, ry: SR_EYE.ry, fill: '#fff', transform: `rotate(${SR_EYE.rot} ${SR_EYE.cx} ${SR_EYE.cy})` }, g);
  const cid = 'srclip' + Math.random().toString(36).slice(2, 7);
  const cp = E('clipPath', { id: cid }, g);
  E('ellipse', { cx: SR_EYE.cx, cy: SR_EYE.cy, rx: SR_EYE.rx, ry: SR_EYE.ry, transform: `rotate(${SR_EYE.rot} ${SR_EYE.cx} ${SR_EYE.cy})` }, cp);
  const iris = E('circle', { cx: -509, cy: 117.7, r: 703.6, fill: C.red, 'clip-path': `url(#${cid})` }, g);
  const notch = E('path', { d: 'M-2150 -760 L-1980 -760 L-2010 -330 L-2050 -330 Z', fill: '#000' }, g);
  g.parts = { outer, inner, iris, notch };
  return g;
}

function showroomContent(parent) {
  const g = E('g', {}, parent);
  const wm = txt(g, 'showroom', { ...F_LABEL, x: 210, y: 113, 'font-size': 124, textLength: 525, lengthAdjust: 'spacingAndGlyphs', fill: '#E0DFE4', style: 'mix-blend-mode:multiply' });
  const logo = wordmark(g, 611, 38, 15.6);
  const list = E('g', {}, g);
  const OR = '#F26A1B', GR = '#8C8C92';
  const rowsL = [['FORD.COM', ' BETTER IDEAS™ FLASH', 451], ['NEWSMAKER.DE', ' FLASH/HTML SITE', 467], ['VIDEOCOM.CH', ' FLASH WEB SITE', 424],
    ['OCRA FINNLAND', ' FLASH ANIMATION', 485], ['HEAVYFLASH VIDEO', ' 332K FLASH', 455], ['CAPTURED SPHERE', ' 24K FLASH', 435],
    ['MODULAR WEBSYNTH', ' FLASH', 428], ['I+K INFRASERV', ' HTML/JS', 403, '¹']];
  const rowsR = [[484, 'HIELSCHER.DE', ' FLASH WEB SITE', 701], [497, 'UNIMARK.CH', ' FLASH WEB SITE', 717], [464, 'KERZEN.COM/.DE', ' FLASH INTRO', 695],
    [517, 'EYE4UFO', ' 74K FLASH', 667], [490, 'HARMONY ON ICE', ' 90K FLASH', 708], [472, 'SPACE TV', ' HTML/JS', 612, '²'], [464, 'LIVE MY LIFE', ' FLASH CD-ROM', 680, '²']];
  const row = (x, y, name, desc, x2, sup) => {
    const t = E('text', { x, y, 'font-size': 14.2, textLength: x2 - x, lengthAdjust: 'spacingAndGlyphs' }, list);
    const a = E('tspan', { ...F_BOLD, fill: OR }, t); a.textContent = name;
    if (sup) { const s_ = E('tspan', { ...F_BOLD, fill: OR, 'font-size': 9, dy: -5 }, t); s_.textContent = sup; }
    const b = E('tspan', { 'font-family': 'Barlow', 'font-weight': 600, fill: GR, dy: sup ? 5 : 0 }, t); b.textContent = desc;
  };
  const ys = [150.5, 170, 189.5, 209, 228.5, 248, 267.5, 287];
  rowsL.forEach((r, i) => row(215, ys[i], r[0], r[1], r[2], r[3]));
  rowsR.forEach((r, i) => row(r[0], ys[i], r[1], r[2], r[3], r[4]));
  const cta = E('g', {}, g);
  txt(cta, 'CLICK ON ONE OF THE LINKS ABOVE TO CHECK OUT', { ...F_BOLD, x: 185, y: 318.5, 'font-size': 15, textLength: 386, lengthAdjust: 'spacingAndGlyphs', fill: '#111' });
  txt(cta, 'OUR WORK FOR VARIOUS CLIENTS.', { ...F_BOLD, x: 185, y: 338.5, 'font-size': 15, textLength: 259, lengthAdjust: 'spacingAndGlyphs', fill: '#111' });
  const fn = (y, n, str, x2) => {
    const t = E('text', { x: 162, y, 'font-size': 12.5, textLength: x2 - 162, lengthAdjust: 'spacingAndGlyphs', 'font-family': 'Barlow Condensed', 'font-weight': 500, fill: '#222' }, cta);
    const a = E('tspan', { fill: C.orange, 'font-size': 9, dy: -4 }, t); a.textContent = n;
    const b = E('tspan', { dy: 4 }, t); b.textContent = ' ' + str;
  };
  fn(386, '1', 'COPYRIGHT 1997-1998 INFRASERV GMBH & CO. GENDORF KG, A HOECHST SERVICE COMPANY', 562);
  fn(406, '2', 'COPYRIGHT 1998 G.A.T. FILM- UND FERNSEH PRODUKTION GMBH & CO. KG', 485);
  const home = txt(g, 'home', { ...F_LABEL, x: 660, y: 462, 'font-size': 34, textLength: 73, lengthAdjust: 'spacingAndGlyphs', fill: '#fff' });
  const mail = txt(g, 'info@eye4u.com', { ...F_BOLD, x: 517, y: 461, 'font-size': 14, textLength: 121, lengthAdjust: 'spacingAndGlyphs', fill: '#fff' });
  g.parts = { wm, logo, list, cta, home, mail };
  return g;
}

// a chain of bubbles following its head's past path, darkening toward the tail
function snake(pool, path, rads, t, n, dt, cols, alpha = 1) {
  const out = [];
  for (let k = n - 1; k >= 0; k--) {
    const tk = t - k * dt;
    if (tk < path[0][0]) { out.push(null); continue; }     // stable slot per trail position
    const x = track(path.map(p => [p[0], p[1]]), tk), y = track(path.map(p => [p[0], p[2]]), tk);
    const r = track(rads, tk) * (1 - 0.06 * k);
    out.push({ x, y, r, c: cols[Math.min(k, cols.length - 1)], a: alpha });
  }
  return out;
}
const TEALS = ['#14DCFC', '#12B1C8', '#0D8495', '#096B7A', '#095863', '#063138'];
const TEALS_DARK = ['#0D8495', '#096B7A', '#095863', '#074149', '#063138', '#052428'];
const blendPal = (a, b, f) => a.map((c, i) => mixColor(c, b[i], f));

// ----- entry: burst from the showroom dot, iris to black, bubbles on black ----------
scene('showroomIn', [[44.53, 49.36]], g => {
  const black = E('rect', { x: -20, y: -20, width: W + 40, height: H + 40, fill: '#000' }, g);
  const star = sunburst(g, [0, 45, 90, 135, 180, 225, 270, 315].map(a => ({ a, hw: 7, c: C.cyan, l: 1 })));
  const disc = E('circle', { r: 0, fill: C.orange }, g);
  const burst = sunburst(g, makeRays(3, 12, [C.cyan], 4, 6, 0.3));
  const iris = E('circle', { r: 0, fill: '#000' }, g);
  const flash = E('rect', { x: -20, y: -20, width: W + 40, height: H + 40, fill: '#fff' }, g);
  const eyeG = showroomEye(g);
  const bubbles = circlePool(g, 24);
  return s => {
    // burst phase (over the zooming hub)
    const dx = track([[44.53, 650], [44.6, 650], [44.7, 638], [44.83, 625], [45.0, 597], [45.2, 567], [45.5, 480], [45.63, 442], [45.73, 440]], s);
    const dy = track([[44.53, 238], [44.6, 237], [44.7, 237], [44.83, 233], [45.0, 233], [45.2, 232], [45.5, 232], [45.63, 233], [45.73, 233]], s);
    const dr = track([[44.53, 31], [44.6, 17], [44.7, 40], [44.83, 79], [45.0, 121], [45.2, 192], [45.35, 260], [45.5, 331], [45.63, 400], [45.73, 450], [45.8, 480]], s);
    const burstOn = s < 45.8;
    A(disc, { cx: dx, cy: dy, r: burstOn && s >= 44.56 ? dr : 0 });
    star.draw(dx, dy, track([[44.53, 0], [44.83, 20]], s), s >= 44.56 && s < 44.85 ? track([[44.56, 20], [44.6, 32], [44.7, 58], [44.83, 90]], s) : 0, 1);
    burst.draw(dx, dy, track([[44.8, 0], [45.8, 70]], s), s >= 44.8 && burstOn ? track([[44.8, 90], [44.9, 700], [45.0, 1500]], s, true) : 0, 1, 0, null, track([[44.9, 1], [45.2, 1.15], [45.5, 1.3], [45.73, 1.5]], s));
    A(iris, { cx: dx, cy: dy, r: burstOn ? track([[45.47, 0], [45.5, 12], [45.63, 150], [45.73, 240], [45.8, 480]], s) : 0 });
    // white flash frame, then black ground
    show(flash, s >= 45.767 && s < 45.84);
    show(black, s >= 45.84);
    // snakes on black
    let list = [];
    if (s >= 45.84 && s < 49.2) {
      const fade = 1 - inv(49.05, 49.2, s);
      list = list.concat(snake(null, [[45.87, 125, 93], [46.2, 297, 135], [46.5, 580, 97], [46.9, 813, 100], [47.2, 1050, 60]],
        [[45.87, 22], [46.2, 35], [46.5, 97], [46.9, 150], [47.2, 210]], s, 5, 0.1, TEALS));
      list = list.concat(snake(null, [[46.15, 920, 330], [46.5, 738, 300], [46.9, 468, 345], [47.3, 200, 400], [47.55, -200, 430]],
        [[46.15, 15], [46.5, 40], [46.9, 75], [47.3, 150], [47.55, 230]], s, 5, 0.1, blendPal(TEALS, TEALS_DARK, inv(47.1, 47.4, s)), 1 - inv(47.5, 47.62, s)));
      // big dark cluster that hangs at the top while the column rises
      {
        const q = EASE.io2(inv(47.1, 48.6, s)), ca = inv(47.1, 47.35, s) * (1 - inv(48.3, 48.6, s)) * fade, g = lerp(0.6, 1, EASE.o2(inv(47.1, 47.5, s)));
        list.push({ x: lerp(560, 700, q), y: lerp(40, 60, q), r: lerp(120, 150, q) * g, c: '#095863', a: ca });
        list.push({ x: lerp(700, 800, q), y: 90, r: lerp(130, 150, q) * g, c: '#0D8495', a: ca });
        list.push({ x: lerp(430, 600, q), y: lerp(60, 30, q), r: lerp(110, 130, q) * g, c: '#063138', a: ca });
      }
      list = list.concat(snake(null, [[47.52, 470, 480], [47.6, 463, 332], [47.8, 450, 200], [48.0, 452, 60], [48.15, 430, 10], [48.28, 360, 90], [48.4, 290, 220], [48.55, 255, 360], [48.7, 245, 430], [49.0, 220, 410], [49.2, 205, 420]],
        [[47.52, 20], [47.6, 40], [47.8, 60], [48.1, 85], [48.4, 147], [48.7, 175], [49.0, 170]], s, 6, 0.075, blendPal(blendPal(TEALS, TEALS_DARK, inv(48.4, 48.75, s)), Array(6).fill('#0A2F36'), inv(48.7, 49.0, s)), fade));
    }
    // eye close-up that becomes the page (drawn under the bubbles)
    const eyeOn = s >= 47.62;
    show(eyeG, eyeOn);
    if (eyeOn) {
      const k = track([[47.62, 0.1], [47.8, 0.18], [48.1, 0.3], [48.4, 0.5], [48.7, 0.75], [49.0, 0.93], [49.2, 1]], s, true);
      const r = track([[47.62, -18], [47.8, -15], [48.1, -12], [48.4, -8], [48.7, -3], [49.2, 0]], s);
      const x = track([[47.62, -60], [47.8, 42], [48.1, -188], [48.4, -300], [48.7, -420], [49.0, -560], [49.2, -600]], s);
      const y = track([[47.62, 330], [47.8, 265], [48.1, 230], [48.4, 150], [48.7, 110], [49.0, 85], [49.2, 77]], s);
      cam(eyeG, x, y, k, r, SR_EYE.cx, SR_EYE.cy);
      A(eyeG.parts.inner, { fill: mixColor('#F7B391', '#FFFFFF', inv(48.8, 49.2, s)) });
    }
    // bubbles are drawn above the eye: re-append pool to keep it on top
    bubbles.draw(list);
  };
});

// ----- the page, and the zoom back out ----------------------------------------------
scene('showroom', [[49.2, 57.45]], g => {
  E('rect', { x: -20, y: -20, width: W + 40, height: H + 40, fill: '#000' }, g);
  const eyeG = showroomEye(g);
  const blob = E('circle', { r: 0, fill: C.mint }, g);
  const content = showroomContent(g);
  const P = content.parts;
  const snakes = circlePool(g, 8);
  return s => {
    // page colours fade up from white after the flash frame
    const inA = inv(49.3, 49.55, s);
    const outP = inv(56.25, 56.62, s);
    A(eyeG.parts.iris, { fill: s < 56.3 ? mixColor('#FFFFFF', C.red, inA) : track([[56.3, C.red], [56.62, '#D5230C'], [56.95, '#D8330E'], [57.2, '#E4561C']], s) });
    A(eyeG.parts.outer, { fill: s < 56.3 ? mixColor('#FFFFFF', C.orange, inA) : C.orange });
    A(eyeG.parts.inner, { fill: s < 56.3 ? '#FFFFFF' : track([[56.3, '#FFFFFF'], [56.6, '#FAC8AA'], [56.9, '#F59A6A'], [57.1, '#F07A3E'], [57.2, '#EC6526']], s) });
    if (s < 56.3) cam(eyeG, SR_EYE.cx, SR_EYE.cy, 1, 0, SR_EYE.cx, SR_EYE.cy);
    else {
      const k = track([[56.3, 1], [56.6, 0.8], [56.9, 0.3], [57.2, 0.104], [57.45, 0.09]], s, true);
      const r = track([[56.3, 0], [56.9, 4], [57.2, 6]], s);
      const x = track([[56.3, -600], [56.6, -400], [56.9, 180], [57.2, 380], [57.45, 400]], s);
      const y = track([[56.3, 77], [56.6, 110], [56.9, 230], [57.2, 233], [57.45, 238]], s);
      cam(eyeG, x, y, k, r, SR_EYE.cx, SR_EYE.cy);
    }
    // content
    const on = s < 56.25;
    show(content, on);
    if (on) {
      op(P.wm, inv(49.57, 49.62, s)); op(P.logo, inv(49.57, 49.62, s));
      op(P.list, inv(49.7, 49.75, s)); op(P.cta, inv(49.7, 49.75, s));
      op(P.home, inv(49.57, 49.62, s)); op(P.mail, inv(49.57, 49.62, s));
    }
    // ambient mint blob behind the list
    const bOn = s >= 52.1 && s < 55.7;
    A(blob, {
      cx: track([[52.1, 100], [53.0, 300], [53.5, 383], [54.3, 330], [55.3, 280], [55.7, 268]], s),
      cy: track([[52.1, 560], [53.0, 330], [53.5, 258], [54.3, 120], [55.3, 20], [55.7, -80]], s), r: bOn ? 92 : 0,
    });
    // exit bubbles under the shrinking eye
    snakes.draw(s >= 56.75 ? snake(null, [[56.75, 760, 540], [57.0, 420, 480], [57.2, 163, 425], [57.45, 20, 290]], [[56.75, 40], [57.0, 70], [57.2, 90], [57.45, 115]], s, 6, 0.06, TEALS) : []);
  };
});

// ----- exit overlays: orange disc + cyan asterisk, peach disc + mint burst, green burst over the hub ring --
scene('showroomExit', [[57.3, 57.6]], g => {
  const bg = E('rect', { x: -20, y: -20, width: W + 40, height: H + 40, fill: '#000' }, g);
  const disc = E('circle', { cx: 430, cy: 245, r: 0, fill: C.orange }, g);
  const ast = sunburst(g, [0, 72, 144, 216, 288].map(a => ({ a, hw: 7, c: C.cyan, l: 1 })));
  const peach = E('circle', { cx: 430, cy: 245, r: 0, fill: '#FBC0A0' }, g);
  const mintB = sunburst(g, makeRays(21, 10, [C.mint], 5, 8, 0.45));
  return s => {
    show(bg, false);
    A(disc, { r: s >= 57.3 && s < 57.47 ? track([[57.3, 150], [57.37, 290], [57.47, 320]], s) : 0 });
    ast.draw(430, 245, 20, s >= 57.33 && s < 57.47 ? track([[57.33, 45], [57.47, 95]], s) : 0, 1, 0, null, 1.2);
    A(peach, { r: s >= 57.47 && s < 57.58 ? 420 : 0 });
    // mint then green burst, over the hub's small ring (hub is below this scene)
    mintB.draw(430, 245, track([[57.47, 0], [58.0, 25]], s), s >= 57.47 ? 1600 : 0, 1, 0, C.mint);
  };
});
