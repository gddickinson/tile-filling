"""Spirograph patterns - hypotrochoid and epitrochoid parametric curves."""

import math
from typing import Dict, List
from patterns.base import BasePattern, DrawCommand


class SpirographPattern(BasePattern):
    """Spirograph art - gear-based parametric curves with rich harmonic structure."""

    name = "Spirograph"
    description = "Hypotrochoid and epitrochoid curves from rolling circle geometry"

    @staticmethod
    def get_params() -> List[Dict]:
        return [
            {"name": "R", "label": "Outer Radius (R)", "type": "int", "min": 10, "max": 100, "default": 60},
            {"name": "r", "label": "Inner Radius (r)", "type": "int", "min": 3, "max": 80, "default": 37},
            {"name": "d", "label": "Pen Distance (d)", "type": "float", "min": 5.0, "max": 100.0, "default": 45.0},
            {"name": "mode", "label": "Mode (0=Hypo,1=Epi,2=Both)", "type": "int", "min": 0, "max": 2, "default": 0},
            {"name": "multi", "label": "Overlaid Curves", "type": "int", "min": 1, "max": 8, "default": 1},
            {"name": "resolution", "label": "Resolution", "type": "int", "min": 500, "max": 10000, "default": 5000},
        ]

    def generate(self, width: float, height: float, params: Dict, margin: float = 40) -> List[DrawCommand]:
        R = params.get("R", 60)
        r = params.get("r", 37)
        d = params.get("d", 45.0)
        mode = params.get("mode", 0)
        multi = params.get("multi", 1)
        resolution = params.get("resolution", 5000)

        commands = []
        cx, cy = width / 2, height / 2
        size = min(width, height) / 2 - margin

        for layer in range(multi):
            # Vary parameters slightly for each overlaid curve
            lr = r + layer * 2
            ld = d + layer * 3

            if mode == 0 or mode == 2:
                pts = self._hypotrochoid(R, lr, ld, resolution)
                self._add_curve(commands, pts, cx, cy, size, layer * 2)

            if mode == 1 or mode == 2:
                pts = self._epitrochoid(R, lr, ld, resolution)
                self._add_curve(commands, pts, cx, cy, size, layer * 2 + 1)

        return commands

    def _hypotrochoid(self, R, r, d, n):
        """x = (R-r)cos(t) + d*cos((R-r)t/r), y = (R-r)sin(t) - d*sin((R-r)t/r)"""
        if r == 0:
            return []

        # Number of full rotations needed to close the curve
        g = math.gcd(R, r)
        rotations = r // g
        t_max = 2 * math.pi * rotations

        points = []
        for i in range(n + 1):
            t = t_max * i / n
            x = (R - r) * math.cos(t) + d * math.cos((R - r) * t / r)
            y = (R - r) * math.sin(t) - d * math.sin((R - r) * t / r)
            points.append((x, y))
        return points

    def _epitrochoid(self, R, r, d, n):
        """x = (R+r)cos(t) - d*cos((R+r)t/r), y = (R+r)sin(t) - d*sin((R+r)t/r)"""
        if r == 0:
            return []

        g = math.gcd(R, r)
        rotations = r // g
        t_max = 2 * math.pi * rotations

        points = []
        for i in range(n + 1):
            t = t_max * i / n
            x = (R + r) * math.cos(t) - d * math.cos((R + r) * t / r)
            y = (R + r) * math.sin(t) - d * math.sin((R + r) * t / r)
            points.append((x, y))
        return points

    def _add_curve(self, commands, points, cx, cy, size, color_idx):
        """Scale and add curve to commands."""
        if len(points) < 2:
            return

        # Find bounds for scaling
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        max_extent = max(max(abs(x) for x in xs), max(abs(y) for y in ys)) or 1
        scale = size / max_extent

        total = len(points)
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            x1 = cx + p1[0] * scale
            y1 = cy + p1[1] * scale
            x2 = cx + p2[0] * scale
            y2 = cy + p2[1] * scale
            commands.append(("line", (x1, y1, x2, y2), color_idx))
