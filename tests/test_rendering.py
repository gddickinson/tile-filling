"""Regression tests for bugs fixed in the desktop renderer and GUI.

Run: python -m pytest -q tests/test_rendering.py   (the GUI test is skipped where no display is available)
"""
import sys
from pathlib import Path

import pytest
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from patterns import PATTERN_REGISTRY  # noqa: E402
from rendering.effects import apply_noise_grain  # noqa: E402
from rendering.renderer import render_high_res  # noqa: E402


def _mean(img):
    px = list(img.convert("L").getdata())
    return sum(px) / len(px)


def test_film_grain_keeps_brightness():
    """Film grain adds noise around the image; it used to halve every pixel (ImageChops.add scale=2, offset=-64)."""
    img = Image.new("RGB", (64, 48), (200, 120, 40))
    out = apply_noise_grain(img, amount=20, seed=3)
    assert abs(_mean(out) - _mean(img)) < 2
    diff = ImageChops.difference(out, img).getextrema()
    assert all(lo == 0 and 0 < hi <= 20 for lo, hi in diff)


def test_hires_export_draws_the_whole_pattern():
    """Export Hi-Res PNG renders at 4x size: the pattern must be scaled too, not drawn 1x in the top-left corner."""
    w = h = 200
    params = {p["name"]: p["default"] for p in PATTERN_REGISTRY["Grid"].get_params()}
    cmds = PATTERN_REGISTRY["Grid"]().generate(w, h, params)
    hires = render_high_res(cmds, w, h, "Monochrome", 1.0, False, False, scale=4)
    bg = Image.new("RGB", hires.size, hires.getpixel((0, 0)))
    bbox = ImageChops.difference(hires, bg).getbbox()
    # the grid spans the margin box 40..160 px at 1x, so 160..640 px at 4x (lines are 4 px wide)
    assert hires.size == (800, 800)
    assert all(abs(a - e) <= 4 for a, e in zip(bbox, (160, 160, 640, 640))), bbox


def _tk_app():
    try:
        import tkinter
        tkinter.Tk().destroy()
    except Exception:  # no display (CI)
        pytest.skip("no display for tkinter")
    from gui.app import TileFillingApp
    return TileFillingApp()


def test_load_preset_restores_effects():
    """Save Preset writes the kaleidoscope and effect settings; Load Preset used to ignore them."""
    app = _tk_app()
    try:
        app._apply_preset({"pattern": "Truchet Tiles", "params": {"cols": 9},
                           "settings": {"palette": "Gold", "line_width": 2.0, "glow": True, "gradient": False,
                                        "kaleidoscope": 6, "gauss_glow": True, "vignette": True, "chromatic": False,
                                        "scanlines": True, "grain": False}})
        s = app.controls.get_render_settings()
        assert app.controls.get_pattern_name() == "Truchet Tiles" and app.controls.get_params()["cols"] == 9
        assert s["palette"] == "Gold" and s["line_width"] == 2.0 and s["glow"] is True
        assert s["kaleidoscope"] == 6 and app.controls.kal_label.cget("text") == "6"
        assert s["gauss_glow"] and s["vignette"] and s["scanlines"] and not s["chromatic"] and not s["grain"]
    finally:
        app.root.destroy()
