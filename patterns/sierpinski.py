"""Sierpinski triangle and carpet fractal patterns."""

import math
from typing import Dict, List
from patterns.base import BasePattern, DrawCommand
from utils.geometry import midpoint


class SierpinskiPattern(BasePattern):
    """Fractal subdivision patterns - Sierpinski triangle and carpet."""

    name = "Sierpinski"
    description = "Fractal triangle and carpet subdivision patterns"

    @staticmethod
    def get_params() -> List[Dict]:
        return [
            {"name": "depth", "label": "Recursion Depth", "type": "int", "min": 1, "max": 8, "default": 5},
            {"name": "mode", "label": "Mode (0=Tri,1=Carpet,2=Hex)", "type": "int", "min": 0, "max": 2, "default": 0},
            {"name": "fill_mode", "label": "Fill Outlines", "type": "bool", "min": 0, "max": 1, "default": False},
            {"name": "rotation", "label": "Rotation (deg)", "type": "float", "min": 0, "max": 360, "default": 0},
        ]

    def generate(self, width: float, height: float, params: Dict, margin: float = 40) -> List[DrawCommand]:
        depth = params.get("depth", 5)
        mode = params.get("mode", 0)
        rotation = math.radians(params.get("rotation", 0))

        commands = []
        cx = width / 2
        cy = height / 2
        size = min(width, height) - 2 * margin

        if mode == 0:
            self._sierpinski_triangle(commands, cx, cy, size, depth, rotation)
        elif mode == 1:
            self._sierpinski_carpet(commands, cx, cy, size, depth)
        else:
            self._sierpinski_hexagon(commands, cx, cy, size, depth, rotation)

        return commands

    def _sierpinski_triangle(self, commands, cx, cy, size, depth, rotation):
        """Generate Sierpinski triangle."""
        h = size * math.sqrt(3) / 2
        # Equilateral triangle vertices centered at (cx, cy)
        p1 = (cx, cy - h * 2 / 3)
        p2 = (cx - size / 2, cy + h / 3)
        p3 = (cx + size / 2, cy + h / 3)

        if rotation != 0:
            cos_r = math.cos(rotation)
            sin_r = math.sin(rotation)
            def rot(p):
                dx, dy = p[0] - cx, p[1] - cy
                return (cx + dx * cos_r - dy * sin_r, cy + dx * sin_r + dy * cos_r)
            p1, p2, p3 = rot(p1), rot(p2), rot(p3)

        self._subdivide_triangle(commands, p1, p2, p3, depth)

    def _subdivide_triangle(self, commands, p1, p2, p3, depth):
        """Recursively subdivide triangle."""
        if depth == 0:
            commands.append(("line", (*p1, *p2), 0))
            commands.append(("line", (*p2, *p3), 0))
            commands.append(("line", (*p3, *p1), 0))
            return

        m12 = midpoint(p1, p2)
        m23 = midpoint(p2, p3)
        m31 = midpoint(p3, p1)

        # Three corner triangles (skip the middle one)
        self._subdivide_triangle(commands, p1, m12, m31, depth - 1)
        self._subdivide_triangle(commands, m12, p2, m23, depth - 1)
        self._subdivide_triangle(commands, m31, m23, p3, depth - 1)

    def _sierpinski_carpet(self, commands, cx, cy, size, depth):
        """Generate Sierpinski carpet (square version)."""
        x0 = cx - size / 2
        y0 = cy - size / 2
        self._subdivide_carpet(commands, x0, y0, size, depth)

    def _subdivide_carpet(self, commands, x, y, size, depth):
        """Recursively subdivide square for carpet."""
        if depth == 0:
            # Draw square outline
            commands.append(("line", (x, y, x + size, y), 0))
            commands.append(("line", (x + size, y, x + size, y + size), 0))
            commands.append(("line", (x + size, y + size, x, y + size), 0))
            commands.append(("line", (x, y + size, x, y), 0))
            return

        s = size / 3
        for i in range(3):
            for j in range(3):
                if i == 1 and j == 1:
                    # Draw the removed center square outline
                    sx, sy = x + s, y + s
                    commands.append(("line", (sx, sy, sx + s, sy), 1))
                    commands.append(("line", (sx + s, sy, sx + s, sy + s), 1))
                    commands.append(("line", (sx + s, sy + s, sx, sy + s), 1))
                    commands.append(("line", (sx, sy + s, sx, sy), 1))
                    continue
                self._subdivide_carpet(commands, x + i * s, y + j * s, s, depth - 1)

    def _sierpinski_hexagon(self, commands, cx, cy, size, depth, rotation):
        """Generate Sierpinski hexagon variation."""
        r = size / 2
        verts = []
        for i in range(6):
            angle = rotation + i * math.pi / 3 - math.pi / 6
            verts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))

        self._subdivide_hex(commands, verts, depth)

    def _subdivide_hex(self, commands, verts, depth):
        """Recursively subdivide hexagon."""
        if depth == 0:
            for i in range(6):
                p1 = verts[i]
                p2 = verts[(i + 1) % 6]
                commands.append(("line", (*p1, *p2), 0))
            return

        cx = sum(v[0] for v in verts) / 6
        cy = sum(v[1] for v in verts) / 6

        # Create 6 smaller hexagons at each vertex
        for i in range(6):
            v = verts[i]
            new_cx = (cx + v[0]) / 2
            new_cy = (cy + v[1]) / 2
            new_r = math.hypot(v[0] - cx, v[1] - cy) / 3

            new_verts = []
            base_angle = math.atan2(v[1] - cy, v[0] - cx)
            for j in range(6):
                angle = base_angle + j * math.pi / 3
                new_verts.append((
                    new_cx + new_r * math.cos(angle),
                    new_cy + new_r * math.sin(angle),
                ))
            self._subdivide_hex(commands, new_verts, depth - 1)
