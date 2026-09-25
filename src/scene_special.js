// ---------------------------------------------------------------------------
// SPECIAL: zoom through "special" -> page tumbles into place -> page -> exit burst
// ---------------------------------------------------------------------------

// page layer shared by the transition and the page itself
function specialPage(parent) {
  const g = E('g', {}, parent);
  E('rect', { x: -3000, y: -3000, width: 7000, height: 7000, fill: '#fff' }, g);
  E('circle', { cx: -2593.5, cy: -251.5, r: 2885.8, fill: C.orange }, g);    // left band (traced edge)
  E('circle', { cx: 702.3, cy: 885.1, r: 494.3, fill: C.green }, g);         // bottom-right blob
  const blob = E('circle', { r: 0, fill: C.cyan }, g);
  const wm = txt(g, 'special', { ...F_LABEL, x: 115, y: 172, 'font-size': 176, textLength: 555, lengthAdjust: 'spacingAndGlyphs', fill: C.watermark, style: 'mix-blend-mode:multiply' });
  const content = E('g', {}, g);
  const bullets = circlePool(content, 2);
  const w = {};
  const word = (k, str, x, y, len) => { w[k] = txt(content, str, { ...F_LABEL, x, y, 'font-size': 32, textLength: len, lengthAdjust: 'spacingAndGlyphs', fill: '#5A5A60' }); };
  word('free', 'free', 347, 268, 50); word('screensaver', 'screensaver', 405, 268, 171);
  word('monitor', 'monitor', 347, 326, 105); word('adjustment', 'adjustment', 461, 326, 155);
  const home = txt(content, 'home', { ...F_LABEL, x: 660, y: 462, 'font-size': 34, textLength: 73, lengthAdjust: 'spacingAndGlyphs', fill: '#fff' });
  const mail = txt(content, 'info@eye4u.com', { ...F_BOLD, x: 520, y: 461, 'font-size': 14, textLength: 120, lengthAdjust: 'spacingAndGlyphs', fill: '#fff' });
  const fx = circlePool(g, 8);
  const sweep = E('path', { fill: '#FBD9C6' }, g);
  g.parts = { blob, wm, content, bullets, w, home, mail, fx, sweep };
  return g;
}

scene('special', [[29.15, 37.82]], g => {
  // --- transition overlays (sit above the hub while it is still visible) ---
  const white = E('rect', { x: -20, y: -20, width: W + 40, height: H + 40, fill: '#fff' }, g);
  const page = specialPage(g);
  const P = page.parts;
  const wmBlurF = E('filter', { id: 'wmblur', x: '-20%', y: '-50%', width: '140%', height: '200%' }, g);
  const wmBlur = E('feGaussianBlur', { stdDeviation: 0 }, wmBlurF);
  A(P.wm, { filter: 'url(#wmblur)' });
  const ast = sunburst(g, [0, 60, 120, 180, 240, 300].map(a => ({ a, hw: 1, c: '#28D4F2', l: 1 })));
  const burst = sunburst(g, makeRays(5, 14, ['#6FE8FC'], 3.5, 6.5, 0.4));
  const disc = E('circle', { r: 0, fill: C.orange }, g);
  const zoomTxt = txt(g, 'special', { ...F_LABEL, x: 0, y: 0, 'text-anchor': 'middle', 'font-size': 34, textLength: 93, lengthAdjust: 'spacingAndGlyphs', fill: C.green });

  return s => {
    // hub still under us until 29.5: white ground only after the frame is gone
    show(white, s >= 29.5);
    // ---- page camera ----
    const pageOn = s >= 30.33;
    show(page, pageOn);
    if (pageOn) {
      const k = track([[30.33, 0.42], [30.5, 0.54], [30.8, 0.69], [31.07, 0.94], [31.27, 1]], s);
      const r = track([[30.33, 150], [30.5, 180], [30.8, 270], [31.07, 323], [31.27, 360, 'o2']], s);
      const x = track([[30.33, 330], [30.5, 297], [30.8, 190], [31.07, 220], [31.27, 392]], s);
      const y = track([[30.33, 250], [30.5, 223], [30.8, 233], [31.07, 175], [31.27, 115]], s);
      cam(page, x, y, k, r, 392, 115);
      A(wmBlur, { stdDeviation: (2.6 * (1 - inv(31.0, 31.27, s))).toFixed(2) });
      // page build
      const built = s >= 31.27;
      show(P.content, built);
      if (built) {
        const wf = P.w;
        op(wf.free, inv(31.45, 31.5, s)); A(wf.free, { transform: `translate(0 ${lerp(-133, 0, EASE.o(inv(31.45, 31.66, s))).toFixed(2)})` });
        op(wf.screensaver, inv(31.55, 31.6, s)); A(wf.screensaver, { transform: `translate(${lerp(160, 0, EASE.o(inv(31.55, 31.7, s))).toFixed(2)} 0)` });
        op(wf.monitor, inv(31.6, 31.65, s)); A(wf.monitor, { transform: `translate(0 ${lerp(59, 0, EASE.o(inv(31.6, 31.88, s))).toFixed(2)})` });
        op(wf.adjustment, inv(31.72, 31.76, s)); A(wf.adjustment, { transform: `translate(0 ${lerp(-300, 0, EASE.o(inv(31.72, 31.92, s))).toFixed(2)})` });
        op(P.home, inv(31.42, 31.47, s)); op(P.mail, inv(31.42, 31.47, s));
        const bp = EASE.back(inv(31.86, 31.93, s));
        P.bullets.draw([{ x: 316, y: 256, r: 23 * bp, c: C.cyan }, { x: 316, y: 313, r: 23 * bp, c: C.cyan }]);
        // flash sweep over the orange band and pale mint bubbles
        const sw = inv(31.27, 31.45, s);
        A(P.sweep, { d: `M${lerp(250, 110, sw)} -10 L${lerp(330, 190, sw)} -10 L${lerp(250, 110, sw)} 490 L${lerp(170, 30, sw)} 490 Z`, opacity: (0.75 * (1 - sw)).toFixed(3) });
        show(P.sweep, sw > 0 && sw < 1);
        const a1 = 1 - inv(31.3, 31.5, s), a2 = s < 31.45 ? 0 : 1 - inv(31.55, 31.72, s);
        const fl = inv(31.93, 32.3, s), fa = s < 31.93 ? 0 : 1 - inv(32.2, 32.32, s);
        P.fx.draw([
          { x: 667, y: 273, r: 170, c: '#C3F6D9', a: 0.8 * a1 }, { x: 350, y: 332, r: 50, c: '#2BE574', a: a1 }, { x: 350, y: 423, r: 45, c: '#2BE574', a: a1 },
          { x: 313, y: 82, r: 58, c: '#8EF0C8', a: 0.85 * a2 }, { x: 447, y: 248, r: 100, c: '#9AF0C0', a: 0.8 * a2 }, { x: 480, y: 457, r: 100, c: '#90F0A0', a: 0.8 * a2 },
          { x: lerp(290, 50, fl), y: lerp(313, 257, fl), r: 17, c: mixColor(C.orange, '#FFFFFF', fl), a: fa },
          { x: lerp(345, 472, fl), y: 317, r: 18, c: mixColor(C.orange, PEACH, fl), a: fa },
        ]);
      } else { show(P.sweep, false); P.fx.draw([]); P.bullets.draw([]); }
      // ambient cyan blob (under the watermark, above the ground)
      const bx = track([[35.3, 300], [35.8, 280], [36.2, 297], [36.7, 320], [37.2, 342], [37.6, 360], [37.82, 372]], s);
      const by = track([[35.3, 560], [35.8, 470], [36.2, 373], [36.7, 280], [37.2, 175], [37.6, 120], [37.82, 96]], s);
      A(P.blob, { cx: bx, cy: by, r: s >= 35.3 ? 72 : 0 });
    }
    // ---- zoom-through overlays ----
    const astL = track([[29.18, 20], [29.2, 50], [29.3, 80], [29.4, 112], [29.47, 150]], s);
    const astX = track([[29.2, 430], [29.4, 425]], s), astY = track([[29.2, 248], [29.4, 267]], s);
    ast.draw(astX, astY, track([[29.2, 10], [29.47, 30]], s), s >= 29.18 && s < 29.47 ? astL : 0, 1, 0, null, track([[29.2, 6], [29.4, 9]], s));
    const bl = track([[29.46, 150], [29.53, 330], [29.67, 520], [29.8, 700], [30.0, 1100]], s, true);
    const bc = track([[29.4, '#45D9F6'], [29.53, '#6FE8FC'], [29.97, '#A4F0FD'], [30.3, '#DDF9FE']], s);
    burst.draw(track([[29.4, 425], [29.53, 430], [29.67, 442], [29.8, 470], [30.1, 520]], s), track([[29.4, 267], [29.53, 250], [29.67, 240], [29.8, 245], [30.1, 300]], s),
      track([[29.4, 0], [30.4, 40]], s), bl, 1 - inv(30.3, 30.45, s), 0, bc);
    const dOn = s >= 29.5 && s < 30.45;
    A(disc, {
      cx: track([[29.5, 505], [29.67, 380], [29.8, 230], [29.97, 100], [30.13, 20], [30.3, -60], [30.45, -120]], s),
      cy: track([[29.5, 133], [29.67, 132], [29.8, 115], [29.97, 60], [30.13, -40], [30.3, -170], [30.45, -300]], s),
      r: dOn ? track([[29.5, 60], [29.67, 115], [29.8, 175], [29.97, 300], [30.13, 520], [30.3, 860], [30.45, 1200]], s, true) : 0,
    });
    const zOn = s >= 29.45 && s < 30.42;
    show(zoomTxt, zOn);
    if (zOn) {
      const k = track([[29.45, 1.2], [29.53, 1.5], [29.67, 3.2], [29.8, 4.7], [29.97, 7.5], [30.13, 12], [30.3, 18], [30.42, 26]], s, true);
      const r = track([[29.45, -12], [29.53, -8], [29.67, 10], [29.8, 18], [29.97, 32], [30.13, 42], [30.3, 48], [30.42, 51]], s);
      // focus drifts from the word centre onto "p", then "e" (text units)
      const fxT = track([[29.7, 0], [29.97, -24], [30.13, -24], [30.3, -14], [30.42, -12]], s), fyT = track([[29.7, 0], [29.97, -7], [30.42, -6]], s);
      const x = track([[29.45, 470], [29.53, 488], [29.67, 530], [29.8, 575], [29.97, 560], [30.13, 520], [30.3, 470], [30.42, 440]], s);
      const y = track([[29.45, 128], [29.53, 133], [29.67, 165], [29.8, 223], [29.97, 290], [30.13, 320], [30.3, 330], [30.42, 330]], s);
      A(zoomTxt, { transform: `translate(${x.toFixed(2)} ${y.toFixed(2)}) rotate(${r.toFixed(2)}) scale(${k.toFixed(4)}) translate(${(-fxT).toFixed(2)} ${(11 - fyT).toFixed(2)})` });
    }
  };
});
// exit: hard cut to a pale cyan burst with orange discs, over the hub's zoom-out
scene('specialExit', [[37.82, 38.36]], g => {
  const b = sunburst(g, makeRays(9, 10, ['#5FE9FC'], 6, 9, 0.3));
  const discs = circlePool(g, 3);
  return s => {
    b.draw(430, 252, track([[37.82, 0], [38.36, 60]], s), 1500, 1 - inv(38.22, 38.36, s), 0, track([[37.82, '#5FE9FC'], [38.1, '#9BF0FD'], [38.25, '#D6F7FD']], s));
    const a = 1 - inv(37.95, 38.03, s);
    discs.draw([{ x: -10, y: 192, r: 150, c: '#F37A3A', a }, { x: 813, y: 250, r: 150, c: '#F37A3A', a }, { x: 563, y: 467, r: 150, c: '#12C43A', a }]);
  };
});
