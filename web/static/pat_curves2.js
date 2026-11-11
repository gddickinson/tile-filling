// Mathematical curves, part 2: ports of patterns/lsystem.py, patterns/lissajous.py, patterns/guilloche.py and
// patterns/phyllotaxis.py.
import { Commands, radians } from './pyutil.js';
import { addCurve, rewrite } from './pat_curves.js';

const get = (params, k, d) => (params[k] ?? d);

// lsystem.PRESETS (the node test checks this copy against the Python list).
export const LSYSTEM_PRESETS = [
  { name: 'Koch Snowflake', axiom: 'F++F++F', rules: { F: 'F-F++F-F' }, angle: 60, draw: 'F' },
  { name: 'Dragon Curve', axiom: 'FX', rules: { X: 'X+YF+', Y: '-FX-Y' }, angle: 90, draw: 'F' },
  { name: 'Sierpinski Arrow', axiom: 'A', rules: { A: 'B-A-B', B: 'A+B+A' }, angle: 60, draw: 'AB' },
  { name: 'Plant Fractal', axiom: 'X', rules: { X: 'F+[[X]-X]-F[-FX]+X', F: 'FF' }, angle: 25, draw: 'F' },
  { name: 'Pentigree', axiom: 'F-F-F-F-F', rules: { F: 'F-F++F+F-F-F' }, angle: 72, draw: 'F' },
  { name: 'Crystal', axiom: 'F+F+F+F', rules: { F: 'FF+F++F+F' }, angle: 90, draw: 'F' },
  {
    name: 'Quadratic Gosper', axiom: '-YF', angle: 90, draw: 'F', rules: {
      X: 'XFX-YF-YF+FX+FX-YF-YFFX+YF+FXFXYF-FX+YF+FXFX+YF-FXYF-YF-FX+FX+YFYF-',
      Y: '+FXFX-YF-YF+FX+FXYF+FX-YFYF-FX-YF+FXYFYF-FX-YFFX+FX+YF-YF-FX+FX+YFY',
    },
  },
];

// --- lsystem.py ------------------------------------------------------------------------------------------------------
export function lsystem(width, height, params, margin = 40) {
  const idx = get(params, 'preset', 0), iterations = get(params, 'iterations', 4);
  const adj = get(params, 'angle_adjust', 0.0), start = get(params, 'start_angle', 0.0);
  const p = LSYSTEM_PRESETS[idx % LSYSTEM_PRESETS.length];
  const state = rewrite(p.axiom, p.rules, iterations, 1000000);
  // turtle with a stack; segments kept as flat [x1, y1, x2, y2, ...]
  let x = 0.0, y = 0.0, heading = radians(start);
  const a = radians(p.angle + adj), stack = [], seg = [];
  for (const c of state) {
    if (p.draw.includes(c)) {
      const nx = x + Math.cos(heading), ny = y + Math.sin(heading);
      seg.push(x, y, nx, ny); x = nx; y = ny;
    } else if (c === 'f') { x += Math.cos(heading); y += Math.sin(heading); }
    else if (c === '+') heading += a;
    else if (c === '-') heading -= a;
    else if (c === '[') stack.push([x, y, heading]);
    else if (c === ']') { if (stack.length) [x, y, heading] = stack.pop(); }
  }
  const out = new Commands();
  if (!seg.length) return out;
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  for (let i = 0; i < seg.length; i += 2) {
    const sx = seg[i], sy = seg[i + 1];
    if (sx < minX) minX = sx; if (sx > maxX) maxX = sx; if (sy < minY) minY = sy; if (sy > maxY) maxY = sy;
  }
  const rx = (maxX - minX) || 1, ry = (maxY - minY) || 1, w = width - 2 * margin, h = height - 2 * margin;
  const scale = Math.min(w / rx, h / ry), ox = margin + (w - rx * scale) / 2, oy = margin + (h - ry * scale) / 2;
  const total = seg.length / 4;
  for (let i = 0; i < total; i++) {
    const o = 4 * i;
    out.line(ox + (seg[o] - minX) * scale, oy + (seg[o + 1] - minY) * scale, ox + (seg[o + 2] - minX) * scale,
      oy + (seg[o + 3] - minY) * scale, Math.floor((i * 3) / total));
  }
  return out;
}

// --- lissajous.py ----------------------------------------------------------------------------------------------------
export function lissajous(width, height, params, margin = 40) {
  const fx = get(params, 'freq_x', 3), fy = get(params, 'freq_y', 4), phase = radians(get(params, 'phase', 90.0));
  const damping = get(params, 'damping', 0.0), layers = get(params, 'layers', 1), n = get(params, 'resolution', 4000);
  const harmonograph = get(params, 'harmonograph', false);
  const out = new Commands();
  const cx = width / 2, cy = height / 2, size = Math.min(width, height) / 2 - margin;
  for (let layer = 0; layer < layers; layer++) {
    const lp = phase + layer * Math.PI / (layers * 2), lfx = fx + layer * 0.1, lfy = fy + layer * 0.1;
    const pts = [];
    if (harmonograph) {
      const tMax = 2 * Math.PI * 40, d1 = damping > 0 ? damping : 0.003, d2 = d1 * 1.1;
      const f2x = lfx + 0.01, f2y = lfy + 0.01, p2 = lp * 0.7;
      for (let i = 0; i < n + 1; i++) {
        const t = tMax * i / n;
        pts.push([Math.sin(lfx * t + lp) * Math.exp(-d1 * t) + Math.sin(f2x * t + p2) * Math.exp(-d2 * t),
          Math.sin(lfy * t + lp * 0.5) * Math.exp(-d1 * t) + Math.sin(f2y * t + p2 * 0.3) * Math.exp(-d2 * t)]);
      }
    } else {
      const tMax = 2 * Math.PI * Math.max(10, Math.trunc(lfx * lfy));
      for (let i = 0; i < n + 1; i++) {
        const t = tMax * i / n, decay = Math.exp(-damping * t);
        pts.push([Math.sin(lfx * t + lp) * decay, Math.sin(lfy * t) * decay]);
      }
    }
    addCurve(out, pts, cx, cy, size, layer, 0.95);
  }
  return out;
}

// --- guilloche.py ------------------------------------------------------------------------------------------------------
export function guilloche(width, height, params, margin = 40) {
  const nWaves = get(params, 'waves', 80), amp = get(params, 'amplitude', 30.0), freq = get(params, 'freq', 6.0);
  const shape = get(params, 'shape', 0), modulation = get(params, 'modulation', 0.3), res = get(params, 'resolution', 400);
  const out = new Commands();
  const cx = width / 2, cy = height / 2, w = width - 2 * margin, h = height - 2 * margin;
  for (let wave = 0; wave < nWaves; wave++) {
    const tOff = wave / nWaves, baseR = 0.2 + 0.7 * wave / nWaves, c = Math.floor((wave * 3) / nWaves);
    let px0 = 0, py0 = 0;
    for (let i = 0; i < res + 1; i++) {
      const t = 2 * Math.PI * i / res;
      let bx, by;
      if (shape === 0) { bx = Math.cos(t); by = Math.sin(t); }
      else if (shape === 1) { bx = Math.cos(t); by = Math.sin(t) * 0.6; }
      else if (shape === 2) { bx = Math.cos(t) * (1.0 + 0.3 * Math.cos(2 * t)); by = Math.sin(t) * (0.6 + 0.2 * Math.cos(2 * t)); }
      else { const rr = Math.cos(3 * t); bx = rr * Math.cos(t); by = rr * Math.sin(t); }
      const waveVal = Math.sin(freq * t + tOff * 2 * Math.PI);
      const m = 1.0 + modulation * Math.sin(3 * t + wave * 0.1);
      const offset = amp * waveVal * m * (1.0 / nWaves);
      let nx = -by, ny = bx;
      const norm = Math.hypot(nx, ny) || 1;
      nx /= norm; ny /= norm;
      const r = baseR * Math.min(w, h) / 2;
      const px = cx + bx * r + nx * offset, py = cy + by * r + ny * offset;
      if (i > 0) out.line(px0, py0, px, py, c);
      px0 = px; py0 = py;
    }
  }
  return out;
}

// --- phyllotaxis.py ----------------------------------------------------------------------------------------------------
const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));

export function phyllotaxis(width, height, params, margin = 40) {
  const n = get(params, 'points', 500), style = get(params, 'style', 2), mult = get(params, 'angle_mult', 1.0);
  const pow = get(params, 'scale_power', 0.5), dot = get(params, 'dot_size', 3.0);
  const out = new Commands();
  const cx = width / 2, cy = height / 2, maxR = Math.min(width, height) / 2 - margin, pts = [];
  for (let i = 0; i < n; i++) {
    const a = i * GOLDEN_ANGLE * mult, r = maxR * (i / n) ** pow;
    pts.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]);
  }
  const L = (p, q, c) => out.line(p[0], p[1], q[0], q[1], c);
  if (style === 0) pts.forEach(([x, y], i) => out.circle(x, y, dot * (0.3 + 0.7 * i / n), Math.floor((i * 4) / n)));
  else if (style === 1) pts.forEach(([x, y], i) => out.line(cx, cy, x, y, Math.floor((i * 4) / n)));
  else if (style === 2) {
    for (let i = 0; i < pts.length - 1; i++) L(pts[i], pts[i + 1], Math.floor((i * 3) / n));
    for (const fib of [8, 13, 21]) {
      for (let i = 0; i < pts.length - fib; i++) L(pts[i], pts[i + fib], (Math.floor((i * 3) / n) + 1) % 4);
    }
  } else if (style === 3) {
    // three nearest neighbours by (squared distance, index), as Python's sorted list of (d, j) tuples
    for (let i = 0; i < pts.length; i++) {
      const best = [];
      for (let j = 0; j < pts.length; j++) {
        if (i === j) continue;
        const d = (pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2;
        if (best.length === 3 && (d > best[2][0] || (d === best[2][0] && j > best[2][1]))) continue;
        best.push([d, j]);
        best.sort((u, v) => u[0] - v[0] || u[1] - v[1]);
        if (best.length > 3) best.pop();
      }
      for (const [, j] of best) if (j > i) L(pts[i], pts[j], Math.floor((i * 3) / n));
    }
  }
  return out;
}
