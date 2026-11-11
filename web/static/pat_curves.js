// Mathematical curves, part 1: ports of patterns/space_filling.py, patterns/moire.py, patterns/spirograph.py and
// patterns/attractors.py.
import { Commands, radians } from './pyutil.js';

const get = (params, k, d) => (params[k] ?? d);

// Fit a point list into the margin box and draw consecutive segments (space_filling / attractors _scale_and_draw).
function fitBox(xs, ys, width, height, margin) {
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  for (const x of xs) { if (x < minX) minX = x; if (x > maxX) maxX = x; }
  for (const y of ys) { if (y < minY) minY = y; if (y > maxY) maxY = y; }
  const rx = (maxX - minX) || 1, ry = (maxY - minY) || 1;
  const w = width - 2 * margin, h = height - 2 * margin, scale = Math.min(w / rx, h / ry);
  return { minX, minY, scale, ox: margin + (w - rx * scale) / 2, oy: margin + (h - ry * scale) / 2 };
}

// L-system rewrite with the size guard used in space_filling.py / lsystem.py (stop once the string exceeds `limit`).
export function rewrite(axiom, rules, depth, limit) {
  let state = axiom;
  for (let d = 0; d < depth; d++) {
    const parts = [];
    for (const c of state) parts.push(rules[c] ?? c);
    state = parts.join('');
    if (state.length > limit) break;
  }
  return state;
}

// --- space_filling.py -------------------------------------------------------------------------------------------------
export function spaceFilling(width, height, params, margin = 40) {
  const type = get(params, 'curve_type', 0), depth = get(params, 'depth', 5);
  const rounded = get(params, 'rounded', 0.0), connect = get(params, 'connect', true);
  let xs, ys;
  if (type === 0) [xs, ys] = hilbert(depth);
  else if (type === 1) [xs, ys] = turtle(rewrite('X', { X: 'XFYFX+F+YFXFY-F-XFYFX', Y: 'YFXFY-F-XFYFX+F+YFXFY' }, depth, 500000), 90, 'F');
  else [xs, ys] = turtle(rewrite('A', { A: 'A-B--B+A++AA+B-', B: '+A-BB--B-A++A+B' }, depth, 500000), 60, 'AB');
  const out = new Commands();
  if (xs.length < 2) return out;
  const { minX, minY, scale, ox, oy } = fitBox(xs, ys, width, height, margin);
  const total = xs.length, n = total - 1;
  const P = i => [ox + (xs[i] - minX) * scale, oy + (ys[i] - minY) * scale];
  const lerp = (p, q, t) => [p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])];
  if (!connect) {                                          // each segment on its own, shortened at both ends
    const gap = Math.max(rounded, GAP);
    for (let i = 0; i < n; i++) {
      const a = lerp(P(i), P(i + 1), gap), b = lerp(P(i), P(i + 1), 1 - gap);
      out.line(a[0], a[1], b[0], b[1], Math.floor((i * 3) / total));
    }
  } else if (rounded > 0 && n > 1) {                       // corners cut and joined by quadratic Bezier curves
    let start = P(0);
    for (let i = 0; i < n; i++) {
      const p1 = P(i), p2 = P(i + 1), c = Math.floor((i * 3) / total);
      const end = i < n - 1 ? lerp(p1, p2, 1 - rounded) : p2;
      if (end[0] !== start[0] || end[1] !== start[1]) out.line(start[0], start[1], end[0], end[1], c);
      if (i < n - 1) {
        const q = lerp(p2, P(i + 2), rounded);
        let prev = end;
        for (let k = 1; k <= CURVE_PIECES; k++) {
          const t = k / CURVE_PIECES, u = 1 - t;
          const pt = [u * u * end[0] + 2 * u * t * p2[0] + t * t * q[0], u * u * end[1] + 2 * u * t * p2[1] + t * t * q[1]];
          out.line(prev[0], prev[1], pt[0], pt[1], c);
          prev = pt;
        }
        start = q;
      }
    }
  } else {
    let [px, py] = P(0);
    for (let i = 0; i < n; i++) {
      const [nx, ny] = P(i + 1);
      out.line(px, py, nx, ny, Math.floor((i * 3) / total));
      px = nx; py = ny;
    }
  }
  return out;
}
const GAP = 0.15, CURVE_PIECES = 3;                        // as space_filling.py

function hilbert(depth) {
  const n = 2 ** depth, xs = [], ys = [];
  for (let d0 = 0; d0 < n * n; d0++) {
    let x = 0, y = 0, d = d0;
    for (let s = 1; s < n; s *= 2) {
      const rx = d & 2 ? 1 : 0, ry = (d & 1) ^ rx;
      if (ry === 0) {
        if (rx === 1) { x = s - 1 - x; y = s - 1 - y; }
        [x, y] = [y, x];
      }
      x += s * rx; y += s * ry; d >>= 2;
    }
    xs.push(x); ys.push(y);
  }
  return [xs, ys];
}

function turtle(cmds, angleDeg, drawChars) {
  let x = 0.0, y = 0.0, heading = 0.0;
  const a = radians(angleDeg), xs = [x], ys = [y];
  for (const c of cmds) {
    if (drawChars.includes(c)) { x += Math.cos(heading); y += Math.sin(heading); xs.push(x); ys.push(y); }
    else if (c === '+') heading += a;
    else if (c === '-') heading -= a;
  }
  return [xs, ys];
}

// --- moire.py ------------------------------------------------------------------------------------------------------
export function moire(width, height, params, margin = 40) {
  const style = get(params, 'style', 1), count = get(params, 'count', 60), angleOff = get(params, 'angle_offset', 5.0);
  const centerOff = get(params, 'center_offset', 0.1), layers = get(params, 'layers', 2);
  const out = new Commands();
  const cx = width / 2, cy = height / 2, size = Math.min(width, height) / 2 - margin;
  for (let layer = 0; layer < layers; layer++) {
    const rot = radians(angleOff * layer);
    const lcx = cx + size * centerOff * Math.cos(layer * Math.PI / layers);
    const lcy = cy + size * centerOff * Math.sin(layer * Math.PI / layers);
    if (style === 0) {
      const spacing = size * 2 / count, c = Math.cos(rot), s = Math.sin(rot);
      const clX = v => Math.max(margin, Math.min(width - margin, v)), clY = v => Math.max(margin, Math.min(height - margin, v));
      for (let i = 0; i < count + 1; i++) {
        const off = -size + i * spacing, px = lcx + off * c, py = lcy + off * s, dx = -s * size * 1.5, dy = c * size * 1.5;
        out.line(clX(px - dx), clY(py - dy), clX(px + dx), clY(py + dy), layer);
      }
    } else if (style === 1) {
      const spacing = size / count, segs = 60;
      for (let i = 1; i < count + 1; i++) {
        const r = i * spacing;
        for (let j = 0; j < segs; j++) {
          const a1 = 2 * Math.PI * j / segs, a2 = 2 * Math.PI * (j + 1) / segs;
          out.line(lcx + r * Math.cos(a1), lcy + r * Math.sin(a1), lcx + r * Math.cos(a2), lcy + r * Math.sin(a2), layer);
        }
      }
    } else {
      for (let i = 0; i < count; i++) {
        const a = rot + 2 * Math.PI * i / count;
        out.line(lcx, lcy, lcx + size * Math.cos(a), lcy + size * Math.sin(a), layer);
      }
    }
  }
  return out;
}

// --- spirograph.py -----------------------------------------------------------------------------------------------------
const gcd = (a, b) => { a = Math.abs(a); b = Math.abs(b); while (b) [a, b] = [b, a % b]; return a; };

export function spirograph(width, height, params, margin = 40) {
  const R = get(params, 'R', 60), r = get(params, 'r', 37), d = get(params, 'd', 45.0), mode = get(params, 'mode', 0);
  const multi = get(params, 'multi', 1), res = get(params, 'resolution', 5000);
  const out = new Commands();
  const cx = width / 2, cy = height / 2, size = Math.min(width, height) / 2 - margin;
  for (let layer = 0; layer < multi; layer++) {
    const lr = r + layer * 2, ld = d + layer * 3;
    if (mode === 0 || mode === 2) addCurve(out, trochoid(R, lr, ld, res, -1), cx, cy, size, layer * 2, 1);
    if (mode === 1 || mode === 2) addCurve(out, trochoid(R, lr, ld, res, 1), cx, cy, size, layer * 2 + 1, 1);
  }
  return out;
}

// sign -1: hypotrochoid, +1: epitrochoid (rotations = r // gcd(R, r)).
function trochoid(R, r, d, n, sign) {
  if (r === 0) return [];
  const tMax = 2 * Math.PI * Math.floor(r / gcd(R, r)), pts = [];
  for (let i = 0; i < n + 1; i++) {
    const t = tMax * i / n;
    if (sign < 0) pts.push([(R - r) * Math.cos(t) + d * Math.cos((R - r) * t / r), (R - r) * Math.sin(t) - d * Math.sin((R - r) * t / r)]);
    else pts.push([(R + r) * Math.cos(t) - d * Math.cos((R + r) * t / r), (R + r) * Math.sin(t) - d * Math.sin((R + r) * t / r)]);
  }
  return pts;
}

// Centre a curve, scaled so its largest |x| or |y| reaches `size * k` (spirograph k=1, lissajous k=0.95).
export function addCurve(out, pts, cx, cy, size, c, k) {
  if (pts.length < 2) return;
  let mx = 0, my = 0;
  for (const p of pts) { if (Math.abs(p[0]) > mx) mx = Math.abs(p[0]); if (Math.abs(p[1]) > my) my = Math.abs(p[1]); }
  const scale = k === 1 ? size / (Math.max(mx, my) || 1) : size / (Math.max(mx, my) || 1) * k;
  for (let i = 0; i < pts.length - 1; i++) {
    out.line(cx + pts[i][0] * scale, cy + pts[i][1] * scale, cx + pts[i + 1][0] * scale, cy + pts[i + 1][1] * scale, c);
  }
}

// --- attractors.py ---------------------------------------------------------------------------------------------------------
export function attractors(width, height, params, margin = 40) {
  const type = get(params, 'attractor', 0), a = get(params, 'a', -1.4), b = get(params, 'b', 1.6);
  const c = get(params, 'c', 1.0), d = get(params, 'd', 0.7), n = get(params, 'iterations', 80) * 1000;
  const skip = get(params, 'skip_lines', 1);
  const [xs, ys] = attractorOrbit(type, a, b, c, d, n);
  const out = new Commands();
  if (n < 2) return out;
  const f = fitBox(xs, ys, width, height, margin);
  for (let i = 0; i < n - skip; i += skip) {
    out.line(f.ox + (xs[i] - f.minX) * f.scale, f.oy + (ys[i] - f.minY) * f.scale,
      f.ox + (xs[i + skip] - f.minX) * f.scale, f.oy + (ys[i + skip] - f.minY) * f.scale, Math.floor((i * 4) / n));
  }
  return out;
}

// The raw orbit of attractors._clifford / _dejong / _lorenz (Lorenz projected to the x-z plane).
export function attractorOrbit(type, a, b, c, d, n) {
  const xs = new Float64Array(n), ys = new Float64Array(n);
  let x = 0.1, y = type === 2 ? 0.0 : 0.1, z = 0.0;
  for (let i = 0; i < n; i++) {
    if (type === 0) { const nx = Math.sin(a * y) + c * Math.cos(a * x); y = Math.sin(b * x) + d * Math.cos(b * y); x = nx; }
    else if (type === 1) { const nx = Math.sin(a * y) - Math.cos(b * x); y = Math.sin(c * x) - Math.cos(d * y); x = nx; }
    else {                                                  // Lorenz, sigma 10, rho 28, beta 8/3, dt 0.002
      const dx = 10.0 * (y - x), dy = x * (28.0 - z) - y, dz = x * y - (8.0 / 3.0) * z;
      x += dx * 0.002; y += dy * 0.002; z += dz * 0.002;
    }
    xs[i] = x; ys[i] = type === 2 ? z : y;
  }
  return [xs, ys];
}
