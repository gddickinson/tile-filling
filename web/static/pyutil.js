// Helpers shared by the pattern ports: the command list, utils/geometry.py, rendering/projection.py,
// rendering/colors.py, and Python semantics JS lacks (round() half-to-even, %, complex ** 0.5).

// Drawing commands (patterns/base.py): ("line", (x1,y1,x2,y2), c), ("circle", (cx,cy,r), c), ("polygon", pts, c).
// Stored flat so that patterns with millions of segments stay small: kind[i] is 0 line / 1 circle / 2 polygon.
export class Commands {
  constructor() { this.kind = []; this.col = []; this.xy = []; }
  get length() { return this.kind.length; }
  line(x1, y1, x2, y2, c) { this.kind.push(0); this.col.push(c); this.xy.push(x1, y1, x2, y2); }
  circle(cx, cy, r, c) { this.kind.push(1); this.col.push(c); this.xy.push(cx, cy, r); }
  polygon(pts, c) { this.kind.push(2); this.col.push(c); this.xy.push(pts.length); for (const [x, y] of pts) this.xy.push(x, y); }
  // Visit every command: fn(kind, colorIndex, xy, offset, index). Polygons: xy[offset] = point count, then x, y pairs.
  forEach(fn) {
    let o = 0;
    for (let i = 0; i < this.kind.length; i++) {
      const k = this.kind[i];
      fn(k, this.col[i], this.xy, o, i);
      o += k === 0 ? 4 : k === 1 ? 3 : 1 + 2 * this.xy[o];
    }
  }
  // Python-shaped list [type, data, colorIndex] (tests and small exports only).
  toList() {
    const out = [];
    this.forEach((k, c, xy, o) => {
      if (k === 0) out.push(['line', xy.slice(o, o + 4), c]);
      else if (k === 1) out.push(['circle', xy.slice(o, o + 3), c]);
      else out.push(['polygon', Array.from({ length: xy[o] }, (_, j) => [xy[o + 1 + 2 * j], xy[o + 2 + 2 * j]]), c]);
    });
    return out;
  }
}

// --- Python semantics -----------------------------------------------------------------------------------------------
export const mod = (a, n) => ((a % n) + n) % n;           // Python a % n for n > 0
export const radians = d => d * Math.PI / 180;

// round(x, nd) for floats: exact decimal value, ties to even (toFixed rounds ties away from zero).
export function pyRound(x, nd) {
  if (!Number.isFinite(x)) return x;
  const full = Math.abs(x).toFixed(Math.min(100, nd + 60));
  const dot = full.indexOf('.');
  const tail = full.slice(dot + 1 + nd);
  if (/^50*$/.test(tail)) {                               // exact tie: round half to even
    const kept = full.slice(0, dot + 1 + nd).replace('.', '');
    let n = BigInt(kept);
    if (n % 2n === 1n) n += 1n;
    const v = Number(n) / 10 ** nd;
    return x < 0 ? -v : v;
  }
  return Number(x.toFixed(nd));
}

// Python's complex ** 0.5 (CPython c_pow): returns [re, im].
export function csqrt(re, im) {
  if (re === 0 && im === 0) return [0, 0];
  const len = Math.pow(Math.hypot(re, im), 0.5);
  const phase = Math.atan2(im, re) * 0.5;
  return [len * Math.cos(phase), len * Math.sin(phase)];
}

// --- utils/geometry.py ------------------------------------------------------------------------------------------------
export const PHI = (1 + Math.sqrt(5)) / 2;
export const midpoint = (p1, p2) => [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2];
export const lerpPoint = (p1, p2, t) => [p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1])];
export function polygonVertices(center, radius, n, startAngle = 0) {
  const out = [];
  for (let i = 0; i < n; i++) {
    out.push([center[0] + radius * Math.cos(startAngle + 2 * Math.PI * i / n),
      center[1] + radius * Math.sin(startAngle + 2 * Math.PI * i / n)]);
  }
  return out;
}

// --- rendering/projection.py ------------------------------------------------------------------------------------------
export function rotateXYZ(p, rx, ry, rz) {
  let [x, y, z] = p, c = Math.cos(rx), s = Math.sin(rx);
  [y, z] = [y * c - z * s, y * s + z * c];
  c = Math.cos(ry); s = Math.sin(ry);
  [x, z] = [x * c + z * s, -x * s + z * c];
  c = Math.cos(rz); s = Math.sin(rz);
  [x, y] = [x * c - y * s, x * s + y * c];
  return [x, y, z];
}
export function projectPerspective(p, focal, cx, cy) {
  const [x, y, z] = p;
  let zs = z + focal * 2;
  if (zs <= 0.1) zs = 0.1;
  const f = focal / zs;
  return [[cx + x * f, cy - y * f], f];
}
export function projectIsometric(p, cx, cy, scale = 1.0) {
  const [x, y, z] = p;
  return [[(x - z) * 0.866 * scale + cx, -y * scale + (x + z) * 0.5 * scale + cy], x + z];
}

// --- rendering/colors.py ----------------------------------------------------------------------------------------------
export const hexToRgb = h => { h = h.replace(/^#/, ''); return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16)); };
export const rgbToHex = (r, g, b) => '#' + [r, g, b].map(v => v.toString(16).padStart(2, '0')).join('');
export function lerpColor(c1, c2, t) {
  const [r1, g1, b1] = hexToRgb(c1), [r2, g2, b2] = hexToRgb(c2);
  return rgbToHex(Math.trunc(r1 + t * (r2 - r1)), Math.trunc(g1 + t * (g2 - g1)), Math.trunc(b1 + t * (b2 - b1)));
}
export const getLineColor = (palette, index) => palette.lines[mod(index, palette.lines.length)];
export function gradientColor(palette, t) {
  const colors = palette.lines;
  if (colors.length === 1) return colors[0];
  const segment = t * (colors.length - 1);
  const i = Math.trunc(segment);
  if (i >= colors.length - 1) return colors[colors.length - 1];
  return lerpColor(colors[i], colors[i + 1], segment - i);
}
