"""Hexagonal tiling patterns."""

import math
from typing import Dict, List
from patterns.base import BasePattern, DrawCommand
from utils.geometry import polygon_vertices, rotate_point


class HexagonalPattern(BasePattern):
    """Hexagonal (honeycomb) tiling with optional internal decorations."""

    name = "Hexagonal"
    description = "Honeycomb tiling with optional star and floral decorations"

    @staticmethod
    def get_params() -> List[Dict]:
        return [
            {"name": "size", "label": "Hex Size", "type": "int", "min": 10, "max": 80, "default": 35},
            {"name": "decoration", "label": "Decoration (0-4)", "type": "int", "min": 0, "max": 4, "default": 1},
            {"name": "inner_hex", "label": "Inner Hex Scale", "type": "float", "min": 0.1, "max": 0.9, "default": 0.5},
            {"name": "pointy_top", "label": "Pointy Top", "type": "bool", "min": 0, "max": 1, "default": True},
        ]

    def generate(self, width: float, height: float, params: Dict, margin: float = 40) -> List[DrawCommand]:
        size = params.get("size", 35)
        decoration = params.get("decoration", 1)
        inner_scale = params.get("inner_hex", 0.5)
        pointy = params.get("pointy_top", True)

        commands = []
        start_angle = -math.pi / 6 if pointy else 0

        if pointy:
            col_spacing = size * math.sqrt(3)
            row_spacing = size * 1.5
        else:
            col_spacing = size * 1.5
            row_spacing = size * math.sqrt(3)

        x0 = margin + size
        y0 = margin + size

        cols = int((width - 2 * margin) / col_spacing) + 1
        rows = int((height - 2 * margin) / row_spacing) + 1

        for row in range(rows):
            for col in range(cols):
                if pointy:
                    cx = x0 + col * col_spacing + (row % 2) * col_spacing / 2
                    cy = y0 + row * row_spacing
                else:
                    cx = x0 + col * col_spacing
                    cy = y0 + row * row_spacing + (col % 2) * row_spacing / 2

                if cx > width - margin or cy > height - margin:
                    continue

                verts = polygon_vertices((cx, cy), size, 6, start_angle)

                # Draw hex outline
                for i in range(6):
                    p1 = verts[i]
                    p2 = verts[(i + 1) % 6]
                    commands.append(("line", (*p1, *p2), 0))

                # Decorations
                if decoration >= 1:
                    # Inner hex
                    inner_verts = polygon_vertices((cx, cy), size * inner_scale, 6, start_angle)
                    for i in range(6):
                        p1 = inner_verts[i]
                        p2 = inner_verts[(i + 1) % 6]
                        commands.append(("line", (*p1, *p2), 1))

                if decoration >= 2:
                    # Connect inner to outer vertices
                    for i in range(6):
                        commands.append(("line", (*verts[i], *inner_verts[i]), 1))

                if decoration >= 3:
                    # Star pattern - connect alternate vertices
                    for i in range(6):
                        commands.append(("line", (*verts[i], *verts[(i + 2) % 6]), 2))

                if decoration >= 4:
                    # Radial lines from center
                    for i in range(12):
                        angle = start_angle + i * math.pi / 6
                        ex = cx + size * 0.9 * math.cos(angle)
                        ey = cy + size * 0.9 * math.sin(angle)
                        commands.append(("line", (cx, cy, ex, ey), 2))
                    commands.append(("circle", (cx, cy, size * 0.06), 2))

        return commands
