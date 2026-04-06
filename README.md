# Tile Filling Visualizer

A Python GUI application for generating stunning mathematical and geometric art. 22 pattern types, 12 color palettes, 3D wireframe surfaces, 9 post-processing effects, and real-time parameter control with presets.

## Gallery

### Classic Tilings

**Decorated Grid** — Layered geometric decorations with chromatic aberration and bloom.

![Decorated Grid](samples/chromatic_grid.png)

**Truchet Tiles (Cyberpunk)** — Quarter-circle arcs with gradient coloring and glow.

![Truchet Cyberpunk](samples/truchet_cyberpunk.png)

**Islamic Star (Gold)** — Eight-pointed interlocking stars.

![Islamic Star](samples/islamic_gold.png)

**Penrose Tiling (Ocean)** — Aperiodic golden-ratio tiling.

![Penrose Ocean](samples/penrose_ocean.png)

**Hexagonal (Sunset)** — Honeycomb grid with star decorations.

![Hexagonal Sunset](samples/hexagonal_sunset.png)

**Sierpinski (Neon)** — Fractal triangle subdivision.

![Sierpinski Neon](samples/sierpinski_neon.png)

**Voronoi (Arctic)** — Organic cell tessellation.

![Voronoi Arctic](samples/voronoi_arctic.png)

### Mathematical Curves

**Hilbert Space-Filling Curve (Cyberpunk)** — A single path that fills 2D space.

![Hilbert Curve](samples/hilbert_cyberpunk.png)

**Spirograph (Neon)** — Overlaid hypotrochoid curves.

![Spirograph](samples/spirograph_neon.png)

**L-System Plant (Forest)** — Fractal branching tree.

![L-System Plant](samples/lsystem_plant.png)

**De Jong Attractor (Cyberpunk)** — Chaotic trajectory art.

![De Jong Attractor](samples/dejong_cyberpunk.png)

**Harmonograph (Cyberpunk)** — Damped pendulum simulation.

![Harmonograph](samples/harmonograph_cyberpunk.png)

**Phyllotaxis (Sunset)** — Fibonacci sunflower spiral with connected arcs.

![Phyllotaxis](samples/phyllotaxis_sunset.png)

**Guilloche (Gold)** — Fine-line engraving art with bloom.

![Guilloche](samples/guilloche_neon.png)

### Flow & Organic Patterns

**Flow Field (Ocean)** — Noise-driven particle traces.

![Flow Field](samples/flow_field_ocean.png)

**Flow Field with Scan Lines** — CRT-style retro effect.

![Flow Scanlines](samples/flow_scanlines.png)

**Apollonian Gasket (Gold)** — Recursive tangent circle packing.

![Apollonian](samples/apollonian_gold.png)

**Reaction-Diffusion (Arctic)** — Gray-Scott organic Turing patterns.

![Reaction-Diffusion](samples/reaction_diffusion.png)

### 3D Patterns

**Wireframe Torus (Cyberpunk)** — Perspective projection with depth coloring.

![Wireframe Torus](samples/wireframe_torus.png)

**Isometric Cubes (Pastel)** — 3D cube grid with wave height variation.

![Isometric Cubes](samples/iso_cubes.png)

**Trefoil Knot (Neon)** — 3D mathematical knot with bloom.

![Trefoil Knot](samples/trefoil_glow.png)

### Effects Showcase

**Kaleidoscope + Bloom** — Any pattern with N-fold symmetry.

![Kaleidoscope](samples/kaleidoscope_truchet.png)

**Chladni Figures (Gold)** — Wave equation nodal lines.

![Chladni](samples/chladni_gold.png)

## Quick Start

```bash
pip install Pillow
python main.py
```

Requires Python 3 and tkinter (included with most Python installations).

## All 22 Pattern Types

| Category | Patterns |
|----------|----------|
| **Classic Tilings** | Grid, Decorated Grid, Islamic Star, Penrose, Truchet, Voronoi, Hexagonal, Sierpinski |
| **Mathematical Curves** | Space-Filling (Hilbert/Peano/Gosper), Spirograph, L-System, Attractors, Lissajous, Guilloche, Phyllotaxis, Moire |
| **3D Patterns** | Isometric Cubes, 3D Wireframe (Torus/Klein/Trefoil/Sphere/Mobius) |
| **Advanced** | Flow Field, Apollonian Gasket, Chladni Figures, Reaction-Diffusion |

## 12 Color Palettes

Monochrome, Blueprint, Cyberpunk, Ocean, Sunset, Forest, Gold, Neon, Minimal White, Pastel, Fire, Arctic

## Rendering & Effects

- **Line rendering:** Adjustable width, glow, gradient coloring
- **Anti-aliasing:** 2x supersampled rendering
- **Post-processing:** Kaleidoscope (2-12 folds), Gaussian bloom, Vignette, Chromatic aberration, CRT scan lines, Film grain
- **3D rendering:** Perspective/isometric projection, depth-based coloring
- **Export:** Standard PNG, hi-res 4x PNG (300 DPI), batch random export (10 variations)

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Randomize all parameters |
| `R` | Regenerate current pattern |
| `E` | Export PNG |
| `S` | Save preset |
| `L` | Load preset |

## Presets

Save your favorite parameter combinations as JSON presets. Presets store the pattern type, all parameters, palette, and effect settings. Saved to the `presets/` folder.

## Adding New Patterns

1. Create a file in `patterns/` with a class inheriting `BasePattern`
2. Implement `get_params()` (parameter slider definitions) and `generate()` (returns drawing commands)
3. Register it in `patterns/__init__.py` under `PATTERN_REGISTRY`
