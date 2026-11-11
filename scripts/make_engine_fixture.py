"""Reference numbers from the repo's Python code for the JS engine tests (web/static/*.test.mjs).

Writes tests/fixtures/engine_fixture.json (pattern commands, palettes, colour helpers, L-system presets) and
tests/fixtures/effects_fixture.json (each post-processing effect of rendering/effects.py on a small test image).
tests/test_web.py regenerates both and checks the committed files are still current (numbers compared with a tolerance).

Run: python scripts/make_engine_fixture.py [--check]
"""
import argparse
import base64
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from PIL import Image  # noqa: E402

from patterns import PATTERN_REGISTRY  # noqa: E402
from patterns.lsystem import PRESETS  # noqa: E402
from rendering import effects  # noqa: E402
from rendering.colors import PALETTES, gradient_color, lerp_color  # noqa: E402
from rendering.settings import EFFECT_STRENGTHS  # noqa: E402
from web.catalog import command_stats, defaults  # noqa: E402

FIX = ROOT / "tests" / "fixtures"
SIZE = (360, 320)  # not square, so width/height mix-ups show
# (pattern, overrides, global_seed): global_seed seeds Python's module-level random first (Grid jitter uses it unseeded)
VARIANTS = [
    ("Grid", {"jitter": 0.5, "cols": 7}, 7), ("Grid", {"line_weight": 2.5, "rows": 4}, None),
    *[("Sierpinski", {"mode": m, "depth": 3, "fill_mode": True, "rotation": 15.0}, None) for m in (0, 1, 2)],
    ("Space-Filling Curves", {"depth": 3, "rounded": 0.3}, None), ("Space-Filling Curves", {"depth": 3, "connect": False}, None),
    ("Space-Filling Curves", {"curve_type": 2, "depth": 2, "rounded": 0.5}, None),
    ("Space-Filling Curves", {"curve_type": 1, "depth": 2, "connect": False, "rounded": 0.25}, None),
    ("Chladni Figures", {"threshold": 0.2, "resolution": 60}, None),
    ("Chladni Figures", {"mode": 1, "threshold": 0.12, "resolution": 70}, None), ("Decorated Grid", {"decoration": 5, "rotation": 20.0, "cols": 5}, None),
    ("Islamic Star", {"rosette": True, "points": 7}, None), ("Islamic Star", {"points": 12, "interlace": 0.0}, None),
    ("Penrose Tiling", {"draw_triangles": True, "initial_shape": 1, "subdivisions": 4}, None),
    ("Truchet Tiles", {"style": 1, "seed": 7}, None), ("Truchet Tiles", {"style": 2, "cols": 9, "rows": 6}, None),
    ("Voronoi", {"dual_mode": True, "num_points": 80, "relax_steps": 1}, None), ("Voronoi", {"num_points": 7, "seed": 0}, None),
    ("Hexagonal", {"pointy_top": False, "decoration": 4, "size": 22}, None),
    ("Sierpinski", {"mode": 1, "depth": 3}, None), ("Sierpinski", {"mode": 2, "depth": 3, "rotation": 30.0}, None),
    ("Sierpinski", {"rotation": 45.0, "depth": 4}, None),
    ("Space-Filling Curves", {"curve_type": 1, "depth": 3}, None), ("Space-Filling Curves", {"curve_type": 2, "depth": 4}, None),
    ("Moiré", {"style": 0, "layers": 3}, None), ("Moiré", {"style": 2, "count": 40, "angle_offset": 12.5}, None),
    ("Spirograph", {"mode": 2, "multi": 3, "resolution": 800, "r": 25}, None),
    ("Strange Attractors", {"attractor": 0, "iterations": 5, "skip_lines": 3}, None),
    ("Strange Attractors", {"attractor": 1, "iterations": 5, "a": 2.01, "b": -2.53, "c": 1.61, "d": -0.33}, None),
    ("Strange Attractors", {"attractor": 2, "iterations": 5}, None),
    *[("L-System", {"preset": i, "iterations": 3, "angle_adjust": 2.5 * i}, None) for i in range(1, len(PRESETS))],
    ("Lissajous", {"harmonograph": True, "layers": 2, "damping": 0.005, "resolution": 1500}, None),
    ("Lissajous", {"damping": 0.01, "freq_x": 5, "freq_y": 7, "resolution": 900}, None),
    *[("Guilloche", {"shape": s, "waves": 20, "resolution": 100}, None) for s in (1, 2, 3)],
    ("Phyllotaxis", {"style": 0}, None), ("Phyllotaxis", {"style": 1, "angle_mult": 1.02}, None),
    ("Phyllotaxis", {"style": 3, "points": 300}, None),
    ("Isometric Cubes", {"height_mode": 0, "seed": 9}, None),
    ("Isometric Cubes", {"height_mode": 2, "rotation": 20.0, "show_hidden": True}, None),
    *[("3D Wireframe", {"surface": s, "resolution": 12, "rot_z": 40.0}, None) for s in (1, 2, 3, 4)],
    ("Flow Field", {"particles": 100, "steps": 40, "octaves": 2, "seed": 3, "curl": 2.2}, None),
    ("Apollonian Gasket", {"initial": 1, "depth": 4}, None), ("Apollonian Gasket", {"initial": 2, "depth": 4}, None),
    ("Chladni Figures", {"mode": 1, "resolution": 80, "m": 4, "n": 2}, None),
    ("Reaction-Diffusion", {"resolution": 40, "iterations": 800, "seed_count": 8, "contours": 2, "feed": 30, "kill": 57}, None),
]
CHAOTIC = {("Strange Attractors", 0), ("Strange Attractors", 1), ("Strange Attractors", 2)}  # libm-sensitive orbits
HEAVY = {"Reaction-Diffusion": {"resolution": 48, "iterations": 1500}}  # keep the "defaults" case quick in Python


def attractor_orbit(p, n=20):
    """First points of the raw orbit (before any scaling), for the chaotic attractor cases."""
    a = PATTERN_REGISTRY["Strange Attractors"]()
    if p["attractor"] == 0:
        return a._clifford(p["a"], p["b"], p["c"], p["d"], n)
    if p["attractor"] == 1:
        return a._dejong(p["a"], p["b"], p["c"], p["d"], n)
    return a._lorenz(n)


def pattern_cases():
    cases = [(name, dict(HEAVY.get(name, {})), None) for name in PATTERN_REGISTRY] + VARIANTS
    out = []
    w, h = SIZE
    for name, over, gseed in cases:
        params = {**defaults(name), **over}
        if gseed is not None:
            random.seed(gseed)
        cmds = PATTERN_REGISTRY[name]().generate(w, h, params)
        n = len(cmds)
        idx = sorted({0, 1, 2, *[k * (n - 1) // 9 for k in range(10)]} & set(range(n)))
        out.append({"name": name, "params": params, "global_seed": gseed, "width": w, "height": h,
                    "chaotic": (name, params.get("attractor")) in CHAOTIC, "stats": command_stats(cmds),
                    "samples": [[i, cmds[i][0], [list(v) if isinstance(v, tuple) else v for v in cmds[i][1]],
                                 *cmds[i][2:]] for i in idx]})
        if out[-1]["chaotic"]:
            out[-1]["orbit"] = attractor_orbit(params)
    return out


def engine_fixture():
    colors = [[name, t, gradient_color(p, t)] for name, p in PALETTES.items() for t in (0, 0.13, 0.5, 0.77, 0.999, 1)]
    lerps = [[a, b, t, lerp_color(a, b, t)] for a, b in (("#ff00ff", "#00ffff"), ("#0a1628", "#e0fbfc")) for t in (0.1, 0.5, 0.97)]
    return {"size": list(SIZE), "palettes": PALETTES, "gradient": colors, "lerp": lerps, "lsystem_presets": PRESETS,
            "registry": list(PATTERN_REGISTRY), "cases": pattern_cases()}


def test_image(w=48, h=36):
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            px[x, y] = ((x * 37 + y * 11) % 256, (x * x + 3 * y) % 256, (x * y * 5 + 20) % 256) if (x + y) % 9 else (0, 0, 0)
    return img


def effects_fixture():
    img = test_image()
    b64 = lambda im: base64.b64encode(im.tobytes()).decode()  # noqa: E731
    s = EFFECT_STRENGTHS
    out = {"width": img.width, "height": img.height, "input": b64(img), "strengths": s, "results": {
        "kaleidoscope6": b64(effects.apply_kaleidoscope(img, 6)), "kaleidoscope5": b64(effects.apply_kaleidoscope(img, 5)),
        "gauss_glow": b64(effects.apply_gaussian_glow(img, **s["gauss_glow"])),
        "vignette": b64(effects.apply_vignette(img, **s["vignette"])),
        "chromatic": b64(effects.apply_chromatic_aberration(img, **s["chromatic"])),
        "scanlines": b64(effects.apply_scan_lines(img, **s["scanlines"])),
        "grain_seed11": b64(effects.apply_noise_grain(img, **s["grain"], seed=11)),
    }}
    return out


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="only print the case count")
    a = ap.parse_args()
    eng, fx = engine_fixture(), effects_fixture()
    if a.check:
        print(f"{len(eng['cases'])} pattern cases, {len(fx['results'])} effects")
        return
    FIX.mkdir(parents=True, exist_ok=True)
    write(FIX / "engine_fixture.json", eng)
    write(FIX / "effects_fixture.json", fx)
    print(f"wrote {len(eng['cases'])} pattern cases and {len(fx['results'])} effect results to {FIX}")


if __name__ == "__main__":
    main()
