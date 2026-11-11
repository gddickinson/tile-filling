// Classic tilings, part 1: line-by-line ports of patterns/grid.py, patterns/islamic.py and patterns/penrose.py.
// Each generator is (width, height, params, margin) -> Commands, like BasePattern.generate.
import { Commands, PHI, lerpPoint, mod, polygonVertices, pyRound, radians } from './pyutil.js';
import { random } from './pyrandom.js';

const get = (params, k, d) => (params[k] ?? d);

// --- grid.py: GridPattern -------------------------------------------------------------------------------------------
export function grid(width, height, params, margin = 40) {
  const cols = get(params, 'cols', 10), rows = get(params, 'rows', 10), jitter = get(params, 'jitter', 0.0);
  const weight = get(params, 'line_weight', 1.0);         // line-width multiplier for every grid line
  const out = new Commands();
  const w = width - 2 * margin, h = height - 2 * margin, cw = w / cols, ch = h / rows;
  for (let i = 0; i < cols + 1; i++) {   // jitter draws from the shared (unseeded) global generator, as in Python
    const x = margin + i * cw;
    const jx = jitter > 0 ? x + (random.random() - 0.5) * cw * jitter : x;
    out.line(jx, margin, jx, margin + h, 0, weight);
  }
  for (let j = 0; j < rows + 1; j++) {
    const y = margin + j * ch;
    const jy = jitter > 0 ? y + (random.random() - 0.5) * ch * jitter : y;
    out.line(margin, jy, margin + w, jy, 0, weight);
  }
  return out;
}

// --- grid.py: DecoratedGridPattern ---------------------------------------------------------------------------------
export function decoratedGrid(width, height, params, margin = 40) {
  const cols = get(params, 'cols', 8), rows = get(params, 'rows', 8), decoration = get(params, 'decoration', 3);
  const innerScale = get(params, 'inner_scale', 0.5), rotation = radians(get(params, 'rotation', 0));
  const out = new Commands();
  const w = width - 2 * margin, h = height - 2 * margin, cw = w / cols, ch = h / rows;
  for (let i = 0; i < cols + 1; i++) { const x = margin + i * cw; out.line(x, margin, x, margin + h, 0); }
  for (let j = 0; j < rows + 1; j++) { const y = margin + j * ch; out.line(margin, y, margin + w, y, 0); }
  for (let i = 0; i < cols; i++) {
    for (let j = 0; j < rows; j++) {
      decorateCell(out, margin + (i + 0.5) * cw, margin + (j + 0.5) * ch, cw, ch, decoration, innerScale, rotation);
    }
  }
  return out;
}

function decorateCell(out, cx, cy, cw, ch, level, s, rotation) {
  const hw = cw / 2, hh = ch / 2;
  const tl = [cx - hw, cy - hh], tr = [cx + hw, cy - hh], bl = [cx - hw, cy + hh], br = [cx + hw, cy + hh];
  const tm = [cx, cy - hh], bm = [cx, cy + hh], lm = [cx - hw, cy], rm = [cx + hw, cy], c = [cx, cy];
  const L = (a, b, k) => out.line(a[0], a[1], b[0], b[1], k);
  if (level >= 1) { L(tl, br, 1); L(tr, bl, 1); }
  if (level >= 2) { L(c, tm, 1); L(c, bm, 1); L(c, lm, 1); L(c, rm, 1); }
  if (level >= 3) {
    L(c, tl, 2); L(c, tr, 2); L(c, bl, 2); L(c, br, 2);
    L(tm, rm, 2); L(rm, bm, 2); L(bm, lm, 2); L(lm, tm, 2);
  }
  if (level >= 4) {
    const itl = [cx - hw * s, cy - hh * s], itr = [cx + hw * s, cy - hh * s];
    const ibl = [cx - hw * s, cy + hh * s], ibr = [cx + hw * s, cy + hh * s];
    L(itl, itr, 2); L(itr, ibr, 2); L(ibr, ibl, 2); L(ibl, itl, 2);
    L(itl, tl, 2); L(itr, tr, 2); L(ibl, bl, 2); L(ibr, br, 2);
  }
  if (level >= 5) {
    const r = Math.min(hw, hh) * 0.9;
    for (let k = 0; k < 16; k++) {
      const a = rotation + k * Math.PI / 8;
      out.line(cx, cy, cx + r * Math.cos(a), cy + r * Math.sin(a), 3);
    }
    out.circle(cx, cy, Math.min(hw, hh) * 0.08, 3);
  }
}

// --- islamic.py: IslamicStarPattern --------------------------------------------------------------------------------
export function islamicStar(width, height, params, margin = 40) {
  const gs = get(params, 'grid_size', 5), n = get(params, 'points', 8), inner = get(params, 'inner_ratio', 0.4);
  const interlace = get(params, 'interlace', 0.5), rosette = get(params, 'rosette', false);
  const out = new Commands();
  const w = width - 2 * margin, h = height - 2 * margin, cell = Math.min(w, h) / gs, radius = cell * 0.45;
  const ox = margin + (w - cell * gs) / 2, oy = margin + (h - cell * gs) / 2;
  for (let i = 0; i < gs; i++) {
    for (let j = 0; j < gs; j++) {
      const cx = ox + (i + 0.5) * cell, cy = oy + (j + 0.5) * cell;
      if (rosette) drawRosette(out, cx, cy, radius, n, inner);
      else drawStar(out, cx, cy, radius, n, inner, interlace);
    }
  }
  drawConnections(out, ox, oy, cell, gs, radius, n);
  return out;
}

function drawStar(out, cx, cy, radius, n, innerRatio, interlace) {
  const outer = polygonVertices([cx, cy], radius, n, -Math.PI / 2);
  const inner = polygonVertices([cx, cy], radius * innerRatio, n, -Math.PI / 2 + Math.PI / n);
  const all = [];
  for (let i = 0; i < n; i++) all.push(outer[i], inner[i]);
  for (let i = 0; i < all.length; i++) { const p = all[i], q = all[(i + 1) % all.length]; out.line(p[0], p[1], q[0], q[1], 0); }
  if (interlace > 0) {
    const skip = Math.max(2, Math.floor(n / 3));
    for (let i = 0; i < n; i++) { const p = outer[i], q = outer[(i + skip) % n]; out.line(p[0], p[1], q[0], q[1], 1); }
  }
  out.circle(cx, cy, radius * 0.04, 2);
}

function drawRosette(out, cx, cy, radius, n, innerRatio) {
  const outer = polygonVertices([cx, cy], radius, n, -Math.PI / 2);
  const inner = polygonVertices([cx, cy], radius * innerRatio, n, -Math.PI / 2 + Math.PI / n);
  const L = (a, b, k) => out.line(a[0], a[1], b[0], b[1], k);
  for (let i = 0; i < n; i++) L(outer[i], outer[(i + 1) % n], 0);
  for (let i = 0; i < n; i++) L(inner[i], inner[(i + 1) % n], 1);
  for (let i = 0; i < n; i++) { L(outer[i], inner[i], 2); L(outer[i], inner[mod(i - 1, n)], 2); }
  for (let i = 0; i < n; i++) L([cx, cy], outer[i], 2);
  out.circle(cx, cy, radius * 0.06, 2);
}

function closestPair(pts, other) {
  let best = null, bestD = Infinity;
  for (const p of pts) {
    for (const q of other) {
      const d = (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2;
      if (d < bestD) { bestD = d; best = [p, q]; }
    }
  }
  return best;
}

function drawConnections(out, ox, oy, cell, gs, radius, n) {
  const cache = [];
  for (let i = 0; i < gs; i++) {
    cache.push([]);
    for (let j = 0; j < gs; j++) cache[i].push(polygonVertices([ox + (i + 0.5) * cell, oy + (j + 0.5) * cell], radius, n, -Math.PI / 2));
  }
  for (let i = 0; i < gs; i++) {
    for (let j = 0; j < gs; j++) {
      const pts = cache[i][j];
      if (i + 1 < gs) { const b = closestPair(pts, cache[i + 1][j]); if (b) out.line(b[0][0], b[0][1], b[1][0], b[1][1], 0); }
      if (j + 1 < gs) { const b = closestPair(pts, cache[i][j + 1]); if (b) out.line(b[0][0], b[0][1], b[1][0], b[1][1], 0); }
    }
  }
}

// --- penrose.py: PenrosePattern (Robinson triangle subdivision) ----------------------------------------------------
const THIN = 0, THICK = 1;

export function penrose(width, height, params, margin = 40) {
  const subdivisions = get(params, 'subdivisions', 5), drawTri = get(params, 'draw_triangles', false);
  const drawRhombs = get(params, 'draw_rhombs', true), initial = get(params, 'initial_shape', 0);
  const out = new Commands();
  const cx = width / 2, cy = height / 2, size = Math.min(width, height) / 2 - margin;
  let tris = [];
  for (let i = 0; i < 10; i++) {
    const a1 = (2 * i - 1) * Math.PI / 10, a2 = (2 * i + 1) * Math.PI / 10;
    const b = [cx + size * Math.cos(a1), cy + size * Math.sin(a1)], c = [cx + size * Math.cos(a2), cy + size * Math.sin(a2)];
    const type = initial === 0 ? THICK : THIN;
    tris.push(i % 2 === 0 ? [type, [cx, cy], b, c] : [type, [cx, cy], c, b]);
  }
  for (let s = 0; s < subdivisions; s++) tris = subdivide(tris);
  const L = (a, b, k) => out.line(a[0], a[1], b[0], b[1], k);
  if (drawTri) {
    for (const [t, a, b, c] of tris) { const k = t === THICK ? 0 : 1; L(a, b, k); L(b, c, k); L(c, a, k); }
  }
  if (drawRhombs) {
    for (const [verts, t] of extractRhombs(tris)) {
      const k = t === THICK ? 0 : 1;
      for (let i = 0; i < 4; i++) L(verts[i], verts[(i + 1) % 4], k);
    }
  }
  return out;
}

function subdivide(tris) {
  const res = [];
  for (const [t, a, b, c] of tris) {
    if (t === THICK) {
      const p = lerpPoint(a, c, 1 / PHI), q = lerpPoint(b, a, 1 / PHI);
      res.push([THICK, q, p, b], [THICK, p, q, a], [THIN, p, c, b]);
    } else {
      const r = lerpPoint(a, b, 1 / PHI);
      res.push([THIN, r, c, a], [THICK, c, r, b]);
    }
  }
  return res;
}

function extractRhombs(tris) {
  const edgeMap = new Map(), used = new Set(), rhombs = [];
  tris.forEach(([t, a, b, c], idx) => {
    const key = `${t}|${pyRound((b[0] + c[0]) / 2, 4)}|${pyRound((b[1] + c[1]) / 2, 4)}`;
    if (edgeMap.has(key)) {
      const other = edgeMap.get(key);
      if (!used.has(other) && !used.has(idx)) {
        const a2 = tris[other][1];
        rhombs.push([[a, b, a2, c], t]);
        used.add(idx); used.add(other);
      }
    } else edgeMap.set(key, idx);
  });
  tris.forEach(([t, a, b, c], idx) => { if (!used.has(idx)) rhombs.push([[a, b, c, a], t]); });
  return rhombs;
}
