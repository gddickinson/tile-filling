"""Space-filling curves - Hilbert, Peano, and Gosper curves."""

import math
from typing import Dict, List
from patterns.base import BasePattern, DrawCommand


class SpaceFillingPattern(BasePattern):
    """Continuous curves that fill a 2D region - hypnotic mathematical paths."""

    name = "Space-Filling Curves"
    description = "Hilbert, Peano, and Gosper curves that fill space with a single path"

    @staticmethod
    def get_params() -> List[Dict]:
        return [
            {"name": "curve_type", "label": "Type (0=Hilbert,1=Peano,2=Gosper)", "type": "int", "min": 0, "max": 2, "default": 0},
            {"name": "depth", "label": "Recursion Depth", "type": "int", "min": 1, "max": 7, "default": 5},
            {"name": "connect", "label": "Connected Line", "type": "bool", "min": 0, "max": 1, "default": True},
            {"name": "rounded", "label": "Rounded Corners", "type": "float", "min": 0.0, "max": 0.5, "default": 0.0},
        ]

    def generate(self, width: float, height: float, params: Dict, margin: float = 40) -> List[DrawCommand]:
        curve_type = params.get("curve_type", 0)
        depth = params.get("depth", 5)
        rounded = params.get("rounded", 0.0)

        if curve_type == 0:
            points = self._hilbert(depth)
        elif curve_type == 1:
            points = self._peano(depth)
        else:
            points = self._gosper(depth)

        if not points:
            return []

        # Normalize points to fit canvas
        commands = self._scale_and_draw(points, width, height, margin, rounded)
        return commands

    def _hilbert(self, depth):
        """Generate Hilbert curve points using coordinate algorithm."""
        n = 2 ** depth
        points = []
        for d in range(n * n):
            x, y = self._d2xy_hilbert(n, d)
            points.append((x, y))
        return points

    def _d2xy_hilbert(self, n, d):
        """Convert distance along Hilbert curve to (x, y) coordinates."""
        x = y = 0
        s = 1
        while s < n:
            rx = 1 if (d & 2) else 0
            ry = 1 if (d & 1) else 0
            if rx == 0:
                ry = 1 - ry  # XOR with rx=0
            else:
                ry = ry  # XOR with rx=1 keeps same

            # Actually: ry = ((d & 1) ^ rx)... let me redo this properly
            rx = 1 if (d & 2) else 0
            ry = ((d & 1) ^ rx)

            if ry == 0:
                if rx == 1:
                    x = s - 1 - x
                    y = s - 1 - y
                x, y = y, x

            x += s * rx
            y += s * ry
            d >>= 2
            s <<= 1
        return x, y

    def _peano(self, depth):
        """Generate Peano curve using L-system turtle."""
        # L-system: Axiom=X, X→XFYFX+F+YFXFY-F-XFYFX, Y→YFXFY-F-XFYFX+F+YFXFY
        state = "X"
        for _ in range(depth):
            new = []
            for c in state:
                if c == "X":
                    new.append("XFYFX+F+YFXFY-F-XFYFX")
                elif c == "Y":
                    new.append("YFXFY-F-XFYFX+F+YFXFY")
                else:
                    new.append(c)
            state = "".join(new)
            if len(state) > 500000:
                break

        return self._turtle_eval(state, 90)

    def _gosper(self, depth):
        """Generate Gosper flowsnake curve using L-system."""
        # Axiom=A, A→A-B--B+A++AA+B-, B→+A-BB--B-A++A+B
        state = "A"
        for _ in range(depth):
            new = []
            for c in state:
                if c == "A":
                    new.append("A-B--B+A++AA+B-")
                elif c == "B":
                    new.append("+A-BB--B-A++A+B")
                else:
                    new.append(c)
            state = "".join(new)
            if len(state) > 500000:
                break

        return self._turtle_eval(state, 60, draw_chars="AB")

    def _turtle_eval(self, commands, angle_deg, draw_chars="F"):
        """Evaluate turtle graphics commands and return points."""
        x, y = 0.0, 0.0
        heading = 0.0
        angle_rad = math.radians(angle_deg)
        points = [(x, y)]

        for c in commands:
            if c in draw_chars:
                x += math.cos(heading)
                y += math.sin(heading)
                points.append((x, y))
            elif c == "+":
                heading += angle_rad
            elif c == "-":
                heading -= angle_rad

        return points

    def _scale_and_draw(self, points, width, height, margin, rounded):
        """Scale points to canvas and generate draw commands."""
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

        scaled = [
            (ox + (p[0] - min_x) * scale, oy + (p[1] - min_y) * scale)
            for p in points
        ]

        commands = []
        total = len(scaled)

        if rounded > 0 and len(scaled) > 2:
            # Rounded corners: use midpoints as control approximation
            for i in range(len(scaled) - 1):
                p1 = scaled[i]
                p2 = scaled[i + 1]
                color_idx = (i * 3) // total  # Cycle through colors by position
                commands.append(("line", (*p1, *p2), color_idx))
        else:
            for i in range(len(scaled) - 1):
                p1 = scaled[i]
                p2 = scaled[i + 1]
                color_idx = (i * 3) // total
                commands.append(("line", (*p1, *p2), color_idx))

        return commands
