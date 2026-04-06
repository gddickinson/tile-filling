"""Flow field patterns - noise-driven particle traces."""

import math
import random
from typing import Dict, List
from patterns.base import BasePattern, DrawCommand


class FlowFieldPattern(BasePattern):
    """Flow fields - particles trace paths through a Perlin-like noise field.

    One of the most popular generative art techniques. Particles follow
    angle fields derived from layered sine/cosine functions, creating
    organic, flowing compositions.
    """

    name = "Flow Field"
    description = "Noise-driven particle traces creating organic flowing patterns"

    @staticmethod
    def get_params() -> List[Dict]:
        return [
            {"name": "particles", "label": "Particle Count", "type": "int", "min": 50, "max": 2000, "default": 500},
            {"name": "steps", "label": "Steps Per Particle", "type": "int", "min": 10, "max": 200, "default": 80},
            {"name": "step_size", "label": "Step Size", "type": "float", "min": 0.5, "max": 5.0, "default": 2.0},
            {"name": "noise_scale", "label": "Noise Scale", "type": "float", "min": 0.001, "max": 0.02, "default": 0.005},
            {"name": "octaves", "label": "Noise Octaves", "type": "int", "min": 1, "max": 5, "default": 3},
            {"name": "seed", "label": "Random Seed", "type": "int", "min": 0, "max": 9999, "default": 42},
            {"name": "curl", "label": "Curl Factor", "type": "float", "min": 0.0, "max": 3.0, "default": 1.0},
        ]

    def generate(self, width: float, height: float, params: Dict, margin: float = 40) -> List[DrawCommand]:
        n_particles = params.get("particles", 500)
        steps = params.get("steps", 80)
        step_size = params.get("step_size", 2.0)
        noise_scale = params.get("noise_scale", 0.005)
        octaves = params.get("octaves", 3)
        seed = params.get("seed", 42)
        curl = params.get("curl", 1.0)

        random.seed(seed)
        commands = []

        x0, y0 = margin, margin
        w = width - 2 * margin
        h = height - 2 * margin

        for p in range(n_particles):
            # Random starting position
            px = x0 + random.random() * w
            py = y0 + random.random() * h

            for s in range(steps):
                # Compute flow angle from noise
                angle = self._noise_angle(px, py, noise_scale, octaves, seed, curl)

                # Step forward
                nx = px + math.cos(angle) * step_size
                ny = py + math.sin(angle) * step_size

                # Bounds check
                if nx < x0 or nx > x0 + w or ny < y0 or ny > y0 + h:
                    break

                color_idx = (p * 4) // n_particles
                commands.append(("line", (px, py, nx, ny), color_idx))

                px, py = nx, ny

        return commands

    def _noise_angle(self, x, y, scale, octaves, seed, curl):
        """Compute flow angle using layered trigonometric noise."""
        angle = 0.0
        amplitude = 1.0
        frequency = scale

        for o in range(octaves):
            # Pseudo-noise using sine combinations (no external dependency)
            n = (math.sin(x * frequency * 1.7 + seed * 13.37 + o * 5.1) *
                 math.cos(y * frequency * 2.3 + seed * 7.13 + o * 3.7) +
                 math.sin((x + y) * frequency * 0.9 + seed * 11.1 + o * 2.3) * 0.5)

            angle += n * amplitude * math.pi * curl
            amplitude *= 0.5
            frequency *= 2.0

        return angle
