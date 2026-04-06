"""Moiré interference patterns from overlapping geometric structures."""

import math
from typing import Dict, List
from patterns.base import BasePattern, DrawCommand


class MoirePattern(BasePattern):
    """Moiré patterns - visual interference from overlapping periodic structures."""

    name = "Moiré"
    description = "Interference patterns from overlapping grids, circles, or radial lines"

    @staticmethod
    def get_params() -> List[Dict]:
        return [
            {"name": "style", "label": "Style (0=Lines,1=Circles,2=Radial)", "type": "int", "min": 0, "max": 2, "default": 1},
            {"name": "count", "label": "Line/Circle Count", "type": "int", "min": 10, "max": 150, "default": 60},
            {"name": "angle_offset", "label": "Angle Offset (deg)", "type": "float", "min": 0.5, "max": 30.0, "default": 5.0},
            {"name": "center_offset", "label": "Center Offset", "type": "float", "min": 0.0, "max": 0.3, "default": 0.1},
            {"name": "layers", "label": "Number of Layers", "type": "int", "min": 2, "max": 5, "default": 2},
        ]

    def generate(self, width: float, height: float, params: Dict, margin: float = 40) -> List[DrawCommand]:
        style = params.get("style", 1)
        count = params.get("count", 60)
        angle_off = params.get("angle_offset", 5.0)
        center_off = params.get("center_offset", 0.1)
        layers = params.get("layers", 2)

        commands = []
        cx, cy = width / 2, height / 2
        size = min(width, height) / 2 - margin

        for layer in range(layers):
            offset_angle = math.radians(angle_off * layer)
            dx = size * center_off * math.cos(layer * math.pi / layers)
            dy = size * center_off * math.sin(layer * math.pi / layers)
            lcx, lcy = cx + dx, cy + dy
            color_idx = layer

            if style == 0:
                self._draw_lines(commands, lcx, lcy, size, count, offset_angle, color_idx, width, height, margin)
            elif style == 1:
                self._draw_circles(commands, lcx, lcy, size, count, color_idx)
            else:
                self._draw_radial(commands, lcx, lcy, size, count, offset_angle, color_idx)

        return commands

    def _draw_lines(self, commands, cx, cy, size, count, rotation, color_idx, w, h, margin):
        """Draw a set of parallel lines at a given rotation."""
        spacing = size * 2 / count
        cos_r = math.cos(rotation)
        sin_r = math.sin(rotation)

        for i in range(count + 1):
            offset = -size + i * spacing
            # Line perpendicular to rotation direction
            px = cx + offset * cos_r
            py = cy + offset * sin_r
            # Extend line in perpendicular direction
            dx = -sin_r * size * 1.5
            dy = cos_r * size * 1.5

            x1 = max(margin, min(w - margin, px - dx))
            y1 = max(margin, min(h - margin, py - dy))
            x2 = max(margin, min(w - margin, px + dx))
            y2 = max(margin, min(h - margin, py + dy))
            commands.append(("line", (x1, y1, x2, y2), color_idx))

    def _draw_circles(self, commands, cx, cy, size, count, color_idx):
        """Draw concentric circles."""
        spacing = size / count
        segments = 60

        for i in range(1, count + 1):
            r = i * spacing
            for j in range(segments):
                a1 = 2 * math.pi * j / segments
                a2 = 2 * math.pi * (j + 1) / segments
                x1 = cx + r * math.cos(a1)
                y1 = cy + r * math.sin(a1)
                x2 = cx + r * math.cos(a2)
                y2 = cy + r * math.sin(a2)
                commands.append(("line", (x1, y1, x2, y2), color_idx))

    def _draw_radial(self, commands, cx, cy, size, count, rotation, color_idx):
        """Draw radial lines from center."""
        for i in range(count):
            angle = rotation + 2 * math.pi * i / count
            x2 = cx + size * math.cos(angle)
            y2 = cy + size * math.sin(angle)
            commands.append(("line", (cx, cy, x2, y2), color_idx))
