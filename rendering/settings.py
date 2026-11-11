"""Render settings shared by the desktop GUI and the web interface (no tkinter import).

The control panel (gui/controls.py) builds its "Rendering" and "Effects" widgets from these specs, the renderer
(rendering/renderer.py) takes its post-processing strengths from EFFECT_STRENGTHS, and web/app.py serves both to the
browser so the web app uses the same ranges, defaults and labels.
"""

CANVAS_SIZE = (800, 800)      # initial canvas width/height of the desktop window (it follows window resizes)
MARGIN = 40                   # border margin passed to every pattern's generate()
SUPERSAMPLE = 2               # render at 2x and downscale (anti-aliasing) for the preview and standard export
HIRES_SCALE = 4               # "Export Hi-Res PNG": 4x size, line width x4, no supersampling, saved at 300 DPI
HIRES_DPI = 300
BATCH_COUNT = 10              # "Batch Random (10x)"

LINE_WIDTH = {"label": "Line Width", "min": 0.5, "max": 5.0, "default": 1.0}
RENDER_TOGGLES = [            # (key, label, default)
    ("glow", "Glow Effect", False),
    ("gradient", "Gradient Colors", False),
]
KALEIDOSCOPE = {"label": "Kaleidoscope Folds (0=off)", "min": 0, "max": 12, "default": 0}
EFFECT_TOGGLES = [            # (key, label, default), in the order they are applied after the kaleidoscope
    ("gauss_glow", "Gaussian Bloom", False),
    ("vignette", "Vignette", False),
    ("chromatic", "Chromatic Aberration", False),
    ("scanlines", "Scan Lines", False),
    ("grain", "Film Grain", False),
]
EFFECT_KEYS = ["kaleidoscope"] + [k for k, _label, _default in EFFECT_TOGGLES]

# Strengths used by render_to_image for each post-processing effect.
EFFECT_STRENGTHS = {
    "gauss_glow": {"radius": 6, "intensity": 0.5},
    "vignette": {"strength": 0.6},
    "chromatic": {"offset": 3},
    "scanlines": {"spacing": 3, "opacity": 0.3},
    "grain": {"amount": 20},
}
