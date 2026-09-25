// ---------------------------------------------------------------------------
// Cursor: the capture shows the system pointer. Glides between targets, presses
// on the click beats (source times; the warp puts them on the grid).
// ---------------------------------------------------------------------------
const CUR_VIS = [[26.6, 29.4], [32.0, 37.8], [39.5, 44.5], [49.8, 56.23], [59.0, 63.2], [65.6, 78.8]];
const CUR_PATH = [
  [26.6, 640, 52], [27.0, 548, 120], [28.8, 549, 124], [29.4, 600, 102],
  [32.0, 640, 410], [36.9, 690, 438], [37.45, 703, 455],
  [39.5, 560, 420], [42.25, 652, 243], [43.8, 661, 246], [44.5, 663, 247],
  [49.8, 600, 380], [55.75, 700, 452], [56.23, 701, 453],
  [59.0, 640, 300], [60.85, 588, 360], [62.6, 596, 360], [63.2, 598, 361],
  [65.6, 560, 420], [67.95, 415, 318], [68.8, 416, 319], [69.3, 440, 340], [71.6, 700, 452], [71.97, 701, 453],
  [72.5, 660, 420], [73.5, 585, 286], [74.27, 586, 287], [74.8, 600, 400], [75.75, 700, 452], [76.27, 701, 453],
  [76.8, 690, 430], [78.05, 703, 452], [78.8, 703, 452],
];
const CUR_CLICKS = [27.33, 37.6, 42.73, 56.23, 61.27, 68.8, 71.97, 74.27, 76.27, 78.77];
let CURSOR;
function buildCursor() {
  const g = E('g', {}, OVER);
  const d = 'M0 0 L0 17 L4.2 13.2 L7.1 19.8 L10 18.6 L7.2 12.1 L12.4 12.1 Z';
  E('path', { d, fill: '#fff', stroke: '#000', 'stroke-width': 1.1, 'stroke-linejoin': 'round' }, g);
  CURSOR = g;
}
function drawCursor(s) {
  if (!CURSOR) buildCursor();
  const vis = CUR_VIS.some(([a, b]) => s >= a && s < b);
  show(CURSOR, vis);
  if (!vis) return;
  // eased glide between waypoints
  let i = 0;
  while (i < CUR_PATH.length - 2 && s >= CUR_PATH[i + 1][0]) i++;
  const [t0, x0, y0] = CUR_PATH[i], [t1, x1, y1] = CUR_PATH[Math.min(i + 1, CUR_PATH.length - 1)];
  const p = EASE.io2(inv(t0, t1, s));
  const x = lerp(x0, x1, p), y = lerp(y0, y1, p);
  // smooth press: dips to 0.84 and back over ~6 frames around each click
  const press = 1 - 0.16 * Math.max(0, ...CUR_CLICKS.map(c => { const u = (s - (c - 0.04)) / 0.16; return u > 0 && u < 1 ? Math.sin(Math.PI * u) : 0; }));
  cam(CURSOR, x, y, 0.78 * press);
}

// "skip" link of the intro, visible until the hub; grey on white, white on colour
let SKIP;
function drawSkip(s) {
  if (!SKIP) SKIP = txt(OVER, 'skip', { ...F_LABEL, x: 690, y: 452, 'font-size': 15, textLength: 28, lengthAdjust: 'spacingAndGlyphs', fill: '#C6C6CB' });
  const vis = s < 22.2;
  show(SKIP, vis);
  if (vis) A(SKIP, { fill: s >= 13.1 && s < 19.95 ? '#FFFFFF' : '#C6C6CB' });
}
