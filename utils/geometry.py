"""Geometric utility functions for tile pattern calculations."""

import math
from typing import List, Tuple

Point = Tuple[float, float]
Line = Tuple[Point, Point]

PHI = (1 + math.sqrt(5)) / 2  # Golden ratio


def midpoint(p1: Point, p2: Point) -> Point:
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)


def lerp_point(p1: Point, p2: Point, t: float) -> Point:
    return (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1]))


def distance(p1: Point, p2: Point) -> float:
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def rotate_point(point: Point, center: Point, angle_rad: float) -> Point:
    dx = point[0] - center[0]
    dy = point[1] - center[1]
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    return (
        center[0] + dx * cos_a - dy * sin_a,
        center[1] + dx * sin_a + dy * cos_a,
    )


def polygon_vertices(center: Point, radius: float, n: int, start_angle: float = 0) -> List[Point]:
    """Generate vertices of a regular n-gon."""
    return [
        (
            center[0] + radius * math.cos(start_angle + 2 * math.pi * i / n),
            center[1] + radius * math.sin(start_angle + 2 * math.pi * i / n),
        )
        for i in range(n)
    ]


def subdivide_line(p1: Point, p2: Point, n: int) -> List[Point]:
    """Return n+1 points evenly spaced along line from p1 to p2."""
    return [lerp_point(p1, p2, i / n) for i in range(n + 1)]


def offset_polygon(vertices: List[Point], offset: float) -> List[Point]:
    """Inset/outset a polygon by offset distance (positive = inset)."""
    n = len(vertices)
    cx = sum(v[0] for v in vertices) / n
    cy = sum(v[1] for v in vertices) / n
    result = []
    for v in vertices:
        dx = v[0] - cx
        dy = v[1] - cy
        d = math.hypot(dx, dy)
        if d == 0:
            result.append(v)
        else:
            factor = (d - offset) / d
            result.append((cx + dx * factor, cy + dy * factor))
    return result


def line_intersection(p1: Point, p2: Point, p3: Point, p4: Point):
    """Find intersection of lines p1-p2 and p3-p4. Returns None if parallel."""
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-10:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
