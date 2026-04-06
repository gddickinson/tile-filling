"""3D to 2D projection engine - isometric and perspective projection with rotation."""

import math
from typing import Tuple, List

Point3D = Tuple[float, float, float]
Point2D = Tuple[float, float]


def rotate_x(p: Point3D, angle: float) -> Point3D:
    """Rotate point around X axis."""
    x, y, z = p
    c, s = math.cos(angle), math.sin(angle)
    return (x, y * c - z * s, y * s + z * c)


def rotate_y(p: Point3D, angle: float) -> Point3D:
    """Rotate point around Y axis."""
    x, y, z = p
    c, s = math.cos(angle), math.sin(angle)
    return (x * c + z * s, y, -x * s + z * c)


def rotate_z(p: Point3D, angle: float) -> Point3D:
    """Rotate point around Z axis."""
    x, y, z = p
    c, s = math.cos(angle), math.sin(angle)
    return (x * c - y * s, x * s + y * c, z)


def rotate_xyz(p: Point3D, rx: float, ry: float, rz: float) -> Point3D:
    """Apply rotation around X, Y, Z axes in sequence."""
    p = rotate_x(p, rx)
    p = rotate_y(p, ry)
    p = rotate_z(p, rz)
    return p


def project_perspective(p: Point3D, focal: float, cx: float, cy: float) -> Tuple[Point2D, float]:
    """Perspective projection. Returns (screen_point, depth_factor).

    Camera at origin looking down +Z. focal controls FOV.
    """
    x, y, z = p
    # Shift z so objects are in front of camera
    z_shifted = z + focal * 2
    if z_shifted <= 0.1:
        z_shifted = 0.1
    factor = focal / z_shifted
    return ((cx + x * factor, cy - y * factor), factor)


def project_isometric(p: Point3D, cx: float, cy: float, scale: float = 1.0) -> Tuple[Point2D, float]:
    """Isometric projection. Returns (screen_point, depth)."""
    x, y, z = p
    # Standard isometric angles
    sx = (x - z) * 0.866 * scale + cx
    sy = -y * scale + (x + z) * 0.5 * scale + cy
    depth = x + z  # For depth sorting
    return ((sx, sy), depth)


def project_orthographic(p: Point3D, cx: float, cy: float, scale: float = 1.0) -> Tuple[Point2D, float]:
    """Orthographic projection (drop Z). Returns (screen_point, depth)."""
    x, y, z = p
    return ((cx + x * scale, cy - y * scale), z)


def depth_to_alpha(z: float, z_min: float, z_max: float) -> float:
    """Map depth to alpha (0.0 to 1.0). Closer = more opaque."""
    if z_max == z_min:
        return 1.0
    return 0.2 + 0.8 * (z - z_min) / (z_max - z_min)


def depth_to_width(z: float, z_min: float, z_max: float, min_w: float = 0.5, max_w: float = 3.0) -> float:
    """Map depth to line width. Closer = thicker."""
    if z_max == z_min:
        return max_w
    t = (z - z_min) / (z_max - z_min)
    return min_w + t * (max_w - min_w)
