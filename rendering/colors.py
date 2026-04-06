"""Color palettes and gradient utilities for tile rendering."""


PALETTES = {
    "Monochrome": {
        "background": "#1a1a2e",
        "lines": ["#e0e0e0"],
        "accent": "#ffffff",
    },
    "Blueprint": {
        "background": "#0a1628",
        "lines": ["#4a90d9", "#6bb3f0"],
        "accent": "#ffffff",
    },
    "Cyberpunk": {
        "background": "#0d0221",
        "lines": ["#ff00ff", "#00ffff", "#ff6600"],
        "accent": "#ffff00",
    },
    "Ocean": {
        "background": "#0a0e27",
        "lines": ["#0077b6", "#00b4d8", "#90e0ef"],
        "accent": "#caf0f8",
    },
    "Sunset": {
        "background": "#1a0a2e",
        "lines": ["#ff6b6b", "#ffa36b", "#ffe66d"],
        "accent": "#ffffff",
    },
    "Forest": {
        "background": "#0a1a0a",
        "lines": ["#2d6a4f", "#52b788", "#95d5b2"],
        "accent": "#d8f3dc",
    },
    "Gold": {
        "background": "#1a1a0a",
        "lines": ["#b8860b", "#daa520", "#ffd700"],
        "accent": "#fffff0",
    },
    "Neon": {
        "background": "#000000",
        "lines": ["#39ff14", "#ff073a", "#0ff0fc", "#ff6ec7"],
        "accent": "#ffffff",
    },
    "Minimal White": {
        "background": "#2d2d2d",
        "lines": ["#cccccc"],
        "accent": "#ffffff",
    },
    "Pastel": {
        "background": "#2b2d42",
        "lines": ["#f4a261", "#e76f51", "#2a9d8f", "#e9c46a"],
        "accent": "#f1faee",
    },
    "Fire": {
        "background": "#1a0000",
        "lines": ["#8b0000", "#ff4500", "#ff8c00", "#ffd700"],
        "accent": "#ffffff",
    },
    "Arctic": {
        "background": "#0b1320",
        "lines": ["#a8dadc", "#457b9d", "#e0fbfc"],
        "accent": "#f1faee",
    },
}


def hex_to_rgb(hex_color: str):
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def lerp_color(c1: str, c2: str, t: float) -> str:
    """Linearly interpolate between two hex colors."""
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    r = int(r1 + t * (r2 - r1))
    g = int(g1 + t * (g2 - g1))
    b = int(b1 + t * (b2 - b1))
    return rgb_to_hex(r, g, b)


def color_with_alpha(hex_color: str, alpha: float) -> str:
    """Blend hex_color toward black by alpha (0=transparent, 1=opaque)."""
    r, g, b = hex_to_rgb(hex_color)
    r = int(r * alpha)
    g = int(g * alpha)
    b = int(b * alpha)
    return rgb_to_hex(r, g, b)


def get_line_color(palette: dict, index: int) -> str:
    """Get a line color from palette, cycling through available colors."""
    colors = palette["lines"]
    return colors[index % len(colors)]


def gradient_color(palette: dict, t: float) -> str:
    """Get a color from palette gradient at position t (0-1)."""
    colors = palette["lines"]
    if len(colors) == 1:
        return colors[0]
    segment = t * (len(colors) - 1)
    i = int(segment)
    frac = segment - i
    if i >= len(colors) - 1:
        return colors[-1]
    return lerp_color(colors[i], colors[i + 1], frac)
