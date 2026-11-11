// Pattern engine: the 22 generators of patterns/PATTERN_REGISTRY ported to JS, keyed by the Python display names.
// Parameter specs, descriptions and palettes are NOT duplicated here: the pages load them from the Python code via
// the API (/api/patterns, /api/palettes); the node test checks this registry against the same Python lists.
import { decoratedGrid, grid, islamicStar, penrose } from './pat_tilings.js';
import { hexagonal, sierpinski, truchet, voronoi } from './pat_tilings2.js';
import { attractors, moire, spaceFilling, spirograph } from './pat_curves.js';
import { guilloche, lissajous, lsystem, phyllotaxis } from './pat_curves2.js';
import { isoCubes, wireframe } from './pat_3d.js';
import { apollonian, chladni, flowField, reactionDiffusion } from './pat_fields.js';
import { random } from './pyrandom.js';

export const GENERATORS = {
  'Grid': grid, 'Decorated Grid': decoratedGrid, 'Islamic Star': islamicStar, 'Penrose Tiling': penrose,
  'Truchet Tiles': truchet, 'Voronoi': voronoi, 'Hexagonal': hexagonal, 'Sierpinski': sierpinski,
  'Space-Filling Curves': spaceFilling, 'Moiré': moire, 'Spirograph': spirograph, 'Strange Attractors': attractors,
  'L-System': lsystem, 'Lissajous': lissajous, 'Guilloche': guilloche, 'Phyllotaxis': phyllotaxis,
  'Isometric Cubes': isoCubes, '3D Wireframe': wireframe,
  'Flow Field': flowField, 'Apollonian Gasket': apollonian, 'Chladni Figures': chladni, 'Reaction-Diffusion': reactionDiffusion,
};

export const MARGIN = 40;

// Equivalent of PATTERN_REGISTRY[name]().generate(width, height, params) -> Commands.
export function generate(name, width, height, params, margin = MARGIN) {
  const fn = GENERATORS[name];
  if (!fn) throw new Error(`unknown pattern ${name}`);
  return fn(width, height, params, margin);
}

// Default parameter values from a Python get_params() spec list.
export const defaults = spec => Object.fromEntries(spec.map(p => [p.name, p.default]));

// Randomize, as TileFillingApp._randomize / _batch_export: int randint(min, max), float uniform, bool choice.
export function randomParams(spec) {
  const out = {};
  for (const p of spec) {
    if (p.type === 'int') out[p.name] = random.randint(p.min, p.max);
    else if (p.type === 'float') out[p.name] = p.min + random.random() * (p.max - p.min);
    else if (p.type === 'bool') out[p.name] = random.choice([true, false]);
  }
  return out;
}

// Summary numbers used by the cross-check page and the node test (web/catalog.py computes the same in Python).
export function stats(cmds) {
  let lines = 0, circles = 0, polygons = 0, sum = 0, weights = 0, fills = 0;
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  const colors = {};
  const pt = (x, y) => { if (x < minX) minX = x; if (x > maxX) maxX = x; if (y < minY) minY = y; if (y > maxY) maxY = y; };
  cmds.forEach((k, c, xy, o, i) => {
    colors[c] = (colors[c] || 0) + 1;
    const e = cmds.ex[i];
    if (!Number.isNaN(e) && e !== undefined) { if (k === 2) fills += e === 1 ? 1 : 0; else weights += e; }
    if (k === 0) { lines++; sum += xy[o] + xy[o + 1] + xy[o + 2] + xy[o + 3]; pt(xy[o], xy[o + 1]); pt(xy[o + 2], xy[o + 3]); }
    else if (k === 1) { circles++; sum += xy[o] + xy[o + 1] + xy[o + 2]; pt(xy[o] - xy[o + 2], xy[o + 1] - xy[o + 2]); pt(xy[o] + xy[o + 2], xy[o + 1] + xy[o + 2]); }
    else { polygons++; for (let j = 0; j < xy[o]; j++) { sum += xy[o + 1 + 2 * j] + xy[o + 2 + 2 * j]; pt(xy[o + 1 + 2 * j], xy[o + 2 + 2 * j]); } }
  });
  const n = cmds.length;
  return { count: n, lines, circles, polygons, sum, bbox: n ? [minX, minY, maxX, maxY] : null, colors, weights, fills };
}
