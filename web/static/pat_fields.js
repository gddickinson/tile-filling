// Flow and field patterns: ports of patterns/flow_field.py, patterns/apollonian.py, patterns/chladni.py and
// patterns/reaction_diffusion.py.
import { Commands, csqrt, pyRound } from './pyutil.js';
import { random } from './pyrandom.js';

const get = (params, k, d) => (params[k] ?? d);

// --- flow_field.py ------------------------------------------------------------------------------------------------------
export function flowField(width, height, params, margin = 40) {
  const nP = get(params, 'particles', 500), steps = get(params, 'steps', 80), step = get(params, 'step_size', 2.0);
  const scale = get(params, 'noise_scale', 0.005), octaves = get(params, 'octaves', 3), seed = get(params, 'seed', 42);
  const curl = get(params, 'curl', 1.0);
  random.seed(seed);
  const out = new Commands();
  const x0 = margin, y0 = margin, w = width - 2 * margin, h = height - 2 * margin;
  for (let p = 0; p < nP; p++) {
    let px = x0 + random.random() * w, py = y0 + random.random() * h;
    for (let s = 0; s < steps; s++) {
      let angle = 0.0, amp = 1.0, f = scale;
      for (let o = 0; o < octaves; o++) {
        const n = Math.sin(px * f * 1.7 + seed * 13.37 + o * 5.1) * Math.cos(py * f * 2.3 + seed * 7.13 + o * 3.7) +
          Math.sin((px + py) * f * 0.9 + seed * 11.1 + o * 2.3) * 0.5;
        angle += n * amp * Math.PI * curl;
        amp *= 0.5; f *= 2.0;
      }
      const nx = px + Math.cos(angle) * step, ny = py + Math.sin(angle) * step;
      if (nx < x0 || nx > x0 + w || ny < y0 || ny > y0 + h) break;
      out.line(px, py, nx, ny, Math.floor((p * 4) / nP));
      px = nx; py = ny;
    }
  }
  return out;
}

// --- apollonian.py --------------------------------------------------------------------------------------------------------
export function apollonian(width, height, params, margin = 40) {
  const depth = get(params, 'depth', 5), minR = get(params, 'min_radius', 2.0), initial = get(params, 'initial', 0);
  const segs = get(params, 'arc_segments', 36);
  const out = new Commands();
  const cx = width / 2, cy = height / 2, R = Math.min(width, height) / 2 - margin;
  let circles;
  if (initial === 0) { const r = R / 2; circles = [[cx, cy, -R], [cx - r, cy, r], [cx + r, cy, r], [cx, cy - 2 * R / 3, R / 3]]; } // tangent (Descartes)
  else if (initial === 1) {
    const r = R / (1 + 2 / Math.sqrt(3)), off = R - r;
    circles = [[cx, cy, -R]];
    for (let i = 0; i < 3; i++) { const a = i * 2 * Math.PI / 3 - Math.PI / 2; circles.push([cx + off * Math.cos(a), cy + off * Math.sin(a), r]); }
  } else {
    const r = R * 0.4;
    circles = [[cx, cy, -R]];
    for (let i = 0; i < 3; i++) {
      const a = i * 2 * Math.PI / 3 - Math.PI / 2, d = R - r;
      circles.push([cx + d * 0.6 * Math.cos(a), cy + d * 0.6 * Math.sin(a), r]);
    }
  }
  for (const [x, y, r] of circles) circleSegs(out, x, y, Math.abs(r), segs, 0);
  fillGasket(out, circles, depth, minR, segs);
  return out;
}

function fillGasket(out, circles, maxDepth, minR, segs) {
  const n = circles.length;
  if (n < 3) return;
  const queue = [];
  for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) for (let k = j + 1; k < n; k++) queue.push([circles[i], circles[j], circles[k], 0]);
  const seen = new Set(), all = [...circles];
  for (let qi = 0; qi < queue.length; qi++) {               // queue.pop(0) in Python: a FIFO walk
    const [c1, c2, c3, lvl] = queue[qi];
    if (lvl >= maxDepth) continue;
    for (const nc of descartes(c1, c2, c3)) {
      const [ncx, ncy, nr] = nc;
      if (Math.abs(nr) < minR) continue;
      const key = `${pyRound(ncx, 1)}|${pyRound(ncy, 1)}|${pyRound(Math.abs(nr), 1)}`;
      if (seen.has(key)) continue;
      seen.add(key);
      let valid = true;
      for (const ec of all) {
        if (Math.abs(nr) > 1 && Math.hypot(ncx - ec[0], ncy - ec[1]) < Math.abs(nr) * 0.3) { valid = false; break; }
      }
      if (!valid) continue;
      circleSegs(out, ncx, ncy, Math.abs(nr), segs, Math.min(3, lvl + 1));
      all.push(nc);
      queue.push([c1, c2, nc, lvl + 1], [c1, c3, nc, lvl + 1], [c2, c3, nc, lvl + 1]);
    }
  }
}

// Descartes' circle theorem with complex centres, written out as in apollonian._descartes.
function descartes([x1, y1, r1], [x2, y2, r2], [x3, y3, r3]) {
  const k1 = r1 !== 0 ? 1.0 / r1 : 0, k2 = r2 !== 0 ? 1.0 / r2 : 0, k3 = r3 !== 0 ? 1.0 / r3 : 0;
  const disc = k1 * k2 + k2 * k3 + k3 * k1;
  if (disc < 0) return [];
  const sq = Math.sqrt(disc), res = [];
  const cm = (a, b, c, d) => [a * c - b * d, a * d + b * c];      // complex product
  for (const sign of [1, -1]) {
    const k4 = k1 + k2 + k3 + sign * 2 * sq;
    if (Math.abs(k4) < 1e-10) continue;
    const r4 = 1.0 / k4;
    const sumRe = x1 * k1 + x2 * k2 + x3 * k3, sumIm = y1 * k1 + y2 * k2 + y3 * k3;
    const p12 = cm(x1, y1, x2, y2), p23 = cm(x2, y2, x3, y3), p13 = cm(x1, y1, x3, y3);
    const prodRe = p12[0] * k1 * k2 + p23[0] * k2 * k3 + p13[0] * k1 * k3;
    const prodIm = p12[1] * k1 * k2 + p23[1] * k2 * k3 + p13[1] * k1 * k3;
    const [sRe, sIm] = csqrt(prodRe, prodIm);
    for (const ps of [1, -1]) {
      const x4 = (sumRe + ps * 2 * sRe) / k4, y4 = (sumIm + ps * 2 * sIm) / k4;
      if (Math.abs(r4) > 0.1 && tangentToAll(x4, y4, r4, [[x1, y1, r1], [x2, y2, r2], [x3, y3, r3]])) res.push([x4, y4, r4]);
    }
  }
  return res;
}

// apollonian._tangent_to_all: keep only candidates touching all three parents (signed radii: distance = |r_i + r_4|).
function tangentToAll(x4, y4, r4, parents, rtol = 1e-6) {
  let tol = Math.abs(r4);
  for (const p of parents) tol += Math.abs(p[2]);
  tol *= rtol;
  return parents.every(([x, y, r]) => Math.abs(Math.hypot(x4 - x, y4 - y) - Math.abs(r + r4)) <= tol);
}

function circleSegs(out, cx, cy, r, segs, c) {
  if (r < 0.5) return;
  for (let i = 0; i < segs; i++) {
    const a1 = 2 * Math.PI * i / segs, a2 = 2 * Math.PI * (i + 1) / segs;
    out.line(cx + r * Math.cos(a1), cy + r * Math.sin(a1), cx + r * Math.cos(a2), cy + r * Math.sin(a2), c);
  }
}

// --- marching squares shared by chladni.py and reaction_diffusion.py ------------------------------------------------------
const CASES = { 1: ['TL'], 2: ['TR'], 3: ['LR'], 4: ['LB'], 5: ['TB'], 6: ['TL', 'RB'], 7: ['RB'], 8: ['RB'], 9: ['TR', 'LB'],
  10: ['TB'], 11: ['LB'], 12: ['LR'], 13: ['TR'], 14: ['TL'] };

// v00..v11 are corner values (already minus the threshold); eps is 0 for chladni.py (with its 0.5 fallback) and 1e-10
// for reaction_diffusion.py.
function cell(out, v00, v10, v01, v11, x0, y0, x1, y1, c, eps) {
  let k = 0;
  if (v00 > 0) k |= 1; if (v10 > 0) k |= 2; if (v01 > 0) k |= 4; if (v11 > 0) k |= 8;
  if (k === 0 || k === 15) return;
  const t = (a, b) => (eps ? Math.abs(a) / (Math.abs(a) + Math.abs(b) + eps)
    : (Math.abs(a) + Math.abs(b) > 0 ? Math.abs(a) / (Math.abs(a) + Math.abs(b)) : 0.5));
  const P = {};
  if ((v00 > 0) !== (v10 > 0)) P.T = [x0 + t(v00, v10) * (x1 - x0), y0];
  if ((v01 > 0) !== (v11 > 0)) P.B = [x0 + t(v01, v11) * (x1 - x0), y1];
  if ((v00 > 0) !== (v01 > 0)) P.L = [x0, y0 + t(v00, v01) * (y1 - y0)];
  if ((v10 > 0) !== (v11 > 0)) P.R = [x1, y0 + t(v10, v11) * (y1 - y0)];
  for (const [a, b] of CASES[k]) if (P[a] && P[b]) out.line(P[a][0], P[a][1], P[b][0], P[b][1], c);
}

// --- chladni.py -------------------------------------------------------------------------------------------------------
export function chladni(width, height, params, margin = 40) {
  const m = get(params, 'm', 5), n = get(params, 'n', 3), res = get(params, 'resolution', 150);
  const mode = get(params, 'mode', 0), threshold = get(params, 'threshold', 0.05);
  const out = new Commands();
  const w = width - 2 * margin, h = height - 2 * margin, size = Math.min(w, h);
  const ox = margin + (w - size) / 2, oy = margin + (h - size) / 2, N1 = res + 1, g = new Float64Array(N1 * N1);
  for (let i = 0; i < N1; i++) {
    for (let j = 0; j < N1; j++) {
      const x = i / res, y = j / res;
      if (mode === 0) {
        g[i * N1 + j] = Math.cos(m * Math.PI * x) * Math.cos(n * Math.PI * y) - Math.cos(n * Math.PI * x) * Math.cos(m * Math.PI * y);
      } else {
        const px = 2 * x - 1, py = 2 * y - 1, r = Math.sqrt(px * px + py * py);
        g[i * N1 + j] = r > 1.0 ? NaN : Math.cos(m * Math.atan2(py, px)) * Math.sin(n * Math.PI * r);
      }
    }
  }
  const cw = size / res;
  const contour = (level, c) => {
    for (let i = 0; i < res; i++) {
      for (let j = 0; j < res; j++) {
        const v00 = g[i * N1 + j] - level, v10 = g[(i + 1) * N1 + j] - level, v01 = g[i * N1 + j + 1] - level, v11 = g[(i + 1) * N1 + j + 1] - level;
        if (Number.isNaN(v00) || Number.isNaN(v10) || Number.isNaN(v01) || Number.isNaN(v11)) continue;
        const x0 = ox + i * cw, y0 = oy + j * cw;
        cell(out, v00, v10, v01, v11, x0, y0, x0 + cw, y0 + cw, c, 0);
      }
    }
  };
  contour(0.0, 0);                                         // nodal lines
  if (threshold > 0) {                                     // band |f| < threshold * max|f| (where sand gathers)
    let peak = 0;
    for (let i = 0; i < N1; i++) for (let j = 0; j < N1; j++) { const v = g[i * N1 + j]; if (!Number.isNaN(v) && Math.abs(v) > peak) peak = Math.abs(v); }
    for (const level of [threshold * peak, -threshold * peak]) contour(level, 1);
  }
  return out;
}

// --- reaction_diffusion.py (Gray-Scott, Du 0.16, Dv 0.08, dt 1, periodic edges, seeds from random.seed(42)) --------
export function reactionDiffusion(width, height, params, margin = 40) {
  const res = get(params, 'resolution', 80), iters = get(params, 'iterations', 3000);
  const f = get(params, 'feed', 55) / 1000.0, k = get(params, 'kill', 62) / 1000.0;
  const nC = get(params, 'contours', 3), seeds = get(params, 'seed_count', 5);
  const v = grayScott(res, iters, f, k, seeds);
  const out = new Commands();
  const w = width - 2 * margin, h = height - 2 * margin, size = Math.min(w, h);
  const ox = margin + (w - size) / 2, oy = margin + (h - size) / 2;
  let vmin = Infinity, vmax = -Infinity;
  for (const x of v) { if (x < vmin) vmin = x; if (x > vmax) vmax = x; }
  if (vmax - vmin < 1e-6) return out;
  const c = size / res;
  for (let level = 0; level < nC; level++) {
    const th = vmin + (level + 1) / (nC + 1) * (vmax - vmin);
    for (let i = 0; i < res - 1; i++) {
      for (let j = 0; j < res - 1; j++) {
        const x0 = ox + i * c, y0 = oy + j * c;
        cell(out, v[i * res + j] - th, v[(i + 1) * res + j] - th, v[i * res + j + 1] - th, v[(i + 1) * res + j + 1] - th,
          x0, y0, x0 + c, y0 + c, level, 1e-10);
      }
    }
  }
  return out;
}

export function grayScott(res, iterations, f, k, seedCount) {
  const Du = 0.16, Dv = 0.08, dt = 1.0, N = res * res;
  let u = new Float64Array(N).fill(1.0), v = new Float64Array(N), nu = new Float64Array(N), nv = new Float64Array(N);
  random.seed(42);
  for (let s = 0; s < seedCount; s++) {
    const cx = random.randint(Math.floor(res / 4), Math.floor(3 * res / 4)), cy = random.randint(Math.floor(res / 4), Math.floor(3 * res / 4));
    const r = Math.max(2, Math.floor(res / 15));
    for (let i = Math.max(0, cx - r); i < Math.min(res, cx + r); i++) {
      for (let j = Math.max(0, cy - r); j < Math.min(res, cy + r); j++) {
        if ((i - cx) ** 2 + (j - cy) ** 2 < r * r) { u[i * res + j] = 0.5; v[i * res + j] = 0.25; }
      }
    }
  }
  for (let it = 0; it < iterations; it++) {
    for (let i = 0; i < res; i++) {
      const ip = ((i + 1) % res) * res, im = ((i - 1 + res) % res) * res, ii = i * res;
      for (let j = 0; j < res; j++) {
        const jp = (j + 1) % res, jm = (j - 1 + res) % res, a = ii + j, U = u[a], V = v[a];
        const lapU = u[ip + j] + u[im + j] + u[ii + jp] + u[ii + jm] - 4 * U;
        const lapV = v[ip + j] + v[im + j] + v[ii + jp] + v[ii + jm] - 4 * V;
        const uv2 = U * V * V;
        nu[a] = U + dt * (Du * lapU - uv2 + f * (1 - U));
        nv[a] = V + dt * (Dv * lapV + uv2 - (f + k) * V);
      }
    }
    [u, nu] = [nu, u]; [v, nv] = [nv, v];
  }
  return v;
}
