"""Tile pattern generators for artistic visualization."""

from patterns.base import BasePattern
from patterns.grid import GridPattern, DecoratedGridPattern
from patterns.islamic import IslamicStarPattern
from patterns.penrose import PenrosePattern
from patterns.truchet import TruchetPattern
from patterns.voronoi import VoronoiPattern
from patterns.hexagonal import HexagonalPattern
from patterns.sierpinski import SierpinskiPattern

PATTERN_REGISTRY = {
    "Grid": GridPattern,
    "Decorated Grid": DecoratedGridPattern,
    "Islamic Star": IslamicStarPattern,
    "Penrose Tiling": PenrosePattern,
    "Truchet Tiles": TruchetPattern,
    "Voronoi": VoronoiPattern,
    "Hexagonal": HexagonalPattern,
    "Sierpinski": SierpinskiPattern,
}
