"""Pattern catalogue for the web API, built from the repo's own code (no tkinter import).

- pattern_list(): every entry of patterns.PATTERN_REGISTRY with its description, docstring, category and the
  get_params() slider specs the desktop control panel is built from.
- command_stats(): summary numbers of a generate() command list (the browser engine computes the same numbers, so the
  cross-check page and the node test can compare the two implementations).
- render_png(): a PNG made by the desktop renderer (rendering.renderer.render_to_image, Pillow).
"""
import inspect
import io
import re
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patterns import PATTERN_REGISTRY  # noqa: E402
from rendering import settings as render_settings  # noqa: E402
from rendering.colors import PALETTES  # noqa: E402
from rendering.renderer import render_high_res, render_to_image  # noqa: E402

# Category table of the README ("All 22 Pattern Types"), which follows the registry order.
CATEGORIES = [("Classic Tilings", 8), ("Mathematical Curves", 8), ("3D Patterns", 2), ("Advanced", 4)]
CHECK_SIZE = (400, 400)
# Cross-check runs every pattern at its defaults, except where pure Python would take minutes.
CHECK_OVERRIDES = {"Reaction-Diffusion": {"resolution": 48, "iterations": 1500}}


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower().replace("é", "e")).strip("-")


def _categories():
    names, out, i = list(PATTERN_REGISTRY), {}, 0
    assert sum(n for _c, n in CATEGORIES) == len(names)
    for cat, n in CATEGORIES:
        for name in names[i:i + n]:
            out[name] = cat
        i += n
    return out


def pattern_list():
    cats = _categories()
    out = []
    for name, cls in PATTERN_REGISTRY.items():
        out.append({
            "name": name, "slug": slug(name), "category": cats[name], "description": cls.description,
            "doc": " ".join(inspect.cleandoc(cls.__doc__ or "").split()),
            "module": f"patterns/{Path(inspect.getfile(cls)).name}", "cls": cls.__name__,
            "params": cls.get_params(),
        })
    return out


def render_spec():
    """The desktop control panel's Rendering / Effects specs and the renderer's constants (rendering/settings.py)."""
    s = render_settings
    return {
        "canvas": list(s.CANVAS_SIZE), "margin": s.MARGIN, "supersample": s.SUPERSAMPLE, "hires_scale": s.HIRES_SCALE,
        "hires_dpi": s.HIRES_DPI, "batch_count": s.BATCH_COUNT, "line_width": s.LINE_WIDTH,
        "toggles": [{"key": k, "label": label, "default": d} for k, label, d in s.RENDER_TOGGLES],
        "kaleidoscope": s.KALEIDOSCOPE,
        "effects": [{"key": k, "label": label, "default": d} for k, label, d in s.EFFECT_TOGGLES],
        "effect_strengths": s.EFFECT_STRENGTHS, "default_palette": next(iter(PALETTES)),
    }


def defaults(name):
    return {p["name"]: p["default"] for p in PATTERN_REGISTRY[name].get_params()}


def command_stats(commands):
    """Count, kinds, colour-index histogram, coordinate sum, bounding box, sum of explicit line weights and number of
    filled polygons (same order of additions as engine.js)."""
    lines = circles = polygons = 0
    total = 0.0
    colors = {}
    bx = [float("inf"), float("inf"), float("-inf"), float("-inf")]

    def pt(x, y):
        bx[0], bx[1], bx[2], bx[3] = min(bx[0], x), min(bx[1], y), max(bx[2], x), max(bx[3], y)

    weights = fills = 0
    for cmd in commands:
        kind, data, c = cmd[0], cmd[1], cmd[2]
        colors[str(c)] = colors.get(str(c), 0) + 1
        if len(cmd) > 3:
            if kind == "polygon":
                fills += bool(cmd[3])
            else:
                weights += cmd[3]
        if kind == "line":
            lines += 1
            total += data[0] + data[1] + data[2] + data[3]
            pt(data[0], data[1])
            pt(data[2], data[3])
        elif kind == "circle":
            circles += 1
            total += data[0] + data[1] + data[2]
            pt(data[0] - data[2], data[1] - data[2])
            pt(data[0] + data[2], data[1] + data[2])
        else:
            polygons += 1
            for x, y in data:
                total += x + y
                pt(x, y)
    return {"count": len(commands), "lines": lines, "circles": circles, "polygons": polygons, "sum": total,
            "bbox": bx if commands else None, "colors": colors, "weights": weights, "fills": fills}


@lru_cache(maxsize=None)
def check_case(name):
    """Python numbers for one pattern at CHECK_SIZE (defaults plus CHECK_OVERRIDES)."""
    params = {**defaults(name), **CHECK_OVERRIDES.get(name, {})}
    w, h = CHECK_SIZE
    cmds = PATTERN_REGISTRY[name]().generate(w, h, params)
    return {"name": name, "slug": slug(name), "width": w, "height": h, "params": params, "stats": command_stats(cmds)}


def render_png(name, params, settings, width, height, hires=False):
    """PNG bytes from the desktop renderer (render_to_image, or render_high_res for the 4x export)."""
    cmds = PATTERN_REGISTRY[name]().generate(width, height, {**defaults(name), **params})
    effects = {k: settings.get(k, False) for k in render_settings.EFFECT_KEYS}
    effects["kaleidoscope"] = int(effects["kaleidoscope"] or 0)
    common = dict(palette_name=settings.get("palette", next(iter(PALETTES))),
                  line_width=float(settings.get("line_width", render_settings.LINE_WIDTH["default"])),
                  glow=bool(settings.get("glow", False)), gradient=bool(settings.get("gradient", False)), **effects)
    if hires:
        img = render_high_res(cmds, width, height, **common)
    else:
        img = render_to_image(cmds, width, height, **common)
    buf = io.BytesIO()
    img.save(buf, format="PNG", **({"dpi": (render_settings.HIRES_DPI,) * 2} if hires else {}))
    return buf.getvalue(), len(cmds)
