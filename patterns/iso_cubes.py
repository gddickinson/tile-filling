"""Isometric 3D cube grid pattern with height variation."""

import math
import random
from typing import Dict, List
from patterns.base import BasePattern, DrawCommand
from rendering.projection import rotate_xyz, project_isometric


class IsoCubesPattern(BasePattern):
    """Isometric cube grid - 3D blocks with procedural height variation."""

    name = "Isometric Cubes"
    description = "3D cube grid with height variation in isometric projection"

    @staticmethod
    def get_params() -> List[Dict]:
        return [
            {"name": "grid_size", "label": "Grid Size", "type": "int", "min": 3, "max": 15, "default": 7},
            {"name": "max_height", "label": "Max Height", "type": "int", "min": 1, "max": 8, "default": 4},
            {"name": "seed", "label": "Random Seed", "type": "int", "min": 0, "max": 9999, "default": 42},
            {"name": "height_mode", "label": "Height (0=Rand,1=Wave,2=Pyramid)", "type": "int", "min": 0, "max": 2, "default": 1},
            {"name": "show_hidden", "label": "Show Hidden Lines", "type": "bool", "min": 0, "max": 1, "default": False},
            {"name": "rotation", "label": "Y Rotation (deg)", "type": "float", "min": -45.0, "max": 45.0, "default": 0.0},
        ]

    def generate(self, width: float, height: float, params: Dict, margin: float = 40) -> List[DrawCommand]:
        gs = params.get("grid_size", 7)
        max_h = params.get("max_height", 4)
        seed = params.get("seed", 42)
        h_mode = params.get("height_mode", 1)
        show_hidden = params.get("show_hidden", False)
        rot_y = math.radians(params.get("rotation", 0.0))

        random.seed(seed)

        # Generate height map
        heights = self._gen_heights(gs, max_h, h_mode, seed)

        # Calculate scale to fit
        cx, cy = width / 2, height / 2
        cube_size = min(width, height) / (gs * 2.5)

        commands = []

        # Draw cubes back to front (painter's algorithm)
        for i in range(gs):
            for j in range(gs):
                h = heights[i][j]
                if h <= 0:
                    continue
                self._draw_cube(
                    commands, i, j, h, gs, cube_size,
                    cx, cy, rot_y, show_hidden
                )

        return commands

    def _gen_heights(self, gs, max_h, mode, seed):
        """Generate height map for the grid."""
        heights = [[0] * gs for _ in range(gs)]

        if mode == 0:  # Random
            random.seed(seed)
            for i in range(gs):
                for j in range(gs):
                    heights[i][j] = random.randint(1, max_h)

        elif mode == 1:  # Wave
            for i in range(gs):
                for j in range(gs):
                    h = math.sin(i * 0.8) * math.cos(j * 0.8)
                    heights[i][j] = max(1, int((h + 1) / 2 * max_h + 0.5))

        elif mode == 2:  # Pyramid
            center = gs / 2.0
            for i in range(gs):
                for j in range(gs):
                    dist = max(abs(i - center), abs(j - center)) / center
                    heights[i][j] = max(1, int((1 - dist) * max_h + 0.5))

        return heights

    def _draw_cube(self, commands, gi, gj, h, gs, size, cx, cy, rot_y, show_hidden):
        """Draw a single cube at grid position (gi, gj) with height h."""
        # Center the grid
        ox = (gi - gs / 2) * size
        oz = (gj - gs / 2) * size

        # 8 vertices of the cube
        verts_3d = [
            (ox, 0, oz),                    # 0: bottom-front-left
            (ox + size, 0, oz),             # 1: bottom-front-right
            (ox + size, 0, oz + size),      # 2: bottom-back-right
            (ox, 0, oz + size),             # 3: bottom-back-left
            (ox, h * size * 0.5, oz),               # 4: top-front-left
            (ox + size, h * size * 0.5, oz),        # 5: top-front-right
            (ox + size, h * size * 0.5, oz + size), # 6: top-back-right
            (ox, h * size * 0.5, oz + size),        # 7: top-back-left
        ]

        # Apply rotation
        if rot_y != 0:
            verts_3d = [rotate_xyz(v, 0, rot_y, 0) for v in verts_3d]

        # Project to 2D
        scale = min(cx, cy) * 0.8 / (gs * size * 0.5) if gs > 0 else 1
        verts_2d = []
        for v in verts_3d:
            pt, _ = project_isometric(v, cx, cy, scale)
            verts_2d.append(pt)

        # Draw edges - top face (always visible)
        top_edges = [(4, 5), (5, 6), (6, 7), (7, 4)]
        for a, b in top_edges:
            p1, p2 = verts_2d[a], verts_2d[b]
            commands.append(("line", (*p1, *p2), 0))

        # Front-left and front-right vertical edges
        front_edges = [(0, 4), (1, 5)]
        for a, b in front_edges:
            p1, p2 = verts_2d[a], verts_2d[b]
            commands.append(("line", (*p1, *p2), 1))

        # Bottom front edge
        commands.append(("line", (*verts_2d[0], *verts_2d[1]), 1))

        # Right side vertical edges
        right_edges = [(1, 5), (2, 6)]
        for a, b in right_edges:
            p1, p2 = verts_2d[a], verts_2d[b]
            commands.append(("line", (*p1, *p2), 1))

        # Bottom right edge
        commands.append(("line", (*verts_2d[1], *verts_2d[2]), 1))

        if show_hidden:
            # Draw back and bottom hidden edges
            hidden_edges = [(2, 3), (3, 0), (3, 7), (2, 6), (0, 3)]
            for a, b in hidden_edges:
                p1, p2 = verts_2d[a], verts_2d[b]
                commands.append(("line", (*p1, *p2), 2))
