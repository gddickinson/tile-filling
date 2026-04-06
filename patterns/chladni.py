"""Chladni figure patterns - nodal lines from vibrating plate wave equations."""

import math
from typing import Dict, List
from patterns.base import BasePattern, DrawCommand


class ChladniPattern(BasePattern):
    """Chladni figures - elegant nodal line patterns from 2D wave equations.

    Based on Ernst Chladni's vibrating plate experiments. The patterns show
    where a vibrating surface remains still (nodal lines).
    """

    name = "Chladni Figures"
    description = "Nodal line patterns from vibrating plate wave equations"

    @staticmethod
    def get_params() -> List[Dict]:
        return [
            {"name": "m", "label": "Mode m", "type": "int", "min": 1, "max": 12, "default": 5},
            {"name": "n", "label": "Mode n", "type": "int", "min": 1, "max": 12, "default": 3},
            {"name": "resolution", "label": "Resolution", "type": "int", "min": 50, "max": 300, "default": 150},
            {"name": "threshold", "label": "Line Threshold", "type": "float", "min": 0.01, "max": 0.3, "default": 0.05},
            {"name": "mode", "label": "Mode (0=Square,1=Circular)", "type": "int", "min": 0, "max": 1, "default": 0},
        ]

    def generate(self, width: float, height: float, params: Dict, margin: float = 40) -> List[DrawCommand]:
        m = params.get("m", 5)
        n = params.get("n", 3)
        res = params.get("resolution", 150)
        threshold = params.get("threshold", 0.05)
        mode = params.get("mode", 0)

        commands = []
        w = width - 2 * margin
        h = height - 2 * margin
        size = min(w, h)
        ox = margin + (w - size) / 2
        oy = margin + (h - size) / 2

        # Compute the wave function on a grid
        grid = [[0.0] * (res + 1) for _ in range(res + 1)]

        for i in range(res + 1):
            for j in range(res + 1):
                x = i / res  # 0 to 1
                y = j / res  # 0 to 1

                if mode == 0:
                    # Square plate: cos(m*pi*x)*cos(n*pi*y) - cos(n*pi*x)*cos(m*pi*y)
                    grid[i][j] = (
                        math.cos(m * math.pi * x) * math.cos(n * math.pi * y) -
                        math.cos(n * math.pi * x) * math.cos(m * math.pi * y)
                    )
                else:
                    # Circular: use polar coordinates
                    px = 2 * x - 1  # -1 to 1
                    py = 2 * y - 1
                    r = math.sqrt(px * px + py * py)
                    if r > 1.0:
                        grid[i][j] = float('nan')
                        continue
                    theta = math.atan2(py, px)
                    # Bessel-like approximation using trig
                    grid[i][j] = math.cos(m * theta) * math.sin(n * math.pi * r)

        # Extract zero-contour lines using marching squares
        self._marching_squares(commands, grid, res, ox, oy, size, threshold)

        return commands

    def _marching_squares(self, commands, grid, res, ox, oy, size, threshold):
        """Extract contour lines at z≈0 using marching squares algorithm."""
        cell_w = size / res
        cell_h = size / res

        for i in range(res):
            for j in range(res):
                # Get corners of this cell
                v00 = grid[i][j]
                v10 = grid[i + 1][j]
                v01 = grid[i][j + 1]
                v11 = grid[i + 1][j + 1]

                # Skip NaN cells (circular mode outside disk)
                if any(math.isnan(v) for v in [v00, v10, v01, v11]):
                    continue

                # Classify corners as positive or negative
                case = 0
                if v00 > 0: case |= 1
                if v10 > 0: case |= 2
                if v01 > 0: case |= 4
                if v11 > 0: case |= 8

                if case == 0 or case == 15:
                    continue

                # Cell corner screen coordinates
                x0 = ox + i * cell_w
                y0 = oy + j * cell_h
                x1 = x0 + cell_w
                y1 = y0 + cell_h

                # Interpolated edge crossing points
                edges = self._get_edge_points(v00, v10, v01, v11, x0, y0, x1, y1)

                # Draw contour segments based on case
                segments = self._case_segments(case)
                color_idx = 0

                for seg in segments:
                    if seg[0] in edges and seg[1] in edges:
                        p1 = edges[seg[0]]
                        p2 = edges[seg[1]]
                        commands.append(("line", (*p1, *p2), color_idx))

    def _get_edge_points(self, v00, v10, v01, v11, x0, y0, x1, y1):
        """Calculate interpolated edge crossing points."""
        edges = {}

        # Top edge (between v00 and v10)
        if (v00 > 0) != (v10 > 0):
            t = abs(v00) / (abs(v00) + abs(v10)) if abs(v00) + abs(v10) > 0 else 0.5
            edges["top"] = (x0 + t * (x1 - x0), y0)

        # Bottom edge (between v01 and v11)
        if (v01 > 0) != (v11 > 0):
            t = abs(v01) / (abs(v01) + abs(v11)) if abs(v01) + abs(v11) > 0 else 0.5
            edges["bottom"] = (x0 + t * (x1 - x0), y1)

        # Left edge (between v00 and v01)
        if (v00 > 0) != (v01 > 0):
            t = abs(v00) / (abs(v00) + abs(v01)) if abs(v00) + abs(v01) > 0 else 0.5
            edges["left"] = (x0, y0 + t * (y1 - y0))

        # Right edge (between v10 and v11)
        if (v10 > 0) != (v11 > 0):
            t = abs(v10) / (abs(v10) + abs(v11)) if abs(v10) + abs(v11) > 0 else 0.5
            edges["right"] = (x1, y0 + t * (y1 - y0))

        return edges

    def _case_segments(self, case):
        """Return edge connections for each marching squares case."""
        SEGMENTS = {
            1: [("top", "left")],
            2: [("top", "right")],
            3: [("left", "right")],
            4: [("left", "bottom")],
            5: [("top", "bottom")],
            6: [("top", "left"), ("right", "bottom")],
            7: [("right", "bottom")],
            8: [("right", "bottom")],
            9: [("top", "right"), ("left", "bottom")],
            10: [("top", "bottom")],
            11: [("left", "bottom")],
            12: [("left", "right")],
            13: [("top", "right")],
            14: [("top", "left")],
        }
        return SEGMENTS.get(case, [])
