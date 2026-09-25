// ---------------------------------------------------------------------------
// HUB: orange eye frame, menu chain, eye photo, blurbs. Four appearances.
// Everything sits under one camera so the entry/exit zooms carry the menu.
// ---------------------------------------------------------------------------
const MENU = [[533, 119, 37], [615, 162, 34], [650, 238, 31], [634, 313, 28], [581, 356, 25]];
const MENU_C = ['#10EB37', '#13E86A', '#14E499', '#13E1CA', '#14DCFD'];
const SP_STATE = [[533, 119, 37], [465, 153, 29], [425, 201, 30.5], [417, 263, 28], [437, 312, 24.5]];
const SR_STATE = [[555, 174, 25], [608, 192, 27.5], [650, 238, 31], [663, 306, 34], [637, 376, 37]];
const IN_STATE = [[377, 279, 37.5], [412, 345, 32], [470, 386, 30], [532, 387, 27], [581, 356, 25]];
const PEACH = '#F7B08A';

// Catmull-Rom point along the menu arc, u in [0,1] from special (0) to info (1)
function arcPoint(u) {
  const P = MENU.map(m => [m[0], m[1]]);
  const n = P.length - 1, x = clamp(u) * n, i = Math.min(n - 1, Math.floor(x)), f = x - i;
  const p0 = P[Math.max(0, i - 1)], p1 = P[i], p2 = P[i + 1], p3 = P[Math.min(n, i + 2)];
  const cr = (a, b, c, d) => 0.5 * (2 * b + (-a + c) * f + (2 * a - 5 * b + 4 * c - d) * f * f + (-a + 3 * b - 3 * c + d) * f * f * f);
  return [cr(p0[0], p1[0], p2[0], p3[0]), cr(p0[1], p1[1], p2[1], p3[1])];
}
const dotAt = (u, r, c, a = 1) => { const [x, y] = arcPoint(u); return { x, y, r, c, a }; };
const mixDot = (A_, B_, p) => ({ x: lerp(A_.x, B_.x, p), y: lerp(A_.y, B_.y, p), r: lerp(A_.r, B_.r, p), c: mixColor(A_.c, B_.c, p), a: lerp(A_.a ?? 1, B_.a ?? 1, p) });
const stateDot = (S, i, c, a = 1) => ({ x: S[i][0], y: S[i][1], r: S[i][2], c, a });
const menuDot = i => stateDot(MENU, i, MENU_C[i]);

scene('hub', [[21.9, 29.55], [37.98, 45.25], [57.58, 64.53], [78.85, 85]], g => {
  const underBurst = sunburst(g, makeRays(21, 10, [C.mint], 5, 8, 0.45));
  const infoGreen = sunburst(g, makeRays(41, 10, ['#8AF09A', '#3FD85F', '#7A9A2A', '#B5F5BE'], 6, 9, 0.35));
  const infoOrange = sunburst(g, makeRays(43, 12, ['#DD6A10', '#F07A1A'], 4.5, 7.5, 0.35));
  const greenStar = sunburst(g, [0, 45, 90, 135, 180, 225, 270, 315].map(a => ({ a, hw: 4, c: '#33E060', l: 1 })));
  const camG = E('g', {}, g);
  const ring = hubRing(camG); cam(ring, HUB.cx, HUB.cy, 1);
  const logo = hubLogo(camG), foot = footer(camG);
  const eye = eyeImage(camG);
  const dots = circlePool(camG, 10);
  // blurbs
  const blurbSp = E('g', {}, camG), blurbSr = E('g', {}, camG), blurbIn = E('g', {}, camG);
  const up = { ...F_BOLD, 'font-size': 15, fill: C.ink };
  const hi = { ...F_LABEL, 'font-size': 21, fill: C.orange };
  function mixedLine(parent, x, y, w, parts) {
    const t = E('text', { x, y, textLength: w, lengthAdjust: 'spacingAndGlyphs' }, parent);
    for (const [str, st] of parts) { const sp = E('tspan', st, t); sp.textContent = str; }
    return t;
  }
  mixedLine(blurbSp, 166, 228, 364, [['IN ', up], ['special', hi], [" YOU'LL FIND OUR FREE SCREENSAVER", up]]);
  mixedLine(blurbSp, 166, 250, 310, [['AND A TOOL TO ADJUST YOUR MONITOR!', up]]);
  mixedLine(blurbSr, 166, 228, 242, [['ENTER THE ', up], ['showroom', hi], [' TO VIEW', up]]);
  mixedLine(blurbSr, 166, 250, 220, [['MORE FLASH MADE BY EYE4U.', up]]);
  mixedLine(blurbIn, 166, 225, 262, [['info', hi], [' AND HOW TO ', up], ['contact', hi], [' EYE4U.', up]]);
  // labels
  const lSp = label(camG, 'special', 478, 130, 93);
  const lSr = label(camG, 'showroom', 603, 248, 139);
  const lIn = infoLabel(camG, 543, 367, 170, 34, C.label, '#8E8E94');

  const setLabel = (el, a, col) => { op(el, a); A(el, { fill: col }); };
  const LBL = C.label, INK = C.ink, DIM = '#B9B9BF';

  // ---------- choreography helpers ----------
  // chain collapses onto arc parameter u0, then regrows along the arc toward the menu
  function regrow(s, from, fromCol, tA, tB, tC, dir) {
    // tA..tB: the chain bunches up toward its anchor (special for 'down', info for 'up');
    // tB..tC: dots trail out along the menu arc with staggered, eased starts. Continuous:
    // each dot starts exactly where its bunching ended and blends onto the arc.
    const u0 = dir === 'down' ? 0 : 1;
    const pc = EASE.io2(inv(tA, tB, s));
    const a0 = dotAt(u0, MENU[dir === 'down' ? 0 : 4][2] * 0.9, '#000000');
    const out = [];
    for (let i = 0; i < 5; i++) {
      const src = stateDot(from, i, fromCol(i));
      const bunched = { ...src, x: lerp(src.x, lerp(a0.x, src.x, 0.22), pc), y: lerp(src.y, lerp(a0.y, src.y, 0.22), pc), r: lerp(src.r, lerp(a0.r, src.r, 0.5), pc) };
      if (s < tB) { out.push(bunched); continue; }
      const ui = i / 4, order = dir === 'down' ? i : 4 - i;
      const span = tC - tB, d0 = tB + span * 0.12 * order, d1 = d0 + span * 0.52;
      const p = EASE.io2(inv(d0, d1, s));
      const u = lerp(u0, ui, p);
      const m = menuDot(i), onArc = dotAt(u, lerp(bunched.r, m.r, p), mixColor(bunched.c, m.c, p));
      // offset from the arc fades out with the same ease -> no jump at the hand-over
      const off = 1 - p, ax = arcPoint(u0);
      onArc.x += (bunched.x - ax[0]) * off; onArc.y += (bunched.y - ax[1]) * off;
      out.push(onArc);
    }
    return out;
  }
  // click on item k: others slide along the arc into k, then extend into `state`
  function clickSeq(s, k, state, stateCol, tHover, tClick, tMerged, tExt0, tExt1) {
    const out = [];
    const uk = k / 4, pr = EASE.io2(inv(tClick, tMerged, s));
    for (let i = 0; i < 5; i++) {
      const base = menuDot(i);
      if (i === k) {
        const d = { ...base }; if (s >= tHover) d.c = C.orange; out.push(d); continue;
      }
      if (s < tExt0) {
        const u = lerp(i / 4, uk, pr);
        out.push(dotAt(u, lerp(base.r, base.r * 0.85, pr), mixColor(base.c, stateCol, pr)));
      } else {
        const order = Math.abs(i - k), delay = (order - 1) * 0.035;
        const p = EASE.io2(inv(tExt0 + delay, tExt1 + delay, s));
        const from = { ...dotAt(uk, base.r * 0.85, stateCol) };
        out.push(mixDot(from, stateDot(state, i, stateCol), p));
      }
    }
    return out;
  }
  function peachCopies(s, k, t0, t1, list) {
    const [x, y, r] = MENU[k];
    const p = EASE.io2(inv(t0, t1, s)), a = s < t0 ? 0 : 1 - inv(t1 - 0.08, t1 + 0.06, s);
    if (a <= 0) return;
    const c = mixColor(C.orange, PEACH, clamp(p * 1.6));
    list.push({ x: x - 360 * p, y, r: r * 0.95, c, a });
    list.push({ x: x + 360 * p, y, r: r * 0.95, c, a });
  }

  return s => {
    // defaults
    let camX = 427, camY = 240, camK = 1, camR = 0, fx = 427, fy = 240;
    let ringA = 1, logoA = 1, eyeBlur = 0, eyeA = 1;
    let bSp = 0, bSr = 0, bIn = 0;
    let sp = [1, LBL], sr = [1, LBL], inf = [1, LBL];
    let list = [];

    if (s < 29.6) {
      // ---------------- W1: build, idle, special click ----------------
      logoA = inv(22.18, 22.3, s);
      eyeA = inv(24.27, 24.55, s); eyeBlur = 1 - inv(24.27, 24.62, s);
      const popT = [23.67, 23.45, 23.2, 23.0, 22.73];
      if (s < 27.07) {
        for (let i = 0; i < 5; i++) {
          const p = inv(popT[i], popT[i] + 0.1, s);
          if (p > 0) { const d = menuDot(i); d.r = MENU[i][2] * lerp(0.35, 1, EASE.back(p)); list.push(d); } else list.push(null);
        }
        // leader dot
        if (s >= 22.3 && s < 24.6) {  // slot 5
          const LX = [[22.3, 512], [22.6, 560], [22.7, 581], [23.0, 634], [23.2, 651], [23.45, 615], [23.67, 533], [23.9, 460], [24.1, 400], [24.3, 378], [24.45, 388], [24.6, 392]];
          const LY = [[22.3, 355], [22.6, 356], [22.7, 356], [23.0, 313], [23.2, 238], [23.45, 162], [23.67, 119], [23.9, 135], [24.1, 210], [24.3, 270], [24.45, 320], [24.6, 330]];
          const LR = [[22.3, 6], [22.4, 12], [22.6, 20], [22.7, 25], [23.67, 25], [24.6, 23]];
          const LC = [[22.3, PEACH], [22.5, C.orange], [23.75, C.orange], [23.95, '#F39A6C'], [24.6, PEACH]];
          const LA = [[22.3, 1], [24.2, 1], [24.45, 0.75], [24.6, 0]];
          list.push({ x: track(LX, s), y: track(LY, s), r: track(LR, s), c: track(LC, s), a: track(LA, s) });
        }
        inf = [inv(22.73, 22.8, s), LBL]; sr = [inv(23.2, 23.27, s), LBL]; sp = [inv(23.8, 23.87, s), LBL];
      } else if (s < 28.95) {
        list = clickSeq(s, 0, SP_STATE, C.green, 27.07, 27.33, 27.62, 27.72, 27.86);
        peachCopies(s, 0, 27.73, 27.98, list);
        sp = [1, INK];
        const fade = inv(27.33, 27.62, s);
        sr = [1 - fade, mixColor(LBL, DIM, fade * 2)]; inf = [1 - fade, mixColor(LBL, DIM, fade * 2)];
        bSp = inv(27.78, 27.86, s);
        eyeBlur = inv(27.72, 27.86, s); eyeA = lerp(1, 0.85, eyeBlur);
      } else {
        // 28.95-29.55: chain curls down, special dot flashes, dots scatter (transition S takes over)
        sp = [1, INK]; sr = [0, LBL]; inf = [0, LBL]; bSp = 1 - inv(28.95, 29.0, s);
        eyeBlur = 1; eyeA = 0.85 * (1 - inv(28.95, 29.0, s));
        logoA = 1 - inv(28.95, 29.0, s);
        ringA = 1 - inv(29.47, 29.53, s);
        const K = (keys) => ({ x: track(keys.map(k => [k[0], k[1]]), s), y: track(keys.map(k => [k[0], k[2]]), s), r: track(keys.map(k => [k[0], k[3]]), s), c: track(keys.map(k => [k[0], k[4]]), s), a: track(keys.map(k => [k[0], k[5] ?? 1]), s) });
        list.push(K([[28.95, 533, 119, 37, C.orange], [29.0, 533, 119, 60, C.orange], [29.018, 533, 119, 0.1, C.orange, 0], [29.3, 580, 118, 0.1, C.orange], [29.4, 612, 120, 23, C.orange], [29.55, 660, 110, 20, C.orange, 0]]));
        list.push(K([[28.95, 465, 153, 29, C.green], [29.033, 463, 154, 27.5, C.green], [29.2, 465, 150, 34, C.green], [29.4, 438, 97, 30, C.green], [29.55, 470, 70, 34, C.green]]));
        list.push(K([[28.95, 425, 201, 30.5, C.green], [29.033, 423, 203, 31, C.green], [29.2, 400, 182, 36, C.green], [29.4, 308, 133, 52, C.green], [29.55, 250, 110, 46, C.green]]));
        list.push(K([[28.95, 417, 263, 28, C.green], [29.033, 408, 265, 30, C.green], [29.2, 340, 256, 45, C.green], [29.4, 167, 267, 38, '#F08A55'], [29.55, 90, 267, 34, PEACH]]));
        list.push(K([[28.95, 437, 312, 24.5, C.green], [29.033, 402, 334, 34, C.green], [29.2, 351, 352, 45, C.orange], [29.4, 425, 267, 38, '#F07A40'], [29.55, 430, 255, 36, '#F07A40']]));
        list.push(K([[29.3, 425, 267, 8, PEACH, 0], [29.33, 425, 267, 10, PEACH], [29.4, 25, 367, 30, PEACH], [29.55, -40, 400, 30, PEACH]]));
        list.push(K([[29.3, 425, 267, 8, PEACH, 0], [29.33, 425, 267, 10, PEACH], [29.4, 680, 375, 30, PEACH], [29.55, 760, 400, 30, PEACH]]));
      }
    } else if (s < 45.25) {
      // ---------------- W2: zoom out of "special", regrow, showroom click ----------------
      const CK = [[37.82, 90], [38.03, 45], [38.2, 22], [38.4, 11], [38.6, 4.6], [38.72, 2.4], [38.8, 1.5], [38.88, 1.1], [38.96, 1]];
      const CR = [[37.82, -205], [38.03, -175], [38.2, -140], [38.4, -90], [38.6, -30], [38.72, -10], [38.8, -3], [38.96, 0]];
      const CXk = [[37.82, 430], [38.2, 425], [38.4, 410], [38.6, 440], [38.8, 438], [38.96, 431]];
      const CYk = [[37.82, 250], [38.2, 250], [38.4, 245], [38.6, 205], [38.8, 140], [38.88, 122], [38.96, 118]];
      if (s < 38.96) { camK = track(CK, s, true); camR = track(CR, s); camX = track(CXk, s); camY = track(CYk, s); fx = track([[38.03, 398], [38.4, 400], [38.9, 431]], s); fy = 118; }
      ringA = s >= 38.85 ? 1 : 0;
      logoA = inv(38.86, 38.9, s);
      const spCol = s < 38.4 ? track([[37.82, '#12C43A'], [38.2, '#0B5C1E'], [38.4, INK]], s) : INK;
      eyeA = logoA * lerp(0.85, 1, inv(40.0, 40.9, s)); eyeBlur = 1 - inv(40.0, 40.9, s);
      if (s < 42.6) {
        const col = i => (i === 0 && s < 38.87 ? C.orange : C.green);
        list = s < 38.95 ? SP_STATE.map((q, i) => stateDot(SP_STATE, i, col(i))) : regrow(s, SP_STATE, col, 38.95, 39.3, 40.1, 'down');
        const lf = inv(39.5, 40.0, s);
        sp = [1, mixColor(spCol, LBL, lf)]; sr = [lf, mixColor(DIM, LBL, lf)]; inf = [lf, mixColor(DIM, LBL, lf)];
      } else {
        list = clickSeq(s, 2, SR_STATE, C.mint, 42.6, 42.73, 43.13, 43.2, 43.4);
        peachCopies(s, 2, 43.2, 43.45, list);
        sr = [1, INK];
        const fade = inv(42.73, 43.1, s);
        sp = [1 - fade, mixColor(LBL, DIM, fade * 2)]; inf = [1 - fade, mixColor(LBL, DIM, fade * 2)];
        bSr = inv(43.47, 43.55, s) * (1 - inv(44.5, 44.54, s));
        eyeBlur = inv(43.3, 43.47, s); eyeA = lerp(1, 0.85, eyeBlur) * (1 - inv(44.5, 44.54, s));
        logoA = 1 - inv(44.5, 44.54, s);
        if (s >= 44.53) {
          // zoom into the showroom dot, rotating; menu dots swell outward
          const p = inv(44.53, 45.0, s);
          camK = track([[44.53, 1], [44.6, 1.25], [44.7, 1.9], [44.83, 3.3], [45.0, 5.5], [45.25, 9]], s, true);
          camR = track([[44.53, 0], [44.6, -8], [44.7, -15], [44.83, -25], [45.0, -32], [45.25, -40]], s);
          camX = track([[44.53, 650], [44.6, 650], [44.7, 638], [44.83, 625], [45.0, 597], [45.25, 560]], s);
          camY = track([[44.53, 238], [44.6, 237], [44.7, 237], [44.83, 233], [45.0, 233], [45.25, 232]], s);
          fx = 650; fy = 238;
          list = list.map((d, i) => i === 2 ? { ...d, r: s >= 44.56 ? 0 : d.r } : { ...d, x: 650 + (d.x - 650) * (1 + 0.6 * p), y: 238 + (d.y - 238) * (1 + 0.6 * p), r: d.r * (1 + 0.35 * p), a: 1 - inv(45.05, 45.2, s) });
          ringA = 1;
        }
      }
    } else if (s < 64.53) {
      // ---------------- W3: ring zooms in from showroom, regrow, info click ----------------
      const flying = [];
      if (s < 58.35) {
        camK = track([[57.58, 0.09], [57.6, 0.104], [57.75, 0.26], [57.93, 0.46], [58.03, 0.63], [58.2, 0.85], [58.35, 1]], s, true);
        camX = 427; camY = track([[57.58, 245], [57.9, 258], [58.2, 248], [58.35, 240]], s); fx = 427; fy = 240;
        // teal/green circles fly off to the top left
        const p = inv(57.97, 58.35, s);
        if (p > 0 && p < 1) {
          const cs = ['#14DCFC', '#16D6D6', '#14E3A8', '#12E07A'];
          for (let k = 0; k < 4; k++) {
            const q = clamp(p * 1.25 - k * 0.08);
            flying.push({ x: lerp(600, 40 - k * 60, q), y: lerp(200, -60 + k * 150, q), r: lerp(14, 70 + k * 8, q), c: cs[k], a: 1 - inv(0.85, 1, q) });
          }
        }
      }
      logoA = inv(58.33, 58.37, s);
      eyeA = logoA * lerp(0.85, 1, inv(59.8, 60.5, s)); eyeBlur = 1 - inv(59.8, 60.5, s);
      if (s < 61.07) {
        const stateL = regrow(s, SR_STATE, () => C.mint, 58.4, 58.9, 59.7, 'down');
        list = (s < 58.4 ? SR_STATE.map((q, i) => stateDot(SR_STATE, i, C.mint)) : stateL).concat([null, null, null], flying);
        const lf = inv(59.0, 59.5, s);
        sr = [1, mixColor(INK, LBL, lf)]; sp = [lf, mixColor(DIM, LBL, lf)]; inf = [lf, mixColor(DIM, LBL, lf)];
      } else {
        list = clickSeq(s, 4, IN_STATE, C.cyan, 61.07, 61.27, 61.8, 62.2, 62.45);
        peachCopies(s, 4, 61.8, 62.1, list);
        inf = [1, INK];
        const fade = inv(61.27, 61.8, s);
        sp = [1 - fade, mixColor(LBL, DIM, fade * 2)]; sr = [1 - fade, mixColor(LBL, DIM, fade * 2)];
        bIn = inv(61.93, 62.0, s);
        eyeBlur = inv(61.8, 61.93, s); eyeA = lerp(1, 0.85, eyeBlur);
        if (s >= 63.2) {
          ringA = 0; logoA = 0; bIn = 0; eyeA = 0;
          camK = track([[63.2, 1], [63.25, 1.05], [63.4, 1.6], [63.5, 2.4], [63.73, 5.8], [64.53, 38]], s, true);
          camR = track([[63.2, 0], [63.25, -1], [63.4, -10], [63.5, -24], [63.73, -70], [64.53, -360]], s);
          camX = track([[63.2, 458], [63.25, 455], [63.4, 435], [63.5, 400], [63.73, 345], [64.53, 330]], s);
          camY = track([[63.2, 357], [63.25, 352], [63.4, 330], [63.5, 290], [63.73, 225], [64.53, 240]], s);
          fx = 458; fy = 357;
        }
      }
    } else {
      // ---------------- W4: ring zooms in from info, regrow upward, rest ----------------
      if (s < 79.53) {
        camK = track([[78.85, 0.1], [78.93, 0.16], [79.05, 0.28], [79.13, 0.42], [79.2, 0.55], [79.35, 0.75], [79.47, 0.95], [79.53, 1]], s, true);
        camX = track([[78.85, 337], [79.05, 385], [79.3, 427]], s); camY = track([[78.85, 208], [79.05, 235], [79.3, 244], [79.53, 240]], s); fx = 427; fy = 240;
      }
      logoA = inv(79.5, 79.55, s);
      eyeA = logoA * lerp(0.85, 1, inv(80.8, 81.2, s)); eyeBlur = 1 - inv(80.8, 81.2, s);
      list = s < 79.53 ? IN_STATE.map((q, i) => stateDot(IN_STATE, i, i === 4 ? C.orange : C.cyan)) :
        regrow(s, IN_STATE, i => (i === 4 && s < 79.6 ? C.orange : C.cyan), 79.53, 80.0, 80.8, 'up');
      const lf = inv(80.2, 80.7, s);
      inf = [1, mixColor(INK, LBL, lf)]; sp = [lf, mixColor(DIM, LBL, lf)]; sr = [lf, mixColor(DIM, LBL, lf)];
    }

    const gi = s >= 63.2 && s < 63.32;
    greenStar.draw(422, 240, 15, gi ? track([[63.2, 20], [63.25, 45], [63.32, 70]], s) : 0);
    const gg = s >= 63.32 && s < 63.58;
    infoGreen.draw(track([[63.32, 380], [63.58, 330]], s), track([[63.32, 280], [63.58, 330]], s), track([[63.32, 0], [63.58, 30]], s), gg ? 700 : 0, 1);
    const oo = s >= 63.55 && s < 64.53;
    infoOrange.draw(track([[63.55, 300], [63.73, 270], [64.07, 150], [64.53, 200]], s), track([[63.55, 200], [63.73, 180], [64.07, 340], [64.53, 300]], s), track([[63.55, 0], [64.53, 80]], s), oo ? 1600 : 0, 1);
    const ub = s >= 57.58 && s < 58.02;
    underBurst.draw(430, 245, track([[57.47, 0], [58.0, 25]], s), ub ? 1600 : 0, 1 - inv(57.8, 57.88, s), 0, track([[57.47, C.mint], [57.62, C.mint], [57.75, C.green]], s));
    cam(camG, camX, camY, camK, camR, fx, fy);
    op(ring, ringA);
    op(logo, logoA); op(foot, logoA);
    eye.setEye(eyeBlur, eyeA);
    op(blurbSp, bSp); op(blurbSr, bSr); op(blurbIn, bIn);
    setLabel(lSp, sp[0], sp[1]); setLabel(lSr, sr[0], sr[1]); setLabel(lIn, inf[0], inf[1]);
    A(lIn.amp, { fill: inf[1] === INK ? INK : mixColor(inf[1], '#FFFFFF', 0.3) });
    dots.draw(list);
  };
});
