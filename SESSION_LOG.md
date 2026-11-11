# Session Log

## 2026-11-11 -- Web interface and static GitHub Pages site (branch `web-interface`)
- Added `rendering/settings.py` (tkinter-free): canvas size, margin, supersampling, hi-res scale/DPI, batch count, the
  Rendering/Effects control specs and the effect strengths. `gui/controls.py`, `gui/app.py` and `rendering/renderer.py`
  now read them from there (behaviour unchanged; GUI checked by building the window and rendering with effects).
- Added `web/` (FastAPI + ES-module front end from the shared web kit): Home, Studio, Gallery, Palettes, Cross-check,
  About. `web/catalog.py` serves the registry, `get_params()` specs, palettes and render settings from the Python code.
- JS engine: line-by-line ports of all 22 generators, Python's `random` (MT19937 seeding, `randint`, `choice`, so seeded
  patterns are identical), Python `round()` half-to-even and complex `** 0.5`, the renderer, and every effect including
  Pillow's Gaussian blur / blend / chops arithmetic. Generation runs in a module worker.
- Tests: `engine.test.mjs` (68 parameter sets, 760 sampled commands plus counts, colour indices, coordinate sums and
  extents; chaotic attractors compared on their first 20 orbit points), `effects.test.mjs` (7 effect runs pixel-exact vs
  Pillow except a handful of kaleidoscope pixels where libm and V8 differ in the last bit of cos/sin);
  `tests/test_web.py` checks the fixtures are current with rtol 1e-9.
- Static build and `scripts/screenshots.py` (static and against `run_web.py` on 8123) all ok; screenshots in `docs/img/`.

### Bug fixes in the existing code (separate "Fix" commits, regression tests in `tests/test_rendering.py`)
- Film grain halved the brightness of the whole image: `ImageChops.add(img, noise, scale=2, offset=-64)` is
  img/2 + v/2. Now `scale=1, offset=-128` (img + v, clipped). The web port follows.
- Export Hi-Res PNG drew the pattern at its 1x coordinates into the top-left quarter of the 4x image (`render_high_res`
  scaled the canvas and line width but not the commands). Commands are now scaled with the new `scale_commands()`.
  The web hi-res export always scaled them.
- Load Preset ignored the kaleidoscope and effect settings that Save Preset writes (only palette, line width, glow and
  gradient were restored). New `ControlPanel.set_render_settings()` applies every saved setting; loading is factored
  into `TileFillingApp._apply_preset()` (tested with a real Tk window; skipped without a display).
- README said "9 post-processing effects"; the app has 6 (kaleidoscope, bloom, vignette, chromatic aberration, scan
  lines, grain) plus glow and gradient line rendering. Corrected the README.

### Needs George's decision (not changed)
- Sliders that do nothing: Grid `line_weight`, Space-Filling `connect` and `rounded` (both branches draw straight
  segments), Sierpinski `fill_mode`, Chladni `threshold`. Implement or remove? (The web About page says so.)
- Penrose: `_extract_rhombs` pairs triangles into quadrilaterals `[a, b, a2, c]` that are not the P3 rhombs, so the
  picture is a dense web rather than a clean Penrose tiling (matches `samples/penrose_ocean.png`). A correct P3 would change the look.
- Apollonian "Classic" seed: the fourth circle `(cx, cy - 0.73 r, R - r)` is not tangent to the others, so the gasket
  is not a true Apollonian packing.
- Reaction-Diffusion with the default feed/kill dies out below about 48 x 48 resolution (empty picture); fine at the default 80.
- GitHub repo description says "8 pattern types"; the app has 22.
- Web: SVG export and the canvas-size field are web additions; the browser cannot write the 300 DPI tag.
