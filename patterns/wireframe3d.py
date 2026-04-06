"""3D wireframe surfaces - parametric surfaces rendered as wireframes."""

import math
from typing import Dict, List
from patterns.base import BasePattern, DrawCommand
from rendering.projection import rotate_xyz, project_perspective, depth_to_alpha
from rendering.colors import color_with_alpha


class Wireframe3DPattern(BasePattern):
    """3D wireframe surfaces - torus, Klein bottle, trefoil knot, and sphere."""

    name = "3D Wireframe"
    description = "Parametric 3D surfaces rendered as perspective wireframes"

    @staticmethod
    def get_params() -> List[Dict]:
        return [
            {"name": "surface", "label": "Surface (0=Torus,1=Knot,2=Sphere,3=Klein,4=Mobius)", "type": "int", "min": 0, "max": 4, "default": 0},
            {"name": "resolution", "label": "Resolution", "type": "int", "min": 8, "max": 60, "default": 30},
            {"name": "rot_x", "label": "Rotate X (deg)", "type": "float", "min": -180.0, "max": 180.0, "default": 25.0},
            {"name": "rot_y", "label": "Rotate Y (deg)", "type": "float", "min": -180.0, "max": 180.0, "default": 35.0},
            {"name": "rot_z", "label": "Rotate Z (deg)", "type": "float", "min": -180.0, "max": 180.0, "default": 0.0},
            {"name": "focal", "label": "Focal Length", "type": "int", "min": 100, "max": 1000, "default": 400},
        ]

    def generate(self, width: float, height: float, params: Dict, margin: float = 40) -> List[DrawCommand]:
        surface = params.get("surface", 0)
        res = params.get("resolution", 30)
        rx = math.radians(params.get("rot_x", 25.0))
        ry = math.radians(params.get("rot_y", 35.0))
        rz = math.radians(params.get("rot_z", 0.0))
        focal = params.get("focal", 400)

        cx, cy = width / 2, height / 2
        scale = min(width, height) * 0.3

        # Generate surface vertices
        if surface == 0:
            verts, edges = self._torus(res, scale)
        elif surface == 1:
            verts, edges = self._trefoil_knot(res, scale)
        elif surface == 2:
            verts, edges = self._sphere(res, scale)
        elif surface == 3:
            verts, edges = self._klein_bottle(res, scale)
        else:
            verts, edges = self._mobius(res, scale)

        # Rotate all vertices
        rotated = [rotate_xyz(v, rx, ry, rz) for v in verts]

        # Project and collect edges with depth
        commands = []
        edge_data = []

        for i1, i2, etype in edges:
            p1 = rotated[i1]
            p2 = rotated[i2]
            avg_z = (p1[2] + p2[2]) / 2

            s1, _ = project_perspective(p1, focal, cx, cy)
            s2, _ = project_perspective(p2, focal, cx, cy)
            edge_data.append((s1, s2, avg_z, etype))

        # Sort by depth (far first = painter's algorithm)
        edge_data.sort(key=lambda e: e[2])

        # Compute z range for depth-based coloring
        if edge_data:
            z_min = min(e[2] for e in edge_data)
            z_max = max(e[2] for e in edge_data)
        else:
            z_min = z_max = 0

        for s1, s2, z, etype in edge_data:
            # Map depth to color index: far=0, near=2
            if z_max > z_min:
                t = (z - z_min) / (z_max - z_min)
            else:
                t = 1.0
            color_idx = min(2, int(t * 3))
            commands.append(("line", (*s1, *s2), color_idx))

        return commands

    def _torus(self, res, scale):
        """Generate torus vertices and edges. R=major, r=minor radius."""
        R, r = 1.0, 0.4
        verts = []
        edges = []
        nu, nv = res, res

        for i in range(nu):
            u = 2 * math.pi * i / nu
            for j in range(nv):
                v = 2 * math.pi * j / nv
                x = (R + r * math.cos(v)) * math.cos(u) * scale
                y = (R + r * math.cos(v)) * math.sin(u) * scale
                z = r * math.sin(v) * scale
                verts.append((x, y, z))

        for i in range(nu):
            for j in range(nv):
                idx = i * nv + j
                right = i * nv + (j + 1) % nv
                down = ((i + 1) % nu) * nv + j
                edges.append((idx, right, 0))
                edges.append((idx, down, 1))

        return verts, edges

    def _trefoil_knot(self, res, scale):
        """Generate trefoil knot as a tube-like curve."""
        n = res * 4
        verts = []
        edges = []

        for i in range(n):
            t = 2 * math.pi * i / n
            x = (math.sin(t) + 2 * math.sin(2 * t)) * scale * 0.7
            y = (math.cos(t) - 2 * math.cos(2 * t)) * scale * 0.7
            z = -math.sin(3 * t) * scale * 0.7
            verts.append((x, y, z))

        for i in range(n):
            edges.append((i, (i + 1) % n, 0))

        return verts, edges

    def _sphere(self, res, scale):
        """Generate sphere vertices and edges."""
        verts = []
        edges = []
        nu, nv = res, res // 2

        for i in range(nu):
            u = 2 * math.pi * i / nu
            for j in range(nv + 1):
                v = math.pi * j / nv - math.pi / 2
                x = math.cos(v) * math.cos(u) * scale
                y = math.cos(v) * math.sin(u) * scale
                z = math.sin(v) * scale
                verts.append((x, y, z))

        for i in range(nu):
            for j in range(nv + 1):
                idx = i * (nv + 1) + j
                if j < nv:
                    right = i * (nv + 1) + j + 1
                    edges.append((idx, right, 0))
                down = ((i + 1) % nu) * (nv + 1) + j
                edges.append((idx, down, 1))

        return verts, edges

    def _klein_bottle(self, res, scale):
        """Generate Klein bottle (figure-8 immersion)."""
        verts = []
        edges = []
        nu, nv = res, res

        for i in range(nu):
            u = 2 * math.pi * i / nu
            for j in range(nv):
                v = 2 * math.pi * j / nv
                # Figure-8 Klein bottle parametrization
                r = 1.0
                x = (r + math.cos(u / 2) * math.sin(v) - math.sin(u / 2) * math.sin(2 * v)) * math.cos(u)
                y = (r + math.cos(u / 2) * math.sin(v) - math.sin(u / 2) * math.sin(2 * v)) * math.sin(u)
                z = math.sin(u / 2) * math.sin(v) + math.cos(u / 2) * math.sin(2 * v)
                verts.append((x * scale * 0.5, y * scale * 0.5, z * scale * 0.5))

        for i in range(nu):
            for j in range(nv):
                idx = i * nv + j
                right = i * nv + (j + 1) % nv
                down = ((i + 1) % nu) * nv + j
                edges.append((idx, right, 0))
                edges.append((idx, down, 1))

        return verts, edges

    def _mobius(self, res, scale):
        """Generate Möbius strip."""
        verts = []
        edges = []
        nu = res * 2
        nv = max(4, res // 4)

        for i in range(nu):
            u = 2 * math.pi * i / nu
            for j in range(nv):
                s = -0.5 + j / (nv - 1)  # -0.5 to 0.5
                x = (1 + s * 0.5 * math.cos(u / 2)) * math.cos(u) * scale * 0.7
                y = (1 + s * 0.5 * math.cos(u / 2)) * math.sin(u) * scale * 0.7
                z = s * 0.5 * math.sin(u / 2) * scale * 0.7
                verts.append((x, y, z))

        for i in range(nu):
            for j in range(nv):
                idx = i * nv + j
                if j < nv - 1:
                    right = i * nv + j + 1
                    edges.append((idx, right, 0))
                down = ((i + 1) % nu) * nv + j
                edges.append((idx, down, 1))

        return verts, edges
