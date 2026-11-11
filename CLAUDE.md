# Tile Filling Visualizer

Desktop app: `python main.py` (tkinter + Pillow). Web app: `python run_web.py` (port 8123); static site: `scripts/build_static.py`.

@INTERFACE.md

- The web engine (`web/static/pat_*.js`, `effects.js`) is a line-by-line port of `patterns/` and `rendering/effects.py`.
  After changing either side, run `python scripts/make_engine_fixture.py` and `python -m pytest -q tests/`.
- Session notes go in SESSION_LOG.md.
