# EYE4U rebuild

Live: https://marceloeduardo.com/funslop/eyeforyou/ (the player, a live beat map, the side-by-side, and how it was made).
Made by Claude (Anthropic) in Claude Code, directed by Marcelo Jansson. The original site, animation and music are by EYE4U active media, Munich, 1998.

**Not in this repo:** the 1998 screen capture, its extracted frames, the soundtrack and the rendered videos. They are not ours to redistribute.
To rebuild, put the capture at `analysis/source.mp4`. The scripts in `analysis/` and `tools/` regenerate the frames, audio analysis and assets from it.

Programmatic 1920×1080 / 60 fps remake of the 1998 EYE4U Flash site capture
(`analysis/source.mp4`, 84.87 s), snapped to the soundtrack's measured beat grid.

## Output

- `out/eye4u_rebuild_1080p60.mp4`: final render (H.264, 60 fps, AAC 320k, −14 LUFS).
- `out/eye4u_side_by_side.mp4`: 1998 capture on the left, rebuild on the right.
- `build/index.html` + `build/assets/`: the page the renderer shoots (bare 1080p stage under Playwright or `?render`).
- `web/eyeforyou/`: the hosted site (https://marceloeduardo.com/funslop/eyeforyou/). `index.html` is the case study (`tools/site.py` + `tools/site_tpl.html`): the live player framed from `player/`, a beat map that follows playback, the side-by-side video, and the process with its analysis charts. Every number on it is computed from `analysis/`.
- `web/eye4u.html`: the same player as one self-contained 4 MB file (fonts, photo and soundtrack inlined); opens offline by double-click.

## Web player

The page renders live in the browser: every frame is `seek(t)`, nothing is pre-rendered video.
The soundtrack is decoded once and played through Web Audio. The picture clock is `performance.now()`,
slaved to the time actually reaching the speakers (`getOutputTimestamp`), with drift absorbed by nudging the
clock rate by at most 1%. Measured: picture vs. heard audio within 0.2 ms, seeks exact on any server.
Controls: click or Space to play/pause, ← → ±5 s, F fullscreen, scrubber. `window.player` exposes
`play()`, `pause()`, `seek(t)` and `time` for embedding.

Redeploy (Small Orange, same SSH account as the main site; touches only this folder):

```bash
.venv/bin/python tools/build.py
.venv/bin/python tools/usage.py ~/.claude/projects/<project>/<session>.jsonl   # day + token usage shown on the page
.venv/bin/python tools/site.py --github https://github.com/handfulofnothing/eyeforyou
rsync -az --itemize-changes -e ssh web/eyeforyou/ marceloe@sh089.asoshared.com:public_html/funslop/eyeforyou/
```

## How it works

- **One clock.** `window.seek(t)` computes every attribute from time. There are no CSS animations, timers or carried state. It awaits image decodes before resolving.
- **Source-time authoring.** Motion is written against the capture's own seconds (`src/scene_*.js`).
- **Smooth time warp.** `seek` maps rebuild time to source time through a minimum-curvature warp (`tools/smooth_warp.py` → `src/timeline.js`). It is a constrained QP: section cuts and hard cuts land exactly on their downbeats, other events are soft targets, and playback speed changes by at most 1.4% per frame. Speed never steps.
- **Interpolation.** Keyframe tracks are cubic Hermite with Bessel tangents, so velocity carries through every key. Held values are eased into and out of. Fitted monotone data uses PCHIP (no overshoot).
- **Fitted cameras.** The drop spin, the mint iris and the red sunburst were fitted per source frame by silhouette matching (`tools/fit_drop.py`, `fit_mint.py`, `fit_disc2.py`, `fit_sun*.py`). The 1998 player ran at an irregular 16–20 fps, so the samples are re-timed onto a smooth Flash-frame clock, smoothed with shape-preserving splines (`tools/smooth_fits.py`) and stored densely in `src/fits.js`.
- **Flash tweens rebuilt exactly.** The flower and the mint eye were measured in every source frame (`tools/track_flower.py`, `tools/track_minteye.py`) and rebuilt as the tweens they were authored as. The flower follows one cubic-Bézier motion guide, eased by arc length, with a constant spin. The eye is three chained tweens: a straight ease-out, a Bézier hook, and a camera push. They are fitted per Flash frame (the 1998 player showed frames at jittery times) and mapped to time with a steady 21 fps clock.
- **Traced shapes.** Page outlines come from the capture's pixels (`tools/shapes.py`), fitted to circles and ellipses where they are geometric.
- **Raster assets.** The only photo is the hub eye: a temporal-median still, upscaled, under a continuous horizontal-smear blur computed per frame.

## Grid

135.1 BPM, 4/4. The site restarts its music loop at every section change, so the grid is re-anchored per block:

| Block | Bar 1 at (s) | BPM |
|---|---|---|
| A (the drop) | 12.871 | 135.03 |
| H1 (hub) | 22.598 | 134.96 |
| S (special) | 28.942 | 135.18 |
| R (showroom) | 44.540 | 135.63 |
| E (hub return) | 56.271 | 135.13 |
| F (info) | 63.134 | 135.10 |

Every block was fitted to its kick onsets (median residual 1.4–6.8 ms). Section cuts and hard cuts sit exactly on downbeats. UI hits are soft targets pulled toward their beats (median 47 ms off, worst 156 ms), so that motion speed stays smooth.

## Rebuild

```bash
.venv/bin/python tools/build.py            # assemble build/index.html
cd render && node probe.mjs 25.5 45.35     # probe source times, then:
.venv/bin/python tools/grid_compare.py     # side-by-side probe sheet
cd render && node render.mjs 9             # 9 subframes across t±1/240 -> ffmpeg tmix -> out/chunks
cd render && node motion_audit.mjs 0 84.8  # frame-by-frame velocity-kink audit of every shape
```

Then concat the chunks and mux `audio/master.wav` (see the commands used in `out/`).
