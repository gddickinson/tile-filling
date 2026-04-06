"""Post-processing effects - kaleidoscope symmetry, gaussian glow, depth effects."""

import math
from PIL import Image, ImageFilter, ImageChops, ImageDraw


def apply_kaleidoscope(img, folds=6):
    """Apply N-fold kaleidoscope symmetry to an image.

    Extracts a triangular wedge from the center, mirrors it,
    and rotates it around the center to create symmetry.
    """
    if folds < 2:
        return img

    w, h = img.size
    cx, cy = w // 2, h // 2
    result = Image.new("RGB", (w, h), img.getpixel((0, 0)))

    # We'll build the result pixel by pixel
    # For each output pixel, find the corresponding input pixel
    # by mapping to the base wedge
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

            # Map to base wedge
            wedge_idx = int(angle / wedge_angle)
            local_angle = angle - wedge_idx * wedge_angle

            # Mirror odd wedges
            if wedge_idx % 2 == 1:
                local_angle = wedge_angle - local_angle

            # Map back to source coordinates
            src_x = int(cx + r * math.cos(local_angle))
            src_y = int(cy + r * math.sin(local_angle))

            if 0 <= src_x < w and 0 <= src_y < h:
                pixels_out[x, y] = pixels_in[src_x, src_y]

    return result


def apply_gaussian_glow(img, radius=8, intensity=0.6):
    """Apply proper gaussian blur glow effect.

    Creates a blurred copy of the image and composites it
    behind the original for a soft bloom/glow effect.
    """
    # Create the glow layer by blurring the image
    glow = img.filter(ImageFilter.GaussianBlur(radius=radius))

    # Brighten the glow layer
    from PIL import ImageEnhance
    enhancer = ImageEnhance.Brightness(glow)
    glow = enhancer.enhance(1.0 + intensity)

    # Screen blend: result = 1 - (1-a)(1-b), approximated with ImageChops
    result = ImageChops.screen(img, glow)

    return result


def apply_vignette(img, strength=0.5):
    """Apply a vignette (darkening at edges) effect."""
    w, h = img.size
    cx, cy = w / 2, h / 2
    max_r = math.sqrt(cx * cx + cy * cy)

    mask = Image.new("L", (w, h), 255)
    mask_draw = ImageDraw.Draw(mask)

    # Draw concentric dark ellipses
    for r_frac in range(100):
        r = r_frac / 100.0
        alpha = int(255 * (1 - strength * r * r))
        alpha = max(0, min(255, alpha))
        rx = int(cx * (1 + r))
        ry = int(cy * (1 + r))
        # Fill from outside in
        if r_frac > 30:
            ring_alpha = int(255 * max(0, 1 - strength * (r_frac / 100.0) ** 2))
            # Simple radial gradient using ellipses
            pass

    # Simpler approach: pixel-based vignette
    pixels = mask.load()
    for y in range(h):
        for x in range(w):
            dx = (x - cx) / cx
            dy = (y - cy) / cy
            d = math.sqrt(dx * dx + dy * dy)
            factor = max(0, 1 - strength * d * d)
            pixels[x, y] = int(255 * factor)

    # Apply mask
    r, g, b = img.split()
    r = Image.composite(r, Image.new("L", (w, h), 0), mask)
    g = Image.composite(g, Image.new("L", (w, h), 0), mask)
    b = Image.composite(b, Image.new("L", (w, h), 0), mask)

    return Image.merge("RGB", (r, g, b))
