"""Reaction-Diffusion patterns - Gray-Scott model with contour line extraction."""

import math
from typing import Dict, List
from patterns.base import BasePattern, DrawCommand


class ReactionDiffusionPattern(BasePattern):
    """Gray-Scott reaction-diffusion - organic Turing patterns as contour lines.

    Simulates chemical reaction-diffusion on a grid, then extracts
    contour lines to produce organic, coral-like line art.
    """

    name = "Reaction-Diffusion"
    description = "Gray-Scott organic Turing patterns rendered as contour lines"

    @staticmethod
    def get_params() -> List[Dict]:
        return [
            {"name": "resolution", "label": "Resolution", "type": "int", "min": 40, "max": 150, "default": 80},
            {"name": "iterations", "label": "Iterations", "type": "int", "min": 500, "max": 10000, "default": 3000},
            {"name": "feed", "label": "Feed Rate (x1000)", "type": "int", "min": 10, "max": 80, "default": 55},
            {"name": "kill", "label": "Kill Rate (x1000)", "type": "int", "min": 40, "max": 75, "default": 62},
            {"name": "contours", "label": "Contour Levels", "type": "int", "min": 1, "max": 8, "default": 3},
            {"name": "seed_count", "label": "Seed Points", "type": "int", "min": 1, "max": 20, "default": 5},
        ]

    def generate(self, width: float, height: float, params: Dict, margin: float = 40) -> List[DrawCommand]:
        res = params.get("resolution", 80)
        iters = params.get("iterations", 3000)
        f = params.get("feed", 55) / 1000.0
        k = params.get("kill", 62) / 1000.0
        n_contours = params.get("contours", 3)
        seed_count = params.get("seed_count", 5)

        # Run Gray-Scott simulation
        v_grid = self._simulate(res, iters, f, k, seed_count)

        # Extract contour lines at multiple levels
        commands = []
        w = width - 2 * margin
        h = height - 2 * margin
        size = min(w, h)
        ox = margin + (w - size) / 2
        oy = margin + (h - size) / 2

        # Find value range
        flat = [v_grid[i][j] for i in range(res) for j in range(res)]
        vmin = min(flat)
        vmax = max(flat)

        if vmax - vmin < 1e-6:
            return commands

        for level in range(n_contours):
            t = (level + 1) / (n_contours + 1)
            threshold = vmin + t * (vmax - vmin)
            self._extract_contour(commands, v_grid, res, ox, oy, size, threshold, level)

        return commands

    def _simulate(self, res, iterations, f, k, seed_count):
        """Run Gray-Scott reaction-diffusion simulation."""
        Du, Dv = 0.16, 0.08
        dt = 1.0

        # Initialize u=1, v=0 everywhere
        u = [[1.0] * res for _ in range(res)]
        v = [[0.0] * res for _ in range(res)]

        # Seed initial perturbations
        import random
        random.seed(42)
        for _ in range(seed_count):
            cx = random.randint(res // 4, 3 * res // 4)
            cy = random.randint(res // 4, 3 * res // 4)
            r = max(2, res // 15)
            for i in range(max(0, cx - r), min(res, cx + r)):
                for j in range(max(0, cy - r), min(res, cy + r)):
                    if (i - cx) ** 2 + (j - cy) ** 2 < r * r:
                        u[i][j] = 0.5
                        v[i][j] = 0.25

        # Simulate
        for _ in range(iterations):
            nu = [[0.0] * res for _ in range(res)]
            nv = [[0.0] * res for _ in range(res)]

            for i in range(res):
                for j in range(res):
                    # Laplacian with periodic boundary
                    ip = (i + 1) % res
                    im = (i - 1) % res
                    jp = (j + 1) % res
                    jm = (j - 1) % res

                    lap_u = (u[ip][j] + u[im][j] + u[i][jp] + u[i][jm] - 4 * u[i][j])
                    lap_v = (v[ip][j] + v[im][j] + v[i][jp] + v[i][jm] - 4 * v[i][j])

                    uv2 = u[i][j] * v[i][j] * v[i][j]
                    nu[i][j] = u[i][j] + dt * (Du * lap_u - uv2 + f * (1 - u[i][j]))
                    nv[i][j] = v[i][j] + dt * (Dv * lap_v + uv2 - (f + k) * v[i][j])

            u, v = nu, nv

        return v

    def _extract_contour(self, commands, grid, res, ox, oy, size, threshold, color_idx):
        """Extract contour lines at a given threshold using marching squares."""
        cell = size / res

        for i in range(res - 1):
            for j in range(res - 1):
                v00 = grid[i][j] - threshold
                v10 = grid[i + 1][j] - threshold
                v01 = grid[i][j + 1] - threshold
                v11 = grid[i + 1][j + 1] - threshold

                case = 0
                if v00 > 0: case |= 1
                if v10 > 0: case |= 2
                if v01 > 0: case |= 4
                if v11 > 0: case |= 8

                if case == 0 or case == 15:
                    continue

                x0 = ox + i * cell
                y0 = oy + j * cell
                x1 = x0 + cell
                y1 = y0 + cell

                # Edge interpolation
                pts = {}
                if (v00 > 0) != (v10 > 0):
                    t = abs(v00) / (abs(v00) + abs(v10) + 1e-10)
                    pts["T"] = (x0 + t * (x1 - x0), y0)
                if (v01 > 0) != (v11 > 0):
                    t = abs(v01) / (abs(v01) + abs(v11) + 1e-10)
                    pts["B"] = (x0 + t * (x1 - x0), y1)
                if (v00 > 0) != (v01 > 0):
                    t = abs(v00) / (abs(v00) + abs(v01) + 1e-10)
                    pts["L"] = (x0, y0 + t * (y1 - y0))
                if (v10 > 0) != (v11 > 0):
                    t = abs(v10) / (abs(v10) + abs(v11) + 1e-10)
                    pts["R"] = (x1, y0 + t * (y1 - y0))

                segs = {
                    1: [("T", "L")], 2: [("T", "R")], 3: [("L", "R")],
                    4: [("L", "B")], 5: [("T", "B")],
                    6: [("T", "L"), ("R", "B")], 7: [("R", "B")],
                    8: [("R", "B")], 9: [("T", "R"), ("L", "B")],
                    10: [("T", "B")], 11: [("L", "B")],
                    12: [("L", "R")], 13: [("T", "R")], 14: [("T", "L")],
                }.get(case, [])

                for s in segs:
                    if s[0] in pts and s[1] in pts:
                        p1, p2 = pts[s[0]], pts[s[1]]
                        commands.append(("line", (*p1, *p2), color_idx))
