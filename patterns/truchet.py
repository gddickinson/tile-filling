"""Truchet tile patterns - oriented tiles creating emergent curves."""

import math
import random
from typing import Dict, List
from patterns.base import BasePattern, DrawCommand


class TruchetPattern(BasePattern):
    """Truchet tiles - simple tiles with oriented patterns that create
    beautiful emergent flowing curves and labyrinths."""

    name = "Truchet Tiles"
    description = "Oriented tiles creating emergent curves and patterns"

    @staticmethod
    def get_params() -> List[Dict]:
        return [
            {"name": "cols", "label": "Columns", "type": "int", "min": 3, "max": 40, "default": 15},
            {"name": "rows", "label": "Rows", "type": "int", "min": 3, "max": 40, "default": 15},
            {"name": "style", "label": "Style (0=Arc,1=Diag,2=Multi)", "type": "int", "min": 0, "max": 2, "default": 0},
            {"name": "seed", "label": "Random Seed", "type": "int", "min": 0, "max": 9999, "default": 42},
            {"name": "arc_segments", "label": "Arc Smoothness", "type": "int", "min": 4, "max": 20, "default": 12},
        ]

    def generate(self, width: float, height: float, params: Dict, margin: float = 40) -> List[DrawCommand]:
        cols = params.get("cols", 15)
        rows = params.get("rows", 15)
        style = params.get("style", 0)
        seed = params.get("seed", 42)
        arc_seg = params.get("arc_segments", 12)

        random.seed(seed)
        commands = []
        w = width - 2 * margin
        h = height - 2 * margin
        cw = w / cols
        ch = h / rows

        for i in range(cols):
            for j in range(rows):
                x = margin + i * cw
                y = margin + j * ch
                orientation = random.randint(0, 1)

                if style == 0:
                    self._draw_arc_tile(commands, x, y, cw, ch, orientation, arc_seg)
                elif style == 1:
                    self._draw_diagonal_tile(commands, x, y, cw, ch, orientation)
                else:
                    self._draw_multi_tile(commands, x, y, cw, ch, orientation, arc_seg)

        return commands

    def _draw_arc_tile(self, commands, x, y, w, h, orient, segments):
        """Quarter-circle arcs at two opposite corners."""
        r = min(w, h) / 2

        if orient == 0:
            # Arcs at top-left and bottom-right
            self._draw_arc(commands, x, y, r, 0, math.pi / 2, segments, 0)
            self._draw_arc(commands, x + w, y + h, r, math.pi, 3 * math.pi / 2, segments, 0)
        else:
            # Arcs at top-right and bottom-left
            self._draw_arc(commands, x + w, y, r, math.pi / 2, math.pi, segments, 0)
            self._draw_arc(commands, x, y + h, r, 3 * math.pi / 2, 2 * math.pi, segments, 0)

    def _draw_arc(self, commands, cx, cy, r, start, end, segments, color_idx):
        """Draw an arc as line segments."""
        for i in range(segments):
            a1 = start + (end - start) * i / segments
            a2 = start + (end - start) * (i + 1) / segments
            x1 = cx + r * math.cos(a1)
            y1 = cy + r * math.sin(a1)
            x2 = cx + r * math.cos(a2)
            y2 = cy + r * math.sin(a2)
            commands.append(("line", (x1, y1, x2, y2), color_idx))

    def _draw_diagonal_tile(self, commands, x, y, w, h, orient):
        """Simple diagonal line tile."""
        if orient == 0:
            commands.append(("line", (x, y, x + w, y + h), 0))
        else:
            commands.append(("line", (x + w, y, x, y + h), 0))

    def _draw_multi_tile(self, commands, x, y, w, h, orient, segments):
        """Multiple concentric arcs for richer patterns."""
        r_max = min(w, h) / 2
        for layer in range(3):
            r = r_max * (1 - layer * 0.25)
            if r <= 0:
                break
            color_idx = layer % 3

            if orient == 0:
                self._draw_arc(commands, x, y, r, 0, math.pi / 2, segments, color_idx)
                self._draw_arc(commands, x + w, y + h, r, math.pi, 3 * math.pi / 2, segments, color_idx)
            else:
                self._draw_arc(commands, x + w, y, r, math.pi / 2, math.pi, segments, color_idx)
                self._draw_arc(commands, x, y + h, r, 3 * math.pi / 2, 2 * math.pi, segments, color_idx)
