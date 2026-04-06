"""Simple grid and decorated grid patterns."""

import math
from typing import Dict, List
from patterns.base import BasePattern, DrawCommand


class GridPattern(BasePattern):
    """Simple rectangular grid - clean and minimal."""

    name = "Grid"
    description = "Clean rectangular grid with configurable spacing"

    @staticmethod
    def get_params() -> List[Dict]:
        return [
            {"name": "cols", "label": "Columns", "type": "int", "min": 2, "max": 50, "default": 10},
            {"name": "rows", "label": "Rows", "type": "int", "min": 2, "max": 50, "default": 10},
            {"name": "line_weight", "label": "Line Weight", "type": "float", "min": 0.5, "max": 5.0, "default": 1.0},
            {"name": "jitter", "label": "Jitter", "type": "float", "min": 0.0, "max": 1.0, "default": 0.0},
        ]

    def generate(self, width: float, height: float, params: Dict, margin: float = 40) -> List[DrawCommand]:
        import random
        cols = params.get("cols", 10)
        rows = params.get("rows", 10)
        jitter = params.get("jitter", 0.0)

        commands = []
        w = width - 2 * margin
        h = height - 2 * margin
        cw = w / cols
        ch = h / rows

        # Vertical lines
        for i in range(cols + 1):
            x = margin + i * cw
            jx = x + (random.random() - 0.5) * cw * jitter if jitter > 0 else x
            commands.append(("line", (jx, margin, jx, margin + h), 0))

        # Horizontal lines
        for j in range(rows + 1):
            y = margin + j * ch
            jy = y + (random.random() - 0.5) * ch * jitter if jitter > 0 else y
            commands.append(("line", (margin, jy, margin + w, jy), 0))

        return commands


class DecoratedGridPattern(BasePattern):
    """Grid with internal decorations - diagonals, stars, and radial lines.

    Matches the intricate pattern from the reference image.
    """

    name = "Decorated Grid"
    description = "Grid cells with internal star/radial decorations"

    @staticmethod
    def get_params() -> List[Dict]:
        return [
            {"name": "cols", "label": "Columns", "type": "int", "min": 2, "max": 30, "default": 8},
            {"name": "rows", "label": "Rows", "type": "int", "min": 2, "max": 30, "default": 8},
            {"name": "decoration", "label": "Decoration Level", "type": "int", "min": 0, "max": 5, "default": 3},
            {"name": "inner_scale", "label": "Inner Scale", "type": "float", "min": 0.1, "max": 0.9, "default": 0.5},
            {"name": "rotation", "label": "Rotation (deg)", "type": "float", "min": 0, "max": 45, "default": 0},
        ]

    def generate(self, width: float, height: float, params: Dict, margin: float = 40) -> List[DrawCommand]:
        cols = params.get("cols", 8)
        rows = params.get("rows", 8)
        decoration = params.get("decoration", 3)
        inner_scale = params.get("inner_scale", 0.5)
        rotation = math.radians(params.get("rotation", 0))

        commands = []
        w = width - 2 * margin
        h = height - 2 * margin
        cw = w / cols
        ch = h / rows

        # Draw base grid
        for i in range(cols + 1):
            x = margin + i * cw
            commands.append(("line", (x, margin, x, margin + h), 0))
        for j in range(rows + 1):
            y = margin + j * ch
            commands.append(("line", (margin, y, margin + w, y), 0))

        # Decorate each cell
        for i in range(cols):
            for j in range(rows):
                cx = margin + (i + 0.5) * cw
                cy = margin + (j + 0.5) * ch
                self._decorate_cell(commands, cx, cy, cw, ch, decoration, inner_scale, rotation)

        return commands

    def _decorate_cell(self, commands, cx, cy, cw, ch, level, scale, rotation):
        hw, hh = cw / 2, ch / 2

        # Corner points
        tl = (cx - hw, cy - hh)
        tr = (cx + hw, cy - hh)
        bl = (cx - hw, cy + hh)
        br = (cx + hw, cy + hh)

        # Edge midpoints
        tm = (cx, cy - hh)
        bm = (cx, cy + hh)
        lm = (cx - hw, cy)
        rm = (cx + hw, cy)

        center = (cx, cy)

        if level >= 1:
            # Diagonals corner to corner
            commands.append(("line", (*tl, *br), 1))
            commands.append(("line", (*tr, *bl), 1))

        if level >= 2:
            # Lines from center to edge midpoints
            commands.append(("line", (*center, *tm), 1))
            commands.append(("line", (*center, *bm), 1))
            commands.append(("line", (*center, *lm), 1))
            commands.append(("line", (*center, *rm), 1))

        if level >= 3:
            # Lines from center to corners
            commands.append(("line", (*center, *tl), 2))
            commands.append(("line", (*center, *tr), 2))
            commands.append(("line", (*center, *bl), 2))
            commands.append(("line", (*center, *br), 2))

            # Inner diamond connecting edge midpoints
            commands.append(("line", (*tm, *rm), 2))
            commands.append(("line", (*rm, *bm), 2))
            commands.append(("line", (*bm, *lm), 2))
            commands.append(("line", (*lm, *tm), 2))

        if level >= 4:
            # Inner scaled square
            s = scale
            itl = (cx - hw * s, cy - hh * s)
            itr = (cx + hw * s, cy - hh * s)
            ibl = (cx - hw * s, cy + hh * s)
            ibr = (cx + hw * s, cy + hh * s)

            commands.append(("line", (*itl, *itr), 2))
            commands.append(("line", (*itr, *ibr), 2))
            commands.append(("line", (*ibr, *ibl), 2))
            commands.append(("line", (*ibl, *itl), 2))

            # Connect inner to outer
            commands.append(("line", (*itl, *tl), 2))
            commands.append(("line", (*itr, *tr), 2))
            commands.append(("line", (*ibl, *bl), 2))
            commands.append(("line", (*ibr, *br), 2))

        if level >= 5:
            # Radial burst - 16 lines from center
            r = min(hw, hh) * 0.9
            for k in range(16):
                angle = rotation + k * math.pi / 8
                ex = cx + r * math.cos(angle)
                ey = cy + r * math.sin(angle)
                commands.append(("line", (cx, cy, ex, ey), 3))

            # Small circle at center
            commands.append(("circle", (cx, cy, min(hw, hh) * 0.08), 3))
