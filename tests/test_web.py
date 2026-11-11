"""Web interface tests: every exported endpoint answers, the static build is complete, and the JS engine tests pass.

Run: python -m pytest -q tests/test_web.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from web.app import STATIC, STATIC_ENDPOINTS, app  # noqa: E402

client = TestClient(app)


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200 and "static/main.js" in r.text


@pytest.mark.parametrize("path", STATIC_ENDPOINTS)
def test_endpoint(path):
    r = client.get("/api" + path)
    assert r.status_code == 200, r.text
    assert r.json() is not None


def test_static_build(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_static
    build_static.build(tmp_path / "site")
    assert (tmp_path / "site" / "index.html").read_text().count("APP_STATIC") == 1
    for path in STATIC_ENDPOINTS:
        assert (tmp_path / "site" / "api" / (path.strip("/") + ".json")).exists()


def test_static_assets_referenced_exist():
    html = (STATIC / "index.html").read_text()
    for name in ("style.css", "main.js"):
        assert f"static/{name}" in html and (STATIC / name).exists()


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_js_engine():
    tests = sorted(STATIC.glob("*.test.mjs"))
    for t in tests:
        r = subprocess.run(["node", str(t)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr


# --- Tile-filling API tests -----------------------------------------------------------------------------------------
import base64  # noqa: E402
import math  # noqa: E402

from patterns import PATTERN_REGISTRY  # noqa: E402
from rendering import settings as render_settings  # noqa: E402
from rendering.colors import PALETTES  # noqa: E402
from web.catalog import command_stats, defaults  # noqa: E402

FIX = ROOT / "tests" / "fixtures"


def test_web_stack_does_not_import_tkinter():
    code = "import sys; import web.app; sys.exit('tkinter' in sys.modules)"
    assert subprocess.run([sys.executable, "-c", code], cwd=ROOT).returncode == 0


def test_patterns_come_from_registry():
    d = client.get("/api/patterns").json()
    assert [p["name"] for p in d] == list(PATTERN_REGISTRY)
    for p in d:
        assert p["params"] == PATTERN_REGISTRY[p["name"]].get_params()
        assert p["description"] == PATTERN_REGISTRY[p["name"]].description
    assert len({p["slug"] for p in d}) == 22
    assert client.get("/api/palettes").json() == PALETTES


def test_render_spec_is_settings_module():
    d = client.get("/api/render-spec").json()
    assert d["line_width"] == render_settings.LINE_WIDTH and d["kaleidoscope"] == render_settings.KALEIDOSCOPE
    assert [e["key"] for e in d["effects"]] == render_settings.EFFECT_KEYS[1:]
    assert d["effect_strengths"] == render_settings.EFFECT_STRENGTHS


def test_check_numbers_are_python():
    d = client.get("/api/check").json()
    assert len(d["cases"]) == 22
    case = next(c for c in d["cases"] if c["name"] == "Truchet Tiles")
    cmds = PATTERN_REGISTRY["Truchet Tiles"]().generate(case["width"], case["height"], defaults("Truchet Tiles"))
    assert case["stats"] == command_stats(cmds)
    assert all(c["stats"]["count"] > 0 for c in d["cases"])


def test_render_png():
    r = client.post("/api/render", json={"pattern": "Hexagonal", "settings": {"palette": "Sunset", "vignette": True},
                                         "width": 200, "height": 150})
    assert r.status_code == 200 and r.content[:8] == b"\x89PNG\r\n\x1a\n" and int(r.headers["x-commands"]) > 0
    assert client.post("/api/render", json={"pattern": "Nope"}).status_code == 404
    assert client.post("/api/render", json={"pattern": "Grid", "width": 9999}).status_code == 422


def _close(a, b, path=""):
    """Recursive comparison with rtol 1e-9 for floats (libm differs in the last digit between platforms)."""
    if isinstance(a, float) or isinstance(b, float):
        assert math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9), f"{path}: {a} != {b}"
    elif isinstance(a, dict):
        assert a.keys() == b.keys(), path
        for k in a:
            _close(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, (list, tuple)):
        assert len(a) == len(b), path
        for i, (x, y) in enumerate(zip(a, b)):
            _close(x, y, f"{path}[{i}]")
    else:
        assert a == b, f"{path}: {a} != {b}"


def test_fixtures_are_current():
    """tests/fixtures/*.json (read by the node tests) still match the Python code."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import json
    import make_engine_fixture as mk
    now, emb = mk.engine_fixture(), json.loads((FIX / "engine_fixture.json").read_text())
    for c_now, c_emb in zip(now["cases"], emb["cases"]):
        if c_now["chaotic"]:  # orbit samples after the first few steps are libm-sensitive; compare the head only
            _close(c_now["orbit"][:5], c_emb["orbit"][:5], c_now["name"])
            assert c_now["stats"]["count"] == c_emb["stats"]["count"]
            continue
        _close(json.loads(json.dumps(c_now)), c_emb, c_now["name"])
    assert len(now["cases"]) == len(emb["cases"])
    _close({k: v for k, v in now.items() if k != "cases"}, {k: v for k, v in json.loads(json.dumps(emb)).items() if k != "cases"})
    fx_now, fx_emb = mk.effects_fixture(), json.loads((FIX / "effects_fixture.json").read_text())
    for name, b64 in fx_now["results"].items():
        a, b = base64.b64decode(b64), base64.b64decode(fx_emb["results"][name])
        diff = sum(x != y for x, y in zip(a, b))
        assert len(a) == len(b) and diff <= (0.01 * len(a) if name.startswith("kaleidoscope") else 0), name
