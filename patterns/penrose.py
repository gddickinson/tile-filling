"""Penrose tiling (P3 - rhombus) via Robinson-triangle subdivision.

Every rhombus is split along a diagonal into two mirror-image golden triangles (type, A, B, C), apex A, base BC:
- THIN: apex 36 deg, legs AB = AC = rhombus side, base BC = the short diagonal of a thin (36/144 deg) rhombus;
- THICK: apex 108 deg, legs = rhombus side, base BC = the long diagonal of a thick (72/108 deg) rhombus.
Subdividing replaces each triangle by smaller ones of the same two shapes (sides divided by the golden ratio), which
keeps the edge-matching rules of the P3 tiling (Preshing's formulation of the Robinson decomposition). Two triangles
of a type that share their base form one rhombus; the rhombus edges are the triangle legs.
"""

import math
from typing import Dict, List
from patterns.base import BasePattern, DrawCommand
from utils.geometry import PHI

# Triangle types for Robinson decomposition
THIN = 0
THICK = 1


def _toward(p, q, t):
    """p + (q - p) * t."""
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


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

        triangles = self.tiling(cx, cy, size, initial, subdivisions)

        if draw_tri:
            for tri_type, a, b, c in triangles:
                color_idx = 0 if tri_type == THICK else 1
                commands.append(("line", (*a, *b), color_idx))
                commands.append(("line", (*b, *c), color_idx))
                commands.append(("line", (*c, *a), color_idx))

        if draw_rhombs:
            rhombs, halves = self._extract_rhombs(triangles)
            for verts, rtype in rhombs:
                color_idx = 0 if rtype == THICK else 1
                for i in range(4):
                    p1 = verts[i]
                    p2 = verts[(i + 1) % 4]
                    commands.append(("line", (*p1, *p2), color_idx))
            # Half rhombs cut by the edge of the patch: only their two rhombus sides are tile edges
            for tri_type, a, b, c in halves:
                color_idx = 0 if tri_type == THICK else 1
                commands.append(("line", (*a, *b), color_idx))
                commands.append(("line", (*a, *c), color_idx))

        return commands

    def tiling(self, cx, cy, size, shape_type, subdivisions):
        """Robinson triangles of the subdivided Sun (0) or Star (1) patch of radius `size`."""
        triangles = self._initial_triangles(cx, cy, size, shape_type)
        for _ in range(subdivisions):
            triangles = self._subdivide(triangles)
        return triangles

    def _initial_triangles(self, cx, cy, size, shape_type):
        """Sun: ten thin triangles around the centre (a decagon). Star: five thick rhombs meeting at the centre."""
        triangles = []
        if shape_type == 0:  # Sun
            for i in range(10):
                angle1 = (2 * i - 1) * math.pi / 10
                angle2 = (2 * i + 1) * math.pi / 10
                b = (cx + size * math.cos(angle1), cy + size * math.sin(angle1))
                c = (cx + size * math.cos(angle2), cy + size * math.sin(angle2))
                if i % 2 == 0:
                    b, c = c, b  # neighbours are mirror images
                triangles.append((THIN, (cx, cy), b, c))
        else:  # Star
            side = size / PHI  # the long diagonal (centre to tip) of a thick rhomb is side * PHI
            for k in range(5):
                theta = 2 * math.pi * k / 5 - math.pi / 2
                tip = (cx + size * math.cos(theta), cy + size * math.sin(theta))
                left = (cx + side * math.cos(theta - math.pi / 5), cy + side * math.sin(theta - math.pi / 5))
                right = (cx + side * math.cos(theta + math.pi / 5), cy + side * math.sin(theta + math.pi / 5))
                # both halves list the long diagonal centre -> tip in the same order, so neighbouring rhombs meet
                # leg to leg with matching orientation (the P3 edge-matching rule)
                triangles.append((THICK, left, (cx, cy), tip))
                triangles.append((THICK, right, (cx, cy), tip))
        return triangles

    def _subdivide(self, triangles):
        """Perform one level of Robinson triangle subdivision (sides shrink by the golden ratio)."""
        result = []
        for tri_type, a, b, c in triangles:
            if tri_type == THIN:
                p = _toward(a, b, 1 / PHI)
                result.append((THIN, c, p, b))
                result.append((THICK, p, c, a))
            else:
                q = _toward(b, a, 1 / PHI)
                r = _toward(b, c, 1 / PHI)
                result.append((THICK, r, c, a))
                result.append((THICK, q, r, b))
                result.append((THIN, r, q, a))
        return result

    def _extract_rhombs(self, triangles):
        """Pair the two halves of each rhomb (same type, same base BC) into [A, B, A', C]; return rhombs and the
        unpaired halves at the edge of the patch."""
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
                    rhombs.append(([a, b, a2, c], tri_type))
                    used.add(idx)
                    used.add(other_idx)
            else:
                edge_map[key] = idx

        halves = [t for idx, t in enumerate(triangles) if idx not in used]
        return rhombs, halves
