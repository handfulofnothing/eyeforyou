// ---------------------------------------------------------------------------
// seek(t): the only entry point. Pure function of rebuild time t (seconds).
// ---------------------------------------------------------------------------
async function seek(t) {
  t = clamp(t, 0, DUR);
  const s = warp(t);
  PENDING = [];
  for (const sc of SCENES) {
    const on = active(sc.windows, s);
    show(sc.g, on);
    if (on) sc.draw(s, t);
  }
  drawSkip(s);
  drawCursor(s, t);
  await Promise.all(PENDING);
  return s;
}

window.seek = seek;
window.warp = warp;
window.unwarp = unwarp;
window.DURATION = DUR;
window.ready = (async () => {
  await document.fonts.ready;
  // make sure every face is actually loaded before the first frame
  const faces = ["800 italic 20px 'Barlow Condensed'", "700 20px 'Barlow'", "400 20px 'Barlow'", "800 20px 'Archivo'", "500 20px 'Barlow Condensed'", "400 20px 'Barlow Condensed'"];
  await Promise.all(faces.map(f => document.fonts.load(f)));
  // warm the eye plate
  { const im = new Image(); im.src = EYE_SRC; await im.decode().catch(() => {}); }
  await seek(0);
  return true;
})();
