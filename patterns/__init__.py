"""Tile pattern generators for artistic visualization."""

from patterns.base import BasePattern
from patterns.grid import GridPattern, DecoratedGridPattern
from patterns.islamic import IslamicStarPattern
from patterns.penrose import PenrosePattern
from patterns.truchet import TruchetPattern
from patterns.voronoi import VoronoiPattern
from patterns.hexagonal import HexagonalPattern
from patterns.sierpinski import SierpinskiPattern
from patterns.space_filling import SpaceFillingPattern
from patterns.moire import MoirePattern
from patterns.spirograph import SpirographPattern
from patterns.attractors import AttractorPattern
from patterns.lsystem import LSystemPattern
from patterns.iso_cubes import IsoCubesPattern
from patterns.wireframe3d import Wireframe3DPattern
from patterns.chladni import ChladniPattern
from patterns.reaction_diffusion import ReactionDiffusionPattern
from patterns.flow_field import FlowFieldPattern
from patterns.apollonian import ApollonianPattern
from patterns.lissajous import LissajousPattern
from patterns.guilloche import GuillochePattern
from patterns.phyllotaxis import PhyllotaxisPattern

PATTERN_REGISTRY = {
    # Classic tilings
    "Grid": GridPattern,
    "Decorated Grid": DecoratedGridPattern,
    "Islamic Star": IslamicStarPattern,
    "Penrose Tiling": PenrosePattern,
    "Truchet Tiles": TruchetPattern,
    "Voronoi": VoronoiPattern,
    "Hexagonal": HexagonalPattern,
    "Sierpinski": SierpinskiPattern,
    # Mathematical curves
    "Space-Filling Curves": SpaceFillingPattern,
    "Moiré": MoirePattern,
    "Spirograph": SpirographPattern,
    "Strange Attractors": AttractorPattern,
    "L-System": LSystemPattern,
    "Lissajous": LissajousPattern,
    "Guilloche": GuillochePattern,
    "Phyllotaxis": PhyllotaxisPattern,
    # 3D patterns
    "Isometric Cubes": IsoCubesPattern,
    "3D Wireframe": Wireframe3DPattern,
    # Advanced
    "Flow Field": FlowFieldPattern,
    "Apollonian Gasket": ApollonianPattern,
    "Chladni Figures": ChladniPattern,
    "Reaction-Diffusion": ReactionDiffusionPattern,
}
