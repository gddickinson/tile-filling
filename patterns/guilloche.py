"""Guilloche patterns - fine-line engraving patterns used on banknotes and certificates."""

import math
from typing import Dict, List
from patterns.base import BasePattern, DrawCommand


class GuillochePattern(BasePattern):
    """Guilloche - intricate fine-line engraving patterns.

    Created by tracing a point on a circle rolling inside/outside another circle,
    with modulated radius. Produces the ornate patterns seen on currency and
    security documents.
    """

    name = "Guilloche"
    description = "Fine-line engraving patterns inspired by banknote security art"

    @staticmethod
    def get_params() -> List[Dict]:
        return [
            {"name": "waves", "label": "Wave Count", "type": "int", "min": 20, "max": 200, "default": 80},
            {"name": "amplitude", "label": "Wave Amplitude", "type": "float", "min": 5.0, "max": 80.0, "default": 30.0},
            {"name": "freq", "label": "Wave Frequency", "type": "float", "min": 1.0, "max": 20.0, "default": 6.0},
            {"name": "shape", "label": "Shape (0=Circle,1=Oval,2=Rect,3=Rose)", "type": "int", "min": 0, "max": 3, "default": 0},
            {"name": "modulation", "label": "Modulation", "type": "float", "min": 0.0, "max": 1.0, "default": 0.3},
            {"name": "resolution", "label": "Points per Wave", "type": "int", "min": 100, "max": 1000, "default": 400},
        ]

    def generate(self, width: float, height: float, params: Dict, margin: float = 40) -> List[DrawCommand]:
        n_waves = params.get("waves", 80)
        amplitude = params.get("amplitude", 30.0)
        freq = params.get("freq", 6.0)
        shape = params.get("shape", 0)
        modulation = params.get("modulation", 0.3)
        resolution = params.get("resolution", 400)

        commands = []
        cx, cy = width / 2, height / 2
        w = width - 2 * margin
        h = height - 2 * margin

        for wave in range(n_waves):
            t_offset = wave / n_waves
            base_r = (0.2 + 0.7 * wave / n_waves)
            color_idx = (wave * 3) // n_waves

            points = []
            for i in range(resolution + 1):
                t = 2 * math.pi * i / resolution

                # Base shape
                if shape == 0:  # Circle
                    bx = math.cos(t)
                    by = math.sin(t)
                elif shape == 1:  # Oval
                    bx = math.cos(t)
                    by = math.sin(t) * 0.6
                elif shape == 2:  # Rounded rectangle
                    bx = math.cos(t) * (1.0 + 0.3 * math.cos(2 * t))
                    by = math.sin(t) * (0.6 + 0.2 * math.cos(2 * t))
                else:  # Rose
                    rose_r = math.cos(3 * t)
                    bx = rose_r * math.cos(t)
                    by = rose_r * math.sin(t)

                # Modulated wave along the path normal
                wave_val = math.sin(freq * t + t_offset * 2 * math.pi)
                mod = 1.0 + modulation * math.sin(3 * t + wave * 0.1)
                offset = amplitude * wave_val * mod * (1.0 / n_waves)

                # Normal direction (perpendicular to tangent)
                nx = -by  # Simplified normal
                ny = bx
                norm = math.hypot(nx, ny) or 1
                nx /= norm
                ny /= norm

                r = base_r * min(w, h) / 2
                px = cx + bx * r + nx * offset
                py = cy + by * r + ny * offset
                points.append((px, py))

            # Draw the wave
            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i + 1]
                commands.append(("line", (*p1, *p2), color_idx))

        return commands
