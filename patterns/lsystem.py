"""L-System fractal patterns - recursive string rewriting with turtle graphics."""

import math
from typing import Dict, List
from patterns.base import BasePattern, DrawCommand

# Preset L-systems: (axiom, rules, angle, draw_chars, name)
PRESETS = [
    {
        "name": "Koch Snowflake",
        "axiom": "F++F++F",
        "rules": {"F": "F-F++F-F"},
        "angle": 60,
        "draw": "F",
    },
    {
        "name": "Dragon Curve",
        "axiom": "FX",
        "rules": {"X": "X+YF+", "Y": "-FX-Y"},
        "angle": 90,
        "draw": "F",
    },
    {
        "name": "Sierpinski Arrow",
        "axiom": "A",
        "rules": {"A": "B-A-B", "B": "A+B+A"},
        "angle": 60,
        "draw": "AB",
    },
    {
        "name": "Plant Fractal",
        "axiom": "X",
        "rules": {"X": "F+[[X]-X]-F[-FX]+X", "F": "FF"},
        "angle": 25,
        "draw": "F",
    },
    {
        "name": "Pentigree",
        "axiom": "F-F-F-F-F",
        "rules": {"F": "F-F++F+F-F-F"},
        "angle": 72,
        "draw": "F",
    },
    {
        "name": "Crystal",
        "axiom": "F+F+F+F",
        "rules": {"F": "FF+F++F+F"},
        "angle": 90,
        "draw": "F",
    },
    {
        "name": "Quadratic Gosper",
        "axiom": "-YF",
        "rules": {
            "X": "XFX-YF-YF+FX+FX-YF-YFFX+YF+FXFXYF-FX+YF+FXFX+YF-FXYF-YF-FX+FX+YFYF-",
            "Y": "+FXFX-YF-YF+FX+FXYF+FX-YFYF-FX-YF+FXYFYF-FX-YFFX+FX+YF-YF-FX+FX+YFY",
        },
        "angle": 90,
        "draw": "F",
    },
]


class LSystemPattern(BasePattern):
    """L-System fractals - recursive rewriting produces organic and geometric forms."""

    name = "L-System"
    description = "Koch, Dragon, Plant, and other fractal patterns from grammar rules"

    @staticmethod
    def get_params() -> List[Dict]:
        return [
            {"name": "preset", "label": "Preset (0-6)", "type": "int", "min": 0, "max": len(PRESETS) - 1, "default": 0},
            {"name": "iterations", "label": "Iterations", "type": "int", "min": 1, "max": 8, "default": 4},
            {"name": "angle_adjust", "label": "Angle Adjust", "type": "float", "min": -15.0, "max": 15.0, "default": 0.0},
            {"name": "start_angle", "label": "Start Angle (deg)", "type": "float", "min": 0.0, "max": 360.0, "default": 0.0},
        ]

    def generate(self, width: float, height: float, params: Dict, margin: float = 40) -> List[DrawCommand]:
        preset_idx = params.get("preset", 0)
        iterations = params.get("iterations", 4)
        angle_adj = params.get("angle_adjust", 0.0)
        start_angle = params.get("start_angle", 0.0)

        preset = PRESETS[preset_idx % len(PRESETS)]

        # Generate L-system string
        state = preset["axiom"]
        rules = preset["rules"]
        for _ in range(iterations):
            new = []
            for c in state:
                new.append(rules.get(c, c))
            state = "".join(new)
            if len(state) > 1000000:
                break

        # Interpret with turtle
        angle = preset["angle"] + angle_adj
        draw_chars = preset["draw"]
        points = self._turtle(state, angle, draw_chars, start_angle)

        return self._scale_and_draw(points, width, height, margin)

    def _turtle(self, commands, angle_deg, draw_chars, start_angle):
        """Turtle graphics interpreter with stack for branching."""
        x, y = 0.0, 0.0
        heading = math.radians(start_angle)
        angle_rad = math.radians(angle_deg)
        stack = []
        segments = []  # List of (start, end) point pairs

        for c in commands:
            if c in draw_chars:
                nx = x + math.cos(heading)
                ny = y + math.sin(heading)
                segments.append(((x, y), (nx, ny)))
                x, y = nx, ny
            elif c == "f":
                x += math.cos(heading)
                y += math.sin(heading)
            elif c == "+":
                heading += angle_rad
            elif c == "-":
                heading -= angle_rad
            elif c == "[":
                stack.append((x, y, heading))
            elif c == "]":
                if stack:
                    x, y, heading = stack.pop()

        return segments

    def _scale_and_draw(self, segments, width, height, margin):
        """Scale segments to fit canvas."""
        if not segments:
            return []

        all_x = [p[0] for s in segments for p in s]
        all_y = [p[1] for s in segments for p in s]
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        range_x = max_x - min_x or 1
        range_y = max_y - min_y or 1

        w = width - 2 * margin
        h = height - 2 * margin
        scale = min(w / range_x, h / range_y)
        ox = margin + (w - range_x * scale) / 2
        oy = margin + (h - range_y * scale) / 2

        commands = []
        total = len(segments)
        for i, (p1, p2) in enumerate(segments):
            x1 = ox + (p1[0] - min_x) * scale
            y1 = oy + (p1[1] - min_y) * scale
            x2 = ox + (p2[0] - min_x) * scale
            y2 = oy + (p2[1] - min_y) * scale
            color_idx = (i * 3) // total
            commands.append(("line", (x1, y1, x2, y2), color_idx))

        return commands
