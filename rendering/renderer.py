"""Rendering engine - draws pattern commands to PIL images and tkinter canvases."""

from PIL import Image, ImageDraw
from rendering.colors import PALETTES, get_line_color, gradient_color, hex_to_rgb


def render_to_image(
    commands,
    width,
    height,
    palette_name="Monochrome",
    line_width=1.0,
    glow=False,
    gradient=False,
    supersample=2,
    kaleidoscope=0,
    gauss_glow=False,
    vignette=False,
    chromatic=False,
    scanlines=False,
    grain=False,
):
    """Render drawing commands to a PIL Image.

    Args:
        commands: List of DrawCommand tuples from pattern generators
        width: Output image width
        height: Output image height
        palette_name: Name of color palette from PALETTES
        line_width: Base line width in pixels
        glow: Whether to add glow effect (draw wider translucent lines behind)
        gradient: Whether to color lines by position instead of index
        supersample: Render at Nx resolution and downscale for anti-aliasing
        kaleidoscope: Number of symmetry folds (0=off)
        gauss_glow: Apply gaussian blur bloom effect
        vignette: Apply edge darkening vignette

    Returns:
        PIL.Image.Image
    """
    palette = PALETTES.get(palette_name, PALETTES["Monochrome"])
    bg = palette["background"]

    ss = supersample
    sw, sh = int(width * ss), int(height * ss)
    s_lw = line_width * ss

    img = Image.new("RGB", (sw, sh), bg)
    draw = ImageDraw.Draw(img)

    if glow:
        _draw_glow_pass(draw, commands, palette, s_lw, sw, sh, gradient, ss)

    _draw_main_pass(draw, commands, palette, s_lw, sw, sh, gradient, ss)

    if ss > 1:
        img = img.resize((width, height), Image.LANCZOS)

    # Post-processing effects
    if kaleidoscope >= 2:
        from rendering.effects import apply_kaleidoscope
        img = apply_kaleidoscope(img, kaleidoscope)

    if gauss_glow:
        from rendering.effects import apply_gaussian_glow
        img = apply_gaussian_glow(img, radius=6, intensity=0.5)

    if vignette:
        from rendering.effects import apply_vignette
        img = apply_vignette(img, strength=0.6)

    if chromatic:
        from rendering.effects import apply_chromatic_aberration
        img = apply_chromatic_aberration(img, offset=3)

    if scanlines:
        from rendering.effects import apply_scan_lines
        img = apply_scan_lines(img, spacing=3, opacity=0.3)

    if grain:
        from rendering.effects import apply_noise_grain
        img = apply_noise_grain(img, amount=20)

    return img


def _draw_main_pass(draw, commands, palette, line_width, sw, sh, gradient, ss):
    """Draw main lines."""
    total = len(commands) if len(commands) > 0 else 1
    for idx, cmd in enumerate(commands):
        cmd_type = cmd[0]
        data = cmd[1]
        color_idx = cmd[2]

        if gradient:
            t = idx / total
            color = gradient_color(palette, t)
        else:
            color = get_line_color(palette, color_idx)

        if cmd_type == "line":
            x1, y1, x2, y2 = data[0] * ss, data[1] * ss, data[2] * ss, data[3] * ss
            draw.line([(x1, y1), (x2, y2)], fill=color, width=max(1, int(line_width)))

        elif cmd_type == "circle":
            cx, cy, r = data[0] * ss, data[1] * ss, data[2] * ss
            bbox = [cx - r, cy - r, cx + r, cy + r]
            draw.ellipse(bbox, outline=color, width=max(1, int(line_width)))

        elif cmd_type == "polygon":
            points = [(p[0] * ss, p[1] * ss) for p in data]
            if len(points) >= 2:
                draw.polygon(points, outline=color)


def _draw_glow_pass(draw, commands, palette, line_width, sw, sh, gradient, ss):
    """Draw a wider, dimmer pass behind lines for glow effect."""
    total = len(commands) if len(commands) > 0 else 1
    glow_width = max(3, int(line_width * 3))

    for idx, cmd in enumerate(commands):
        cmd_type = cmd[0]
        data = cmd[1]
        color_idx = cmd[2]

        if gradient:
            t = idx / total
            base_color = gradient_color(palette, t)
        else:
            base_color = get_line_color(palette, color_idx)

        # Dim the color for glow
        r, g, b = hex_to_rgb(base_color)
        glow_color = f"#{r // 4:02x}{g // 4:02x}{b // 4:02x}"

        if cmd_type == "line":
            x1, y1, x2, y2 = data[0] * ss, data[1] * ss, data[2] * ss, data[3] * ss
            draw.line([(x1, y1), (x2, y2)], fill=glow_color, width=glow_width)

        elif cmd_type == "circle":
            cx, cy, r_val = data[0] * ss, data[1] * ss, data[2] * ss
            bbox = [cx - r_val - 2, cy - r_val - 2, cx + r_val + 2, cy + r_val + 2]
            draw.ellipse(bbox, outline=glow_color, width=glow_width)


def render_high_res(commands, width, height, palette_name, line_width, glow, gradient,
                    scale=4, **effects):
    """Render at high resolution for export."""
    return render_to_image(
        commands,
        width * scale,
        height * scale,
        palette_name,
        line_width * scale,
        glow,
        gradient,
        supersample=1,
        **effects,
    )
