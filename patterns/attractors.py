"""Strange attractor patterns - chaotic systems producing beautiful trajectories."""

import math
from typing import Dict, List
from patterns.base import BasePattern, DrawCommand


class AttractorPattern(BasePattern):
    """Strange attractors - chaotic dynamical systems that create intricate trajectory art."""

    name = "Strange Attractors"
    description = "Clifford, De Jong, and Lorenz chaotic attractor trajectories"

    @staticmethod
    def get_params() -> List[Dict]:
        return [
            {"name": "attractor", "label": "Type (0=Clifford,1=DeJong,2=Lorenz)", "type": "int", "min": 0, "max": 2, "default": 0},
            {"name": "a", "label": "Parameter a", "type": "float", "min": -3.0, "max": 3.0, "default": -1.4},
            {"name": "b", "label": "Parameter b", "type": "float", "min": -3.0, "max": 3.0, "default": 1.6},
            {"name": "c", "label": "Parameter c", "type": "float", "min": -3.0, "max": 3.0, "default": 1.0},
            {"name": "d", "label": "Parameter d", "type": "float", "min": -3.0, "max": 3.0, "default": 0.7},
            {"name": "iterations", "label": "Iterations (k)", "type": "int", "min": 5, "max": 200, "default": 80},
            {"name": "skip_lines", "label": "Line Skip", "type": "int", "min": 1, "max": 20, "default": 1},
        ]

    def generate(self, width: float, height: float, params: Dict, margin: float = 40) -> List[DrawCommand]:
        atype = params.get("attractor", 0)
        a = params.get("a", -1.4)
        b = params.get("b", 1.6)
        c = params.get("c", 1.0)
        d = params.get("d", 0.7)
        iters = params.get("iterations", 80) * 1000
        skip = params.get("skip_lines", 1)

        if atype == 0:
            points = self._clifford(a, b, c, d, iters)
        elif atype == 1:
            points = self._dejong(a, b, c, d, iters)
        else:
            points = self._lorenz(iters)

        return self._scale_and_draw(points, width, height, margin, skip)

    def _clifford(self, a, b, c, d, n):
        """Clifford attractor: x' = sin(a*y) + c*cos(a*x), y' = sin(b*x) + d*cos(b*y)"""
        x, y = 0.1, 0.1
        points = []
        for _ in range(n):
            nx = math.sin(a * y) + c * math.cos(a * x)
            ny = math.sin(b * x) + d * math.cos(b * y)
            x, y = nx, ny
            points.append((x, y))
        return points

    def _dejong(self, a, b, c, d, n):
        """De Jong attractor: x' = sin(a*y) - cos(b*x), y' = sin(c*x) - cos(d*y)"""
        x, y = 0.1, 0.1
        points = []
        for _ in range(n):
            nx = math.sin(a * y) - math.cos(b * x)
            ny = math.sin(c * x) - math.cos(d * y)
            x, y = nx, ny
            points.append((x, y))
        return points

    def _lorenz(self, n):
        """Lorenz attractor projected to 2D (x-z plane)."""
        sigma, rho, beta = 10.0, 28.0, 8.0 / 3.0
        x, y, z = 0.1, 0.0, 0.0
        dt = 0.002
        points = []
        for _ in range(n):
            dx = sigma * (y - x)
            dy = x * (rho - z) - y
            dz = x * y - beta * z
            x += dx * dt
            y += dy * dt
            z += dz * dt
            points.append((x, z))  # Project to x-z plane
        return points

    def _scale_and_draw(self, points, width, height, margin, skip):
        """Scale attractor points to canvas."""
        if len(points) < 2:
            return []

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        range_x = max_x - min_x or 1
        range_y = max_y - min_y or 1

        w = width - 2 * margin
        h = height - 2 * margin
        scale = min(w / range_x, h / range_y)
        ox = margin + (w - range_x * scale) / 2
        oy = margin + (h - range_y * scale) / 2

        commands = []
        total = len(points)
        for i in range(0, total - skip, skip):
            p1 = points[i]
            p2 = points[i + skip]
            x1 = ox + (p1[0] - min_x) * scale
            y1 = oy + (p1[1] - min_y) * scale
            x2 = ox + (p2[0] - min_x) * scale
            y2 = oy + (p2[1] - min_y) * scale
            color_idx = (i * 4) // total
            commands.append(("line", (x1, y1, x2, y2), color_idx))

        return commands
