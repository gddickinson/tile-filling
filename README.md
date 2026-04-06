# Tile Filling Visualizer

A Python GUI application for generating stunning mathematical and geometric art. 17 pattern types, 12 color palettes, 3D wireframe surfaces, post-processing effects, and real-time parameter control.

## Gallery

### Classic Tilings

**Decorated Grid** — Grid cells with layered geometric decorations: diagonals, diamonds, radial lines.

![Decorated Grid](samples/decorated_grid.png)

**Truchet Tiles (Cyberpunk)** — Randomly oriented quarter-circle arcs create emergent flowing curves.

![Truchet Cyberpunk](samples/truchet_cyberpunk.png)

**Islamic Star (Gold)** — Eight-pointed interlocking stars with geometric connections.

![Islamic Star](samples/islamic_gold.png)

**Penrose Tiling (Ocean)** — Aperiodic golden-ratio tiling that never repeats.

![Penrose Ocean](samples/penrose_ocean.png)

**Hexagonal (Sunset)** — Honeycomb grid with star decorations.

![Hexagonal Sunset](samples/hexagonal_sunset.png)

**Sierpinski (Neon)** — Fractal triangle subdivision, self-similar at every scale.

![Sierpinski Neon](samples/sierpinski_neon.png)

**Voronoi (Arctic)** — Organic cell tessellation with Lloyd relaxation.

![Voronoi Arctic](samples/voronoi_arctic.png)

**Truchet Multi-Arc (Fire)** — Concentric arc variant for denser, richer patterns.

![Truchet Fire](samples/truchet_fire.png)

### Mathematical Curves

**Hilbert Space-Filling Curve (Cyberpunk)** — A single continuous path that fills a 2D region. Gradient coloring reveals the curve's traversal order.

![Hilbert Curve](samples/hilbert_cyberpunk.png)

**Spirograph (Neon)** — Overlaid hypotrochoid curves from rolling-circle geometry.

![Spirograph](samples/spirograph_neon.png)

**L-System Plant (Forest)** — Fractal branching tree from recursive string rewriting.

![L-System Plant](samples/lsystem_plant.png)

**L-System Koch Snowflake (Ocean)** — Classic fractal coastline curve.

![Koch Snowflake](samples/lsystem_koch.png)

**Clifford Attractor (Sunset)** — Chaotic trajectory from a simple nonlinear dynamical system.

![Clifford Attractor](samples/clifford_sunset.png)

**De Jong Attractor (Cyberpunk)** — Another chaotic system with butterfly-like structure.

![De Jong Attractor](samples/dejong_cyberpunk.png)

**Moire Interference (Cyberpunk)** — Overlapping concentric circles create emergent patterns.

![Moire](samples/moire_circles.png)

### 3D Patterns

**Wireframe Torus (Cyberpunk)** — Parametric 3D torus with perspective projection and depth-based coloring.

![Wireframe Torus](samples/wireframe_torus.png)

**Wireframe Klein Bottle (Ocean)** — The famous non-orientable surface rendered as a wireframe.

![Klein Bottle](samples/wireframe_klein.png)

**Trefoil Knot (Neon)** — 3D mathematical knot with gaussian bloom and vignette.

![Trefoil Knot](samples/trefoil_glow.png)

**Isometric Cubes (Pastel)** — 3D cube grid with wave-based height variation.

![Isometric Cubes](samples/iso_cubes.png)

### Advanced Patterns

**Chladni Figures (Gold)** — Nodal line patterns from vibrating plate wave equations.

![Chladni](samples/chladni_gold.png)

**Reaction-Diffusion (Arctic)** — Gray-Scott model organic Turing patterns as contour lines.

![Reaction-Diffusion](samples/reaction_diffusion.png)

### Post-Processing Effects

**Kaleidoscope + Gaussian Bloom** — Any pattern can be transformed with N-fold symmetry and bloom effects.

![Kaleidoscope](samples/kaleidoscope_truchet.png)

## Quick Start

```bash
pip install Pillow
python main.py
```

Requires Python 3 and tkinter (included with most Python installations).

## All 17 Pattern Types

| Category | Patterns |
|----------|----------|
| **Classic Tilings** | Grid, Decorated Grid, Islamic Star, Penrose, Truchet, Voronoi, Hexagonal, Sierpinski |
| **Mathematical Curves** | Space-Filling Curves (Hilbert/Peano/Gosper), Spirograph, L-System, Strange Attractors, Moire |
| **3D Patterns** | Isometric Cubes, 3D Wireframe (Torus/Klein/Trefoil/Sphere/Mobius) |
| **Advanced** | Chladni Figures, Reaction-Diffusion |

## 12 Color Palettes

Monochrome, Blueprint, Cyberpunk, Ocean, Sunset, Forest, Gold, Neon, Minimal White, Pastel, Fire, Arctic

## Rendering & Effects

- **Line rendering:** Adjustable width, glow effect, gradient coloring
- **Anti-aliasing:** 2x supersampled rendering
- **Post-processing:** Kaleidoscope symmetry (2-12 folds), Gaussian bloom, Vignette
- **3D rendering:** Perspective/isometric projection, depth-based coloring
- **Export:** Standard PNG and hi-res 4x PNG at 300 DPI

## Adding New Patterns

1. Create a file in `patterns/` with a class inheriting `BasePattern`
2. Implement `get_params()` (parameter slider definitions) and `generate()` (returns drawing commands)
3. Register it in `patterns/__init__.py` under `PATTERN_REGISTRY`
