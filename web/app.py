"""FastAPI web app for the Tile Filling Visualizer: serves the front end in static/ and the JSON API under /api.

Run with `python run_web.py` (http://127.0.0.1:8123, local only). `scripts/build_static.py` exports every path in
STATIC_ENDPOINTS to JSON for the GitHub Pages site, so keep that list in step with the GET routes below.

Everything comes from the desktop app's own modules (via web/catalog.py): patterns.PATTERN_REGISTRY and each
pattern's get_params(), rendering.colors.PALETTES, rendering.settings (control-panel specs and effect strengths), and
rendering.renderer for the server-side PNG (POST /api/render, local app only).
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from web.catalog import (
    CATEGORIES, CHECK_OVERRIDES, PALETTES, PATTERN_REGISTRY, check_case, pattern_list, render_png, render_spec,
)
from pathlib import Path

STATIC = Path(__file__).resolve().parent / "static"
TITLE = "Tile Filling Visualizer"

app = FastAPI(title=TITLE)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/info")
def info():
    """Project summary and counts for the home page."""
    spec = render_spec()
    return {"title": TITLE, "version": "1", "patterns": len(PATTERN_REGISTRY), "palettes": len(PALETTES),
            "effects": 1 + len(spec["effects"]), "categories": [{"name": c, "count": n} for c, n in CATEGORIES]}


@app.get("/api/patterns")
def patterns():
    """Every registered pattern with its description, docstring, category and get_params() slider specs."""
    return pattern_list()


@app.get("/api/palettes")
def palettes():
    """rendering.colors.PALETTES: background, line colours (cycled by colour index) and accent."""
    return PALETTES


@app.get("/api/render-spec")
def render_settings():
    """Control-panel ranges/defaults and renderer constants from rendering/settings.py."""
    return render_spec()


@app.get("/api/check")
def check():
    """Python summary numbers for every pattern at its defaults (see catalog.CHECK_OVERRIDES), for the cross-check."""
    return {"overrides": CHECK_OVERRIDES, "cases": [check_case(name) for name in PATTERN_REGISTRY]}


class RenderRequest(BaseModel):
    pattern: str
    params: dict = {}
    settings: dict = {}
    width: int = Field(800, ge=50, le=2000)
    height: int = Field(800, ge=50, le=2000)
    hires: bool = False


@app.post("/api/render")
def render(req: RenderRequest):
    """PNG drawn by the desktop renderer (Pillow): the same image the desktop app would export."""
    if req.pattern not in PATTERN_REGISTRY:
        raise HTTPException(404, f"unknown pattern {req.pattern!r}")
    if req.hires and req.width * req.height > 1000 * 1000:
        raise HTTPException(422, "hi-res renders are limited to 1000 x 1000 base size on the local server")
    png, n = render_png(req.pattern, req.params, req.settings, req.width, req.height, hires=req.hires)
    return Response(png, media_type="image/png", headers={"X-Commands": str(n)})


# GET paths (without the /api prefix) written to the static site as api/<path>.json.
STATIC_ENDPOINTS = ["/info", "/patterns", "/palettes", "/render-spec", "/check"]
