"""Islamic geometric star patterns."""

import math
from typing import Dict, List
from patterns.base import BasePattern, DrawCommand
from utils.geometry import polygon_vertices, rotate_point, midpoint


class IslamicStarPattern(BasePattern):
    """Islamic-style geometric patterns with interlocking stars."""

    name = "Islamic Star"
    description = "Traditional Islamic geometric star and rosette patterns"

    @staticmethod
    def get_params() -> List[Dict]:
        return [
            {"name": "grid_size", "label": "Grid Size", "type": "int", "min": 2, "max": 15, "default": 5},
            {"name": "points", "label": "Star Points", "type": "int", "min": 5, "max": 12, "default": 8},
            {"name": "inner_ratio", "label": "Inner Ratio", "type": "float", "min": 0.15, "max": 0.85, "default": 0.4},
            {"name": "interlace", "label": "Interlace Depth", "type": "float", "min": 0.0, "max": 1.0, "default": 0.5},
            {"name": "rosette", "label": "Rosette Mode", "type": "bool", "min": 0, "max": 1, "default": False},
        ]

    def generate(self, width: float, height: float, params: Dict, margin: float = 40) -> List[DrawCommand]:
        grid_size = params.get("grid_size", 5)
        n_points = params.get("points", 8)
        inner_ratio = params.get("inner_ratio", 0.4)
        interlace = params.get("interlace", 0.5)
        rosette = params.get("rosette", False)

        commands = []
        w = width - 2 * margin
        h = height - 2 * margin
        cell = min(w, h) / grid_size
        radius = cell * 0.45

        ox = margin + (w - cell * grid_size) / 2
        oy = margin + (h - cell * grid_size) / 2

        for i in range(grid_size):
            for j in range(grid_size):
                cx = ox + (i + 0.5) * cell
                cy = oy + (j + 0.5) * cell

                if rosette:
                    self._draw_rosette(commands, cx, cy, radius, n_points, inner_ratio)
                else:
                    self._draw_star(commands, cx, cy, radius, n_points, inner_ratio, interlace)

        # Draw connecting lines between adjacent stars
        self._draw_connections(commands, ox, oy, cell, grid_size, radius, n_points, inner_ratio)

        return commands

    def _draw_star(self, commands, cx, cy, radius, n, inner_ratio, interlace):
        """Draw an n-pointed star."""
        outer = polygon_vertices((cx, cy), radius, n, -math.pi / 2)
        inner = polygon_vertices((cx, cy), radius * inner_ratio, n, -math.pi / 2 + math.pi / n)

        # Star outline - connect outer to inner points alternately
        all_points = []
        for i in range(n):
            all_points.append(outer[i])
            all_points.append(inner[i])

        for i in range(len(all_points)):
            p1 = all_points[i]
            p2 = all_points[(i + 1) % len(all_points)]
            commands.append(("line", (*p1, *p2), 0))

        # Interlace lines - connect every other outer point
        if interlace > 0:
            skip = max(2, n // 3)
            for i in range(n):
                p1 = outer[i]
                p2 = outer[(i + skip) % n]
                commands.append(("line", (*p1, *p2), 1))

        # Center dot
        commands.append(("circle", (cx, cy, radius * 0.04), 2))

    def _draw_rosette(self, commands, cx, cy, radius, n, inner_ratio):
        """Draw a rosette pattern with overlapping circles concept."""
        outer = polygon_vertices((cx, cy), radius, n, -math.pi / 2)
        inner = polygon_vertices((cx, cy), radius * inner_ratio, n, -math.pi / 2 + math.pi / n)

        # Outer polygon
        for i in range(n):
            p1 = outer[i]
            p2 = outer[(i + 1) % n]
            commands.append(("line", (*p1, *p2), 0))

        # Inner polygon
        for i in range(n):
            p1 = inner[i]
            p2 = inner[(i + 1) % n]
            commands.append(("line", (*p1, *p2), 1))

        # Petal lines: each outer vertex connects to two inner vertices
        for i in range(n):
            commands.append(("line", (*outer[i], *inner[i]), 2))
            commands.append(("line", (*outer[i], *inner[(i - 1) % n]), 2))

        # Radial lines from center
        for i in range(n):
            commands.append(("line", (cx, cy, *outer[i]), 2))

        commands.append(("circle", (cx, cy, radius * 0.06), 2))

    def _draw_connections(self, commands, ox, oy, cell, grid_size, radius, n, inner_ratio):
        """Draw geometric connections between adjacent stars."""
        outer_points_cache = {}

        for i in range(grid_size):
            for j in range(grid_size):
                cx = ox + (i + 0.5) * cell
                cy = oy + (j + 0.5) * cell
                outer_points_cache[(i, j)] = polygon_vertices(
                    (cx, cy), radius, n, -math.pi / 2
                )

        for i in range(grid_size):
            for j in range(grid_size):
                pts = outer_points_cache[(i, j)]
                # Connect to right neighbor
                if i + 1 < grid_size:
                    rpts = outer_points_cache[(i + 1, j)]
                    # Find closest pair of points
                    best = None
                    best_d = float("inf")
                    for pi, p in enumerate(pts):
                        for qi, q in enumerate(rpts):
                            d = (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2
                            if d < best_d:
                                best_d = d
                                best = (p, q)
                    if best:
                        commands.append(("line", (*best[0], *best[1]), 0))

                # Connect to bottom neighbor
                if j + 1 < grid_size:
                    bpts = outer_points_cache[(i, j + 1)]
                    best = None
                    best_d = float("inf")
                    for pi, p in enumerate(pts):
                        for qi, q in enumerate(bpts):
                            d = (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2
                            if d < best_d:
                                best_d = d
                                best = (p, q)
                    if best:
                        commands.append(("line", (*best[0], *best[1]), 0))
