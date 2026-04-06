"""Lissajous and harmonograph patterns - damped parametric pendulum curves."""

import math
from typing import Dict, List
from patterns.base import BasePattern, DrawCommand


class LissajousPattern(BasePattern):
    """Lissajous curves and harmonograph simulations.

    Lissajous: x = A*sin(a*t + d), y = B*sin(b*t)
    Harmonograph: damped Lissajous with decay, producing spiral-in patterns.
    """

    name = "Lissajous"
    description = "Parametric pendulum curves and harmonograph simulations"

    @staticmethod
    def get_params() -> List[Dict]:
        return [
            {"name": "freq_x", "label": "Frequency X", "type": "int", "min": 1, "max": 12, "default": 3},
            {"name": "freq_y", "label": "Frequency Y", "type": "int", "min": 1, "max": 12, "default": 4},
            {"name": "phase", "label": "Phase (deg)", "type": "float", "min": 0.0, "max": 360.0, "default": 90.0},
            {"name": "damping", "label": "Damping", "type": "float", "min": 0.0, "max": 0.02, "default": 0.0},
            {"name": "layers", "label": "Overlaid Curves", "type": "int", "min": 1, "max": 6, "default": 1},
            {"name": "resolution", "label": "Resolution", "type": "int", "min": 500, "max": 10000, "default": 4000},
            {"name": "harmonograph", "label": "Harmonograph Mode", "type": "bool", "min": 0, "max": 1, "default": False},
        ]

    def generate(self, width: float, height: float, params: Dict, margin: float = 40) -> List[DrawCommand]:
        fx = params.get("freq_x", 3)
        fy = params.get("freq_y", 4)
        phase = math.radians(params.get("phase", 90.0))
        damping = params.get("damping", 0.0)
        layers = params.get("layers", 1)
        res = params.get("resolution", 4000)
        harmonograph = params.get("harmonograph", False)

        commands = []
        cx, cy = width / 2, height / 2
        size = min(width, height) / 2 - margin

        for layer in range(layers):
            lphase = phase + layer * math.pi / (layers * 2)
            lfx = fx + layer * 0.1
            lfy = fy + layer * 0.1

            if harmonograph:
                points = self._harmonograph(lfx, lfy, lphase, damping, res)
            else:
                points = self._lissajous(lfx, lfy, lphase, damping, res)

            self._add_curve(commands, points, cx, cy, size, layer)

        return commands

    def _lissajous(self, fx, fy, phase, damping, n):
        """Standard Lissajous: x=sin(fx*t+phase), y=sin(fy*t)."""
        points = []
        t_max = 2 * math.pi * max(10, int(fx * fy))

        for i in range(n + 1):
            t = t_max * i / n
            decay = math.exp(-damping * t)
            x = math.sin(fx * t + phase) * decay
            y = math.sin(fy * t) * decay
            points.append((x, y))

        return points

    def _harmonograph(self, fx, fy, phase, damping, n):
        """Harmonograph: two damped pendulums combined."""
        points = []
        t_max = 2 * math.pi * 40
        d1 = damping if damping > 0 else 0.003
        d2 = d1 * 1.1

        # Two pendulum pairs
        f1x, f1y = fx, fy
        f2x, f2y = fx + 0.01, fy + 0.01
        p1, p2 = phase, phase * 0.7

        for i in range(n + 1):
            t = t_max * i / n
            x = (math.sin(f1x * t + p1) * math.exp(-d1 * t) +
                 math.sin(f2x * t + p2) * math.exp(-d2 * t))
            y = (math.sin(f1y * t + p1 * 0.5) * math.exp(-d1 * t) +
                 math.sin(f2y * t + p2 * 0.3) * math.exp(-d2 * t))
            points.append((x, y))

        return points

    def _add_curve(self, commands, points, cx, cy, size, color_idx):
        """Scale and add curve to commands."""
        if len(points) < 2:
            return

        max_ext = max(max(abs(p[0]) for p in points), max(abs(p[1]) for p in points)) or 1
        scale = size / max_ext * 0.95

        total = len(points)
        for i in range(total - 1):
            p1 = points[i]
            p2 = points[i + 1]
            x1 = cx + p1[0] * scale
            y1 = cy + p1[1] * scale
            x2 = cx + p2[0] * scale
            y2 = cy + p2[1] * scale
            commands.append(("line", (x1, y1, x2, y2), color_idx))
