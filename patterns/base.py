"""Base class for all tile pattern generators."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

# Drawing command types
# ("line", (x1, y1, x2, y2), color_index)
# ("polygon", [(x1,y1), ...], color_index, fill)
# ("circle", (cx, cy, r), color_index)
DrawCommand = Tuple[str, Any, int]


class BasePattern(ABC):
    """Abstract base for tile pattern generators."""

    name: str = "Base"
    description: str = ""

    @staticmethod
    @abstractmethod
    def get_params() -> List[Dict]:
        """Return list of parameter definitions.

        Each dict has: name, label, type ('int'|'float'|'bool'), min, max, default
        """
        pass

    @abstractmethod
    def generate(self, width: float, height: float, params: Dict, margin: float = 40) -> List[DrawCommand]:
        """Generate drawing commands for the pattern.

        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels
            params: Dict of parameter values
            margin: Border margin in pixels

        Returns:
            List of DrawCommand tuples
        """
        pass
