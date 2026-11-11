"""Regression tests for pattern fixes: sliders that had no effect, the Apollonian seed, the Penrose P3 tiling.

Run: python -m pytest -q tests/test_patterns.py
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from patterns import PATTERN_REGISTRY  # noqa: E402
from rendering.renderer import render_to_image  # noqa: E402


def gen(name, w=400, h=400, **over):
    params = {p["name"]: p["default"] for p in PATTERN_REGISTRY[name].get_params()}
    params.update(over)
    return PATTERN_REGISTRY[name]().generate(w, h, params)


def lit(img):
    """Number of pixels clearly brighter than the background (ignores faint resampling halos)."""
    bg = Image.new("RGB", img.size, img.getpixel((0, 0)))
    return sum(1 for v in ImageChops.difference(img, bg).convert("L").getdata() if v > 60)


def test_grid_line_weight_thickens_lines():
    thin = render_to_image(gen("Grid", line_weight=1.0), 400, 400)
    thick = render_to_image(gen("Grid", line_weight=4.0), 400, 400)
    assert lit(thick) > 3 * lit(thin)


def test_sierpinski_fill_mode_fills_shapes():
    for mode in (0, 1, 2):
        outline = render_to_image(gen("Sierpinski", mode=mode, depth=3), 400, 400)
        filled_cmds = gen("Sierpinski", mode=mode, depth=3, fill_mode=True)
        assert any(c[0] == "polygon" and c[3] for c in filled_cmds)
        assert lit(render_to_image(filled_cmds, 400, 400)) > 2 * lit(outline)


def _endpoints(cmds):
    return [((c[1][0], c[1][1]), (c[1][2], c[1][3])) for c in cmds]


def test_space_filling_connect_off_breaks_the_path():
    seg = _endpoints(gen("Space-Filling Curves", depth=3, connect=False))
    assert len(seg) == 63
    assert all(math.dist(a[1], b[0]) > 1 for a, b in zip(seg, seg[1:]))   # gaps at every vertex
    joined = _endpoints(gen("Space-Filling Curves", depth=3))
    assert all(a[1] == b[0] for a, b in zip(joined, joined[1:]))


def test_space_filling_rounded_cuts_the_corners():
    straight = _endpoints(gen("Space-Filling Curves", depth=3))
    corners = {b[0] for a, b in zip(straight, straight[1:])
               if (a[1][0] - a[0][0]) * (b[1][1] - b[0][1]) != (a[1][1] - a[0][1]) * (b[1][0] - b[0][0])}
    rounded = _endpoints(gen("Space-Filling Curves", depth=3, rounded=0.3))
    assert corners and len(rounded) > len(straight)
    pts = {p for s in rounded for p in s}
    assert not any(math.dist(c, p) < 1e-9 for c in corners for p in pts)   # no sharp corner is visited
    assert all(a[1] == b[0] for a, b in zip(rounded, rounded[1:]))         # still one connected path


def test_chladni_threshold_outlines_the_nodal_band():
    base = gen("Chladni Figures", threshold=0.05)
    wide = gen("Chladni Figures", threshold=0.25)
    zero = [c for c in base if c[2] == 0]
    assert zero == [c for c in wide if c[2] == 0]            # the nodal lines themselves do not move
    band05 = [c for c in base if c[2] == 1]
    band25 = [c for c in wide if c[2] == 1]
    assert band05 and band25 and band05 != band25

    def mean_dist(band):  # mean distance of band points from the nearest nodal-line point
        nodal = [(c[1][0], c[1][1]) for c in zero]
        return sum(min(math.dist((c[1][0], c[1][1]), q) for q in nodal) for c in band[::7]) / len(band[::7])
    assert mean_dist(band25) > mean_dist(band05)
