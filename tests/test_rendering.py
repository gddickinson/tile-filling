"""Regression tests for bugs fixed in the desktop renderer and GUI.

Run: python -m pytest -q tests/test_rendering.py   (the GUI test is skipped where no display is available)
"""
import sys
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rendering.effects import apply_noise_grain  # noqa: E402


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
