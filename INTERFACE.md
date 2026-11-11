# INTERFACE.md: navigation map

Tile Filling Visualizer: a tkinter + Pillow desktop app (`main.py`) that generates geometric line art, plus a web
interface (`web/`, `run_web.py`) and a static GitHub Pages site built from it.

## Desktop app
| File | Contents |
|------|----------|
| `main.py` | Entry point: `TileFillingApp().run()` |
| `gui/app.py` | `TileFillingApp`: window, canvas, render scheduling, randomize, presets (JSON in `presets/`), PNG / hi-res / batch export |
| `gui/controls.py` | `ControlPanel`: pattern + palette pickers, Rendering / Effects panels (built from `rendering/settings.py`), per-pattern sliders from `get_params()` |
| `patterns/__init__.py` | `PATTERN_REGISTRY`: display name -> pattern class (22 patterns, in README category order) |
| `patterns/base.py` | `BasePattern` (`get_params()`, `generate(width, height, params, margin=40)` -> drawing commands) |
| `patterns/*.py` | One module per pattern family: grid (Grid, Decorated Grid), islamic, penrose, truchet, voronoi, hexagonal, sierpinski, space_filling, moire, spirograph, attractors, lsystem (`PRESETS`), lissajous, guilloche, phyllotaxis, iso_cubes, wireframe3d, flow_field, apollonian, chladni, reaction_diffusion |
| `rendering/colors.py` | `PALETTES`, `hex_to_rgb`, `lerp_color`, `get_line_color`, `gradient_color` |
| `rendering/renderer.py` | `render_to_image()` (background, glow pass, main pass, 2x supersampling, effects chain), `render_high_res()` |
| `rendering/effects.py` | `apply_kaleidoscope`, `apply_gaussian_glow`, `apply_vignette`, `apply_chromatic_aberration`, `apply_scan_lines`, `apply_noise_grain` (and unused `apply_background_gradient`) |
| `rendering/settings.py` | Tk-free render settings: canvas size, margin, supersample, hi-res scale/DPI, batch count, Rendering/Effects control specs, `EFFECT_KEYS`, `EFFECT_STRENGTHS` |
| `rendering/projection.py` | 3D rotation and isometric / perspective projection |
| `utils/geometry.py` | Points, polygons, `PHI`, line helpers |

## Web interface
| File | Contents |
|------|----------|
| `run_web.py` | Starts `web.app:app` with uvicorn on 127.0.0.1:8123 |
| `web/app.py` | FastAPI: `/api/info`, `/api/patterns`, `/api/palettes`, `/api/render-spec`, `/api/check` (exported to the static site via `STATIC_ENDPOINTS`) and `POST /api/render` (PNG from the desktop renderer, local only) |
| `web/catalog.py` | `pattern_list()`, `render_spec()`, `command_stats()`, `check_case()`, `render_png()`: everything from `patterns/` and `rendering/` |
| `web/static/index.html`, `style.css` (kit), `style_app.css`, `core.js` (kit router/helpers), `main.js`, `static_api.js` | Shell, theme, router, static-site data layer |
| `web/static/pyrandom.js` | Python's `random` (MT19937, `seed`, `random`, `randint`, `choice`); `random` = the shared global generator |
| `web/static/pyutil.js` | `Commands` (flat command list), Python `round`/`%`/complex sqrt, geometry, projection, colour helpers |
| `web/static/pat_tilings.js`, `pat_tilings2.js`, `pat_curves.js`, `pat_curves2.js`, `pat_3d.js`, `pat_fields.js` | Line-by-line JS ports of the 22 generators |
| `web/static/engine.js` | `GENERATORS` (registry), `generate()`, `randomParams()`, `stats()`; `engine_worker.js` runs it in a worker |
| `web/static/render.js`, `effects.js` | `renderToCanvas()` / `renderHighRes()` / `toSVG()`; Pillow-exact ports of the effects |
| `web/static/data.js` | `loadSetup()` (API data), worker `Generator`, `thumb()`, form helpers |
| `web/static/home.js`, `studio.js` (+ `studio_io.js`: export, presets, batch, Python render), `gallery.js`, `palettes.js`, `check.js`, `about.js` | Pages |
| `web/static/engine.test.mjs`, `effects.test.mjs` | Node tests against `tests/fixtures/*.json` |

## Scripts and tests
| File | Contents |
|------|----------|
| `scripts/build_static.py` | Builds `site/` for GitHub Pages (front end + exported API JSON) |
| `scripts/screenshots.py` | Playwright smoke test (console errors, phone overflow) and README screenshots in `docs/img/` |
| `scripts/make_engine_fixture.py` | Python reference numbers for the node tests -> `tests/fixtures/engine_fixture.json`, `effects_fixture.json` |
| `tests/test_web.py` | API, static build, node tests, fixtures-are-current |
| `tests/test_rendering.py` | Regression tests for fixed renderer / preset bugs |
| `.github/workflows/pages.yml` | CI: tests, build, deploy to Pages on push to main |

## How it connects
`gui/*` -> `PATTERN_REGISTRY.generate()` -> `rendering.renderer.render_to_image()` -> Tk canvas / PNG.
`web/app.py` -> `web/catalog.py` -> same `patterns/` and `rendering/` modules. The browser fetches specs and palettes from
the API and generates/draws with the JS ports (`engine.js`, `render.js`, `effects.js`), tested against the Python.
