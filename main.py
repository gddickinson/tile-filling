#!/usr/bin/env python3
"""Tile Filling Visualizer - An artistic tile pattern generator with GUI."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import TileFillingApp


def main():
    app = TileFillingApp()
    app.run()


if __name__ == "__main__":
    main()
