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
