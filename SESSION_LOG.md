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

### Needs George's decision (first three items resolved later the same day, see below)
- Sliders that do nothing: Grid `line_weight`, Space-Filling `connect` and `rounded` (both branches draw straight
  segments), Sierpinski `fill_mode`, Chladni `threshold`. Implement or remove? (The web About page says so.)
- Penrose: `_extract_rhombs` pairs triangles into quadrilaterals `[a, b, a2, c]` that are not the P3 rhombs, so the
  picture is a dense web rather than a clean Penrose tiling (matches `samples/penrose_ocean.png`). A correct P3 would change the look.
- Apollonian "Classic" seed: the fourth circle `(cx, cy - 0.73 r, R - r)` is not tangent to the others, so the gasket
  is not a true Apollonian packing.
- Reaction-Diffusion with the default feed/kill dies out below about 48 x 48 resolution (empty picture); fine at the default 80.
- GitHub repo description says "8 pattern types"; the app has 22.
- Web: SVG export and the canvas-size field are web additions; the browser cannot write the 300 DPI tag.

## 2026-11-11 -- Approved pattern fixes (George), branch `web-interface`
- Five sliders that did nothing now work, desktop and web alike (fixtures regenerated, `tests/test_patterns.py`):
  Grid "Line Weight" (line-width multiplier, carried as an optional 4th command element that the renderer honours);
  Space-Filling "Connected Line" off (each segment drawn alone, shortened by max(rounded, 0.15) at both ends) and
  "Rounded Corners" (corners cut `rounded` of the way along both segments, joined by a 3-piece quadratic Bezier);
  Sierpinski "Fill Outlines" (leaf triangles/squares/hexagons as filled polygons; `polygon` commands now honour their
  documented `fill` flag); Chladni "Line Threshold" (extra contours in colour 1 at +-threshold x max|f|, outlining the
  band where sand gathers; the nodal lines are unchanged).
- Apollonian: the Classic seed's fourth circle was `(cx, cy - 0.73 r, R - r)`, overlapping the others. By Descartes'
  theorem (curvatures -1/R, 2/R, 2/R -> 3/R) it is now radius R/3 at 2R/3 above the centre. Also, `_descartes`
  returned all four sign combinations of the complex formula, and only two of them are real tangent circles; the
  spurious ones drew circles that crossed others or lay far off the canvas (most of the old 122k default commands).
  Candidates are now kept only if they touch all three parents (`_tangent_to_all`). Default Classic: 3,852 commands,
  a true gasket. The "Four" seed's three inner circles overlap each other, so with the tangency check it now draws only
  its 4 seed circles: left for George (see the report).
- Penrose: the old Robinson subdivision rules were not the P3 ones, so the "rhombs" were overlapping quadrilaterals (a
  dense web; see the old `samples/penrose_ocean.png`). Rewritten with the standard Robinson-triangle subdivision
  (thin 36 deg / thick 108 deg golden triangles, sides divided by the golden ratio); Sun = ten thin triangles, Star =
  five thick rhombs at the centre (both halves list the long diagonal in the same order, otherwise the edge-matching
  rule breaks and T-junctions appear). Half rhombs at the patch edge draw only their two sides. Test checks one side
  length, golden-triangle angles, area conservation, every edge shared by two triangles or on the patch outline,
  rhomb angles 36/144 and 72/108, and thick/thin -> golden ratio. Regenerated `samples/penrose_ocean.png` and
  `samples/apollonian_gold.png` (defaults, with bloom for the gasket) with the fixed code.
- Checks re-run: pytest 26 passed (test_web 15, test_rendering 3, test_patterns 8), node engine 158 checks / effects 7,
  screenshots static (8 routes) and against `run_web.py` on 8123 all ok, Cross-check page 22/22, desktop GUI renders
  the changed patterns. README screenshots refreshed.
- Still open for George: the Apollonian "Four" seed (three inner circles at 0.36 R from the centre with radius 0.4 R
  overlap each other, so no tangent circles exist and it now draws only its 4 seed circles; it was previously filled
  with spurious circles). Make it a tangent configuration (which would match "Three") or drop it?
- Resolved (George): removed the Apollonian "Four" seed (overlapping circles; a tangent version would duplicate
  "Three"). The `initial` slider is now 0=Classic, 1=Three; `initial=2` in old presets or calls draws Three. Loading a
  preset (desktop `_apply_preset` and web studio) now clamps numeric parameters to the slider range, so presets from
  older versions stay valid. Tests: `test_apollonian_four_seed_removed_and_old_value_falls_back_to_three`,
  `test_load_preset_clamps_old_values`; the fixture's `initial=2` case checks the JS fallback.
