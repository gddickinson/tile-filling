"""Web interface for the Tile Filling Visualizer.

- app.py      FastAPI app: /api JSON (patterns, palettes, render spec, cross-check) and POST /api/render (PNG)
- catalog.py  pattern catalogue, command statistics and Pillow rendering, built from patterns/ and rendering/
- static/     ES-module front end: the JS pattern engine (pat_*.js, engine.js), renderer and effects, pages
"""
