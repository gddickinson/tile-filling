"""Voronoi tessellation patterns."""

import math
import random
from typing import Dict, List, Tuple
from patterns.base import BasePattern, DrawCommand


class VoronoiPattern(BasePattern):
    """Voronoi tessellation - organic cell-like patterns from random seed points."""

    name = "Voronoi"
    description = "Organic tessellation from random or structured seed points"

    @staticmethod
    def get_params() -> List[Dict]:
        return [
            {"name": "num_points", "label": "Number of Points", "type": "int", "min": 5, "max": 300, "default": 50},
            {"name": "seed", "label": "Random Seed", "type": "int", "min": 0, "max": 9999, "default": 42},
            {"name": "relax_steps", "label": "Lloyd Relaxation", "type": "int", "min": 0, "max": 10, "default": 2},
            {"name": "show_points", "label": "Show Seeds", "type": "bool", "min": 0, "max": 1, "default": True},
            {"name": "dual_mode", "label": "Delaunay Dual", "type": "bool", "min": 0, "max": 1, "default": False},
        ]

    def generate(self, width: float, height: float, params: Dict, margin: float = 40) -> List[DrawCommand]:
        n = params.get("num_points", 50)
        seed = params.get("seed", 42)
        relax = params.get("relax_steps", 2)
        show_pts = params.get("show_points", True)
        dual = params.get("dual_mode", False)

        random.seed(seed)
        commands = []

        x0, y0 = margin, margin
        w = width - 2 * margin
        h = height - 2 * margin

        # Generate seed points
        points = [(random.random() * w + x0, random.random() * h + y0) for _ in range(n)]

        # Lloyd relaxation
        for _ in range(relax):
            points = self._lloyd_relax(points, x0, y0, w, h)

        if dual:
            # Draw Delaunay triangulation
            triangles = self._delaunay(points)
            for i1, i2, i3 in triangles:
                p1, p2, p3 = points[i1], points[i2], points[i3]
                commands.append(("line", (*p1, *p2), 0))
                commands.append(("line", (*p2, *p3), 0))
                commands.append(("line", (*p3, *p1), 0))
        else:
            # Draw Voronoi edges using brute-force approach
            self._draw_voronoi_edges(commands, points, x0, y0, w, h)

        if show_pts:
            for px, py in points:
                commands.append(("circle", (px, py, 2), 2))

        return commands

    def _lloyd_relax(self, points, x0, y0, w, h):
        """One step of Lloyd relaxation - move each point toward its cell centroid."""
        # Simple grid-based approximation
        grid_res = 100
        dx = w / grid_res
        dy = h / grid_res

        centroids = [(0.0, 0.0)] * len(points)
        counts = [0] * len(points)

        for gi in range(grid_res):
            for gj in range(grid_res):
                sx = x0 + (gi + 0.5) * dx
                sy = y0 + (gj + 0.5) * dy

                # Find nearest point
                best = 0
                best_d = float("inf")
                for pi, (px, py) in enumerate(points):
                    d = (sx - px) ** 2 + (sy - py) ** 2
                    if d < best_d:
                        best_d = d
                        best = pi

                cx, cy = centroids[best]
                centroids[best] = (cx + sx, cy + sy)
                counts[best] = counts[best] + 1

        new_points = []
        for i, (px, py) in enumerate(points):
            if counts[i] > 0:
                cx, cy = centroids[i]
                new_points.append((cx / counts[i], cy / counts[i]))
            else:
                new_points.append((px, py))

        return new_points

    def _draw_voronoi_edges(self, commands, points, x0, y0, w, h):
        """Draw Voronoi edges by scanning for cell boundaries."""
        # Use Delaunay to find Voronoi edges (dual)
        triangles = self._delaunay(points)
        drawn_edges = set()

        for i1, i2, i3 in triangles:
            p1, p2, p3 = points[i1], points[i2], points[i3]
            cc = self._circumcenter(p1, p2, p3)
            if cc is None:
                continue

            # Find neighboring triangles sharing each edge
            for edge in [(i1, i2), (i2, i3), (i3, i1)]:
                e = tuple(sorted(edge))
                if e in drawn_edges:
                    continue

                # Find the other triangle sharing this edge
                neighbor_cc = None
                for t2 in triangles:
                    if t2 == (i1, i2, i3):
                        continue
                    t2_set = {t2[0], t2[1], t2[2]}
                    if e[0] in t2_set and e[1] in t2_set:
                        neighbor_cc = self._circumcenter(
                            points[t2[0]], points[t2[1]], points[t2[2]]
                        )
                        break

                drawn_edges.add(e)
                if neighbor_cc:
                    # Clip to bounds
                    lx1 = max(x0, min(x0 + w, cc[0]))
                    ly1 = max(y0, min(y0 + h, cc[1]))
                    lx2 = max(x0, min(x0 + w, neighbor_cc[0]))
                    ly2 = max(y0, min(y0 + h, neighbor_cc[1]))
                    commands.append(("line", (lx1, ly1, lx2, ly2), 0))

    def _circumcenter(self, p1, p2, p3):
        ax, ay = p1
        bx, by = p2
        cx, cy = p3
        d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        if abs(d) < 1e-10:
            return None
        ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) +
              (cx * cx + cy * cy) * (ay - by)) / d
        uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) +
              (cx * cx + cy * cy) * (bx - ax)) / d
        return (ux, uy)

    def _delaunay(self, points):
        """Simple Bowyer-Watson Delaunay triangulation."""
        if len(points) < 3:
            return []

        # Super-triangle
        min_x = min(p[0] for p in points) - 1
        min_y = min(p[1] for p in points) - 1
        max_x = max(p[0] for p in points) + 1
        max_y = max(p[1] for p in points) + 1
        dx = max_x - min_x
        dy = max_y - min_y
        dmax = max(dx, dy) * 10

        sp1 = (min_x - dmax, min_y - 1)
        sp2 = (min_x + dmax * 2, min_y - 1)
        sp3 = (min_x + dx / 2, max_y + dmax)

        all_pts = list(points) + [sp1, sp2, sp3]
        n = len(points)
        si1, si2, si3 = n, n + 1, n + 2

        triangles = [(si1, si2, si3)]

        for pi in range(n):
            px, py = all_pts[pi]
            bad = []
            for tri in triangles:
                cc = self._circumcenter(all_pts[tri[0]], all_pts[tri[1]], all_pts[tri[2]])
                if cc is None:
                    continue
                r2 = (all_pts[tri[0]][0] - cc[0]) ** 2 + (all_pts[tri[0]][1] - cc[1]) ** 2
                d2 = (px - cc[0]) ** 2 + (py - cc[1]) ** 2
                if d2 < r2:
                    bad.append(tri)

            polygon = []
            for tri in bad:
                for edge in [(tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])]:
                    shared = False
                    for other in bad:
                        if other == tri:
                            continue
                        other_edges = [(other[0], other[1]), (other[1], other[2]), (other[2], other[0])]
                        for oe in other_edges:
                            if (edge[0] == oe[1] and edge[1] == oe[0]) or edge == oe:
                                shared = True
                                break
                        if shared:
                            break
                    if not shared:
                        polygon.append(edge)

            for tri in bad:
                triangles.remove(tri)

            for e in polygon:
                triangles.append((pi, e[0], e[1]))

        # Remove triangles connected to super-triangle
        triangles = [t for t in triangles if t[0] < n and t[1] < n and t[2] < n]
        return triangles
