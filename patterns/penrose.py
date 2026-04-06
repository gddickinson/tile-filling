"""Penrose tiling (P3 - rhombus) via subdivision."""

import math
from typing import Dict, List, Tuple
from patterns.base import BasePattern, DrawCommand
from utils.geometry import PHI, lerp_point

# Triangle types for Robinson decomposition
THIN = 0
THICK = 1


class PenrosePattern(BasePattern):
    """Penrose P3 tiling using recursive subdivision of Robinson triangles."""

    name = "Penrose Tiling"
    description = "Aperiodic Penrose tiling with golden ratio proportions"

    @staticmethod
    def get_params() -> List[Dict]:
        return [
            {"name": "subdivisions", "label": "Subdivisions", "type": "int", "min": 1, "max": 8, "default": 5},
            {"name": "draw_triangles", "label": "Show Triangles", "type": "bool", "min": 0, "max": 1, "default": False},
            {"name": "draw_rhombs", "label": "Show Rhombs", "type": "bool", "min": 0, "max": 1, "default": True},
            {"name": "initial_shape", "label": "Initial (0=Sun,1=Star)", "type": "int", "min": 0, "max": 1, "default": 0},
        ]

    def generate(self, width: float, height: float, params: Dict, margin: float = 40) -> List[DrawCommand]:
        subdivisions = params.get("subdivisions", 5)
        draw_tri = params.get("draw_triangles", False)
        draw_rhombs = params.get("draw_rhombs", True)
        initial = params.get("initial_shape", 0)

        commands = []
        cx = width / 2
        cy = height / 2
        size = min(width, height) / 2 - margin

        # Start with a decagon of triangles
        triangles = self._initial_triangles(cx, cy, size, initial)

        # Subdivide
        for _ in range(subdivisions):
            triangles = self._subdivide(triangles)

        if draw_tri:
            for tri_type, a, b, c in triangles:
                color_idx = 0 if tri_type == THICK else 1
                commands.append(("line", (*a, *b), color_idx))
                commands.append(("line", (*b, *c), color_idx))
                commands.append(("line", (*c, *a), color_idx))

        if draw_rhombs:
            rhombs = self._extract_rhombs(triangles)
            for verts, rtype in rhombs:
                color_idx = 0 if rtype == THICK else 1
                for i in range(4):
                    p1 = verts[i]
                    p2 = verts[(i + 1) % 4]
                    commands.append(("line", (*p1, *p2), color_idx))

        return commands

    def _initial_triangles(self, cx, cy, size, shape_type):
        """Create initial set of triangles forming a decagon."""
        triangles = []
        for i in range(10):
            angle1 = (2 * i - 1) * math.pi / 10
            angle2 = (2 * i + 1) * math.pi / 10

            if shape_type == 0:  # Sun
                b = (cx + size * math.cos(angle1), cy + size * math.sin(angle1))
                c = (cx + size * math.cos(angle2), cy + size * math.sin(angle2))
                if i % 2 == 0:
                    triangles.append((THICK, (cx, cy), b, c))
                else:
                    triangles.append((THICK, (cx, cy), c, b))
            else:  # Star
                b = (cx + size * math.cos(angle1), cy + size * math.sin(angle1))
                c = (cx + size * math.cos(angle2), cy + size * math.sin(angle2))
                if i % 2 == 0:
                    triangles.append((THIN, (cx, cy), b, c))
                else:
                    triangles.append((THIN, (cx, cy), c, b))

        return triangles

    def _subdivide(self, triangles):
        """Perform one level of Robinson triangle subdivision."""
        result = []
        for tri_type, a, b, c in triangles:
            if tri_type == THICK:
                # Subdivide thick (acute) triangle
                p = lerp_point(a, c, 1 / PHI)
                q = lerp_point(b, a, 1 / PHI)
                result.append((THICK, q, p, b))
                result.append((THICK, p, q, a))
                result.append((THIN, p, c, b))
            else:
                # Subdivide thin (obtuse) triangle
                r = lerp_point(a, b, 1 / PHI)
                result.append((THIN, r, c, a))
                result.append((THICK, c, r, b))

        return result

    def _extract_rhombs(self, triangles):
        """Pair up triangles into rhombs based on shared edges."""
        # Group triangles by their type and midpoint of edge b-c
        edge_map = {}
        used = set()
        rhombs = []

        for idx, (tri_type, a, b, c) in enumerate(triangles):
            mid = (round((b[0] + c[0]) / 2, 4), round((b[1] + c[1]) / 2, 4))
            key = (tri_type, mid)
            if key in edge_map:
                other_idx = edge_map[key]
                if other_idx not in used and idx not in used:
                    _, a2, b2, c2 = triangles[other_idx]
                    # Form rhomb from the two triangles
                    rhombs.append(([a, b, a2, c], tri_type))
                    used.add(idx)
                    used.add(other_idx)
            else:
                edge_map[key] = idx

        # Draw remaining unpaired triangles as-is
        for idx, (tri_type, a, b, c) in enumerate(triangles):
            if idx not in used:
                rhombs.append(([a, b, c, a], tri_type))

        return rhombs
