"""Phyllotaxis spiral patterns - Fibonacci/golden angle arrangements."""

import math
from typing import Dict, List
from patterns.base import BasePattern, DrawCommand

GOLDEN_ANGLE = math.pi * (3 - math.sqrt(5))  # ~137.5 degrees


class PhyllotaxisPattern(BasePattern):
    """Phyllotaxis - sunflower seed arrangements using the golden angle.

    Points are placed at increasing radii with golden angle rotation,
    connected with various styles to create spiraling patterns.
    """

    name = "Phyllotaxis"
    description = "Fibonacci sunflower spiral arrangements with various connection styles"

    @staticmethod
    def get_params() -> List[Dict]:
        return [
            {"name": "points", "label": "Number of Points", "type": "int", "min": 50, "max": 2000, "default": 500},
            {"name": "style", "label": "Style (0=Dots,1=Spokes,2=Spiral,3=Voronoi)", "type": "int", "min": 0, "max": 3, "default": 2},
            {"name": "angle_mult", "label": "Angle Multiplier", "type": "float", "min": 0.9, "max": 1.1, "default": 1.0},
            {"name": "scale_power", "label": "Radius Power", "type": "float", "min": 0.3, "max": 0.8, "default": 0.5},
            {"name": "dot_size", "label": "Dot/Line Size", "type": "float", "min": 0.5, "max": 8.0, "default": 3.0},
        ]

    def generate(self, width: float, height: float, params: Dict, margin: float = 40) -> List[DrawCommand]:
        n = params.get("points", 500)
        style = params.get("style", 2)
        angle_mult = params.get("angle_mult", 1.0)
        scale_pow = params.get("scale_power", 0.5)
        dot_size = params.get("dot_size", 3.0)

        commands = []
        cx, cy = width / 2, height / 2
        max_r = min(width, height) / 2 - margin

        # Generate phyllotaxis points
        pts = []
        for i in range(n):
            angle = i * GOLDEN_ANGLE * angle_mult
            r = max_r * (i / n) ** scale_pow
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            pts.append((x, y))

        if style == 0:
            # Dots with size based on index
            for i, (x, y) in enumerate(pts):
                r = dot_size * (0.3 + 0.7 * i / n)
                color_idx = (i * 4) // n
                commands.append(("circle", (x, y, r), color_idx))

        elif style == 1:
            # Spokes from center
            for i, (x, y) in enumerate(pts):
                color_idx = (i * 4) // n
                commands.append(("line", (cx, cy, x, y), color_idx))

        elif style == 2:
            # Connect consecutive points (spiral)
            for i in range(len(pts) - 1):
                color_idx = (i * 3) // n
                commands.append(("line", (*pts[i], *pts[i + 1]), color_idx))

            # Also connect every Fibonacci-th point for secondary spirals
            for fib in [8, 13, 21]:
                for i in range(len(pts) - fib):
                    color_idx = ((i * 3) // n + 1) % 4
                    commands.append(("line", (*pts[i], *pts[i + fib]), color_idx))

        elif style == 3:
            # Connect nearest neighbors (approximate Voronoi dual)
            for i in range(len(pts)):
                # Find 3 nearest neighbors
                dists = []
                for j in range(len(pts)):
                    if i == j:
                        continue
                    d = (pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2
                    dists.append((d, j))
                dists.sort()

                for d, j in dists[:3]:
                    if j > i:  # Draw each edge only once
                        color_idx = (i * 3) // n
                        commands.append(("line", (*pts[i], *pts[j]), color_idx))

        return commands
