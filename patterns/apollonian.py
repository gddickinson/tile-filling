"""Apollonian gasket - recursive tangent circle packing."""

import math
from typing import Dict, List, Tuple
from patterns.base import BasePattern, DrawCommand


class ApollonianPattern(BasePattern):
    """Apollonian gasket - fractal circle packing where every gap is filled
    with a tangent circle, creating infinitely nested circular patterns."""

    name = "Apollonian Gasket"
    description = "Recursive tangent circle packing fractal"

    @staticmethod
    def get_params() -> List[Dict]:
        return [
            {"name": "depth", "label": "Recursion Depth", "type": "int", "min": 1, "max": 8, "default": 5},
            {"name": "min_radius", "label": "Min Radius (px)", "type": "float", "min": 0.5, "max": 10.0, "default": 2.0},
            {"name": "initial", "label": "Initial (0=Classic,1=Three,2=Four)", "type": "int", "min": 0, "max": 2, "default": 0},
            {"name": "arc_segments", "label": "Circle Smoothness", "type": "int", "min": 16, "max": 64, "default": 36},
        ]

    def generate(self, width: float, height: float, params: Dict, margin: float = 40) -> List[DrawCommand]:
        depth = params.get("depth", 5)
        min_r = params.get("min_radius", 2.0)
        initial = params.get("initial", 0)
        segments = params.get("arc_segments", 36)

        commands = []
        cx, cy = width / 2, height / 2
        size = min(width, height) / 2 - margin

        if initial == 0:
            circles = self._classic_seed(cx, cy, size)
        elif initial == 1:
            circles = self._three_seed(cx, cy, size)
        else:
            circles = self._four_seed(cx, cy, size)

        # Draw initial circles
        for x, y, r in circles:
            self._draw_circle(commands, x, y, abs(r), segments, 0)

        # Recursively fill gaps
        self._fill_gasket(commands, circles, depth, min_r, segments)

        return commands

    def _classic_seed(self, cx, cy, R):
        """Classic Apollonian: one big circle containing two medium circles."""
        r = R / 2
        return [
            (cx, cy, -R),  # Outer circle (negative curvature = containing)
            (cx - r, cy, r),
            (cx + r, cy, r),
            (cx, cy - r * 0.73, R - r),  # Computed tangent circle
        ]

    def _three_seed(self, cx, cy, R):
        """Three equal circles in a big circle."""
        r = R / (1 + 2 / math.sqrt(3))
        offset = R - r
        circles = [(cx, cy, -R)]
        for i in range(3):
            angle = i * 2 * math.pi / 3 - math.pi / 2
            circles.append((cx + offset * math.cos(angle), cy + offset * math.sin(angle), r))
        return circles

    def _four_seed(self, cx, cy, R):
        """Four circles: one big outer, three inner arranged in a triangle."""
        r = R * 0.4
        circles = [(cx, cy, -R)]
        for i in range(3):
            angle = i * 2 * math.pi / 3 - math.pi / 2
            d = R - r
            circles.append((cx + d * 0.6 * math.cos(angle), cy + d * 0.6 * math.sin(angle), r))
        return circles

    def _fill_gasket(self, commands, circles, max_depth, min_r, segments):
        """Recursively find and fill gaps with tangent circles."""
        n = len(circles)
        if n < 3:
            return

        queue = []
        # Generate all triples from initial circles
        for i in range(n):
            for j in range(i + 1, n):
                for k in range(j + 1, n):
                    queue.append((circles[i], circles[j], circles[k], 0))

        seen = set()
        all_circles = list(circles)

        while queue:
            c1, c2, c3, depth_level = queue.pop(0)

            if depth_level >= max_depth:
                continue

            # Find the circle tangent to all three using Descartes' theorem
            new_circles = self._descartes(c1, c2, c3)

            for nc in new_circles:
                ncx, ncy, nr = nc
                if abs(nr) < min_r:
                    continue

                # Check for duplicates
                key = (round(ncx, 1), round(ncy, 1), round(abs(nr), 1))
                if key in seen:
                    continue
                seen.add(key)

                # Check it doesn't overlap existing circles too badly
                valid = True
                for ec in all_circles:
                    d = math.hypot(ncx - ec[0], ncy - ec[1])
                    expected = abs(nr) + abs(ec[2]) if nr * ec[2] > 0 else abs(abs(nr) - abs(ec[2]))
                    if abs(nr) > 1 and d < abs(nr) * 0.3:
                        valid = False
                        break

                if not valid:
                    continue

                color_idx = min(3, depth_level + 1)
                self._draw_circle(commands, ncx, ncy, abs(nr), segments, color_idx)
                all_circles.append(nc)

                # Queue new triples
                queue.append((c1, c2, nc, depth_level + 1))
                queue.append((c1, c3, nc, depth_level + 1))
                queue.append((c2, c3, nc, depth_level + 1))

    def _descartes(self, c1, c2, c3):
        """Use Descartes' Circle Theorem to find tangent circles."""
        x1, y1, r1 = c1
        x2, y2, r2 = c2
        x3, y3, r3 = c3

        # Curvatures (1/r, negative for containing circle)
        k1 = 1.0 / r1 if r1 != 0 else 0
        k2 = 1.0 / r2 if r2 != 0 else 0
        k3 = 1.0 / r3 if r3 != 0 else 0

        # Descartes' theorem: k4 = k1 + k2 + k3 ± 2*sqrt(k1*k2 + k2*k3 + k3*k1)
        discriminant = k1 * k2 + k2 * k3 + k3 * k1
        if discriminant < 0:
            return []

        sqrt_disc = math.sqrt(discriminant)
        results = []

        for sign in [1, -1]:
            k4 = k1 + k2 + k3 + sign * 2 * sqrt_disc
            if abs(k4) < 1e-10:
                continue

            r4 = 1.0 / k4

            # Complex Descartes for position
            # z4 = (z1*k1 + z2*k2 + z3*k3 ± 2*sqrt(z1*z2*k1*k2 + z2*z3*k2*k3 + z1*z3*k1*k3)) / k4
            zk1 = complex(x1 * k1, y1 * k1)
            zk2 = complex(x2 * k2, y2 * k2)
            zk3 = complex(x3 * k3, y3 * k3)

            sum_zk = zk1 + zk2 + zk3

            # Product terms under sqrt
            prod = (complex(x1, y1) * complex(x2, y2) * k1 * k2 +
                    complex(x2, y2) * complex(x3, y3) * k2 * k3 +
                    complex(x1, y1) * complex(x3, y3) * k1 * k3)

            try:
                sqrt_prod = prod ** 0.5
            except (ValueError, ZeroDivisionError):
                continue

            for pos_sign in [1, -1]:
                z4 = (sum_zk + pos_sign * 2 * sqrt_prod) / k4
                x4 = z4.real
                y4 = z4.imag

                if abs(r4) > 0.1:
                    results.append((x4, y4, r4))

        return results

    def _draw_circle(self, commands, cx, cy, r, segments, color_idx):
        """Draw a circle as line segments."""
        if r < 0.5:
            return
        for i in range(segments):
            a1 = 2 * math.pi * i / segments
            a2 = 2 * math.pi * (i + 1) / segments
            x1 = cx + r * math.cos(a1)
            y1 = cy + r * math.sin(a1)
            x2 = cx + r * math.cos(a2)
            y2 = cy + r * math.sin(a2)
            commands.append(("line", (x1, y1, x2, y2), color_idx))
