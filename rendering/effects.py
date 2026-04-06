"""Post-processing effects - kaleidoscope, glow, chromatic aberration, scan lines, etc."""

import math
import random
from PIL import Image, ImageFilter, ImageChops, ImageDraw, ImageEnhance


def apply_kaleidoscope(img, folds=6):
    """Apply N-fold kaleidoscope symmetry to an image."""
    if folds < 2:
        return img

    w, h = img.size
    cx, cy = w // 2, h // 2
    result = Image.new("RGB", (w, h), img.getpixel((0, 0)))
    wedge_angle = 2 * math.pi / folds

    pixels_in = img.load()
    pixels_out = result.load()

    for y in range(h):
        for x in range(w):
            dx = x - cx
            dy = y - cy
            r = math.sqrt(dx * dx + dy * dy)
            if r == 0:
                pixels_out[x, y] = pixels_in[cx, cy]
                continue

            angle = math.atan2(dy, dx)
            if angle < 0:
                angle += 2 * math.pi

            wedge_idx = int(angle / wedge_angle)
            local_angle = angle - wedge_idx * wedge_angle

            if wedge_idx % 2 == 1:
                local_angle = wedge_angle - local_angle

            src_x = int(cx + r * math.cos(local_angle))
            src_y = int(cy + r * math.sin(local_angle))

            if 0 <= src_x < w and 0 <= src_y < h:
                pixels_out[x, y] = pixels_in[src_x, src_y]

    return result


def apply_gaussian_glow(img, radius=8, intensity=0.6):
    """Apply gaussian blur bloom effect."""
    glow = img.filter(ImageFilter.GaussianBlur(radius=radius))
    enhancer = ImageEnhance.Brightness(glow)
    glow = enhancer.enhance(1.0 + intensity)
    return ImageChops.screen(img, glow)


def apply_vignette(img, strength=0.5):
    """Apply vignette (darkening at edges)."""
    w, h = img.size
    cx, cy = w / 2, h / 2

    mask = Image.new("L", (w, h), 255)
    pixels = mask.load()
    for y in range(h):
        for x in range(w):
            dx = (x - cx) / cx
            dy = (y - cy) / cy
            d = math.sqrt(dx * dx + dy * dy)
            factor = max(0, 1 - strength * d * d)
            pixels[x, y] = int(255 * factor)

    r, g, b = img.split()
    black = Image.new("L", (w, h), 0)
    r = Image.composite(r, black, mask)
    g = Image.composite(g, black, mask)
    b = Image.composite(b, black, mask)
    return Image.merge("RGB", (r, g, b))


def apply_chromatic_aberration(img, offset=3):
    """Offset R/G/B channels to create prismatic color fringing."""
    r, g, b = img.split()

    # Shift red channel left, blue channel right
    r_shifted = Image.new("L", img.size, 0)
    b_shifted = Image.new("L", img.size, 0)

    r_shifted.paste(r, (-offset, 0))
    b_shifted.paste(b, (offset, 0))

    return Image.merge("RGB", (r_shifted, g, b_shifted))


def apply_scan_lines(img, spacing=3, opacity=0.4):
    """Apply CRT-style horizontal scan lines."""
    w, h = img.size
    overlay = Image.new("RGB", (w, h), (0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for y in range(0, h, spacing):
        draw.line([(0, y), (w, y)], fill=(0, 0, 0), width=1)

    # Blend: result = img * (1 - opacity) + overlay * opacity
    # Using ImageChops for speed
    return ImageChops.multiply(
        img,
        _create_scanline_mask(w, h, spacing, opacity)
    )


def _create_scanline_mask(w, h, spacing, opacity):
    """Create a scanline multiplier mask."""
    mask = Image.new("RGB", (w, h), (255, 255, 255))
    pixels = mask.load()
    dark = int(255 * (1 - opacity))
    for y in range(h):
        if y % spacing == 0:
            for x in range(w):
                pixels[x, y] = (dark, dark, dark)
    return mask


def apply_noise_grain(img, amount=30, seed=None):
    """Apply film grain noise overlay."""
    w, h = img.size
    if seed is not None:
        random.seed(seed)

    noise = Image.new("RGB", (w, h))
    pixels = noise.load()
    for y in range(h):
        for x in range(w):
            v = random.randint(-amount, amount)
            pixels[x, y] = (128 + v, 128 + v, 128 + v)

    # Apply as soft light blend
    # Simplified: just add noise scaled down
    return ImageChops.add(img, noise, scale=2, offset=-64)


def apply_background_gradient(img, color1, color2, mode="radial"):
    """Replace flat background with a gradient.

    Args:
        img: Source image
        color1: Center/top color as hex string
        color2: Edge/bottom color as hex string
        mode: "radial" or "linear"
    """
    w, h = img.size
    gradient = Image.new("RGB", (w, h))
    pixels = gradient.load()

    r1, g1, b1 = _hex_to_rgb(color1)
    r2, g2, b2 = _hex_to_rgb(color2)

    cx, cy = w / 2, h / 2
    max_r = math.sqrt(cx * cx + cy * cy)

    for y in range(h):
        for x in range(w):
            if mode == "radial":
                d = math.sqrt((x - cx) ** 2 + (y - cy) ** 2) / max_r
            else:
                d = y / h

            d = min(1.0, d)
            r = int(r1 + (r2 - r1) * d)
            g = int(g1 + (g2 - g1) * d)
            b = int(b1 + (b2 - b1) * d)
            pixels[x, y] = (r, g, b)

    # Screen blend gradient with image (brightens where image has content)
    return ImageChops.screen(gradient, img)


def _hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
