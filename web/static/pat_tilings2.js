// Classic tilings, part 2: ports of patterns/truchet.py, patterns/voronoi.py, patterns/hexagonal.py and
// patterns/sierpinski.py.
import { Commands, midpoint, polygonVertices, radians } from './pyutil.js';
import { random } from './pyrandom.js';

const get = (params, k, d) => (params[k] ?? d);

// --- truchet.py ---------------------------------------------------------------------------------------------------
export function truchet(width, height, params, margin = 40) {
  const cols = get(params, 'cols', 15), rows = get(params, 'rows', 15), style = get(params, 'style', 0);
  const seed = get(params, 'seed', 42), seg = get(params, 'arc_segments', 12);
  random.seed(seed);
  const out = new Commands();
  const w = width - 2 * margin, h = height - 2 * margin, cw = w / cols, ch = h / rows;
  for (let i = 0; i < cols; i++) {
    for (let j = 0; j < rows; j++) {
      const x = margin + i * cw, y = margin + j * ch, o = random.randint(0, 1);
      if (style === 0) arcTile(out, x, y, cw, ch, o, seg, Math.min(cw, ch) / 2, 0);
      else if (style === 1) {
        if (o === 0) out.line(x, y, x + cw, y + ch, 0); else out.line(x + cw, y, x, y + ch, 0);
      } else {
        const rMax = Math.min(cw, ch) / 2;
        for (let layer = 0; layer < 3; layer++) {
          const r = rMax * (1 - layer * 0.25);
          if (r <= 0) break;
          arcTile(out, x, y, cw, ch, o, seg, r, layer % 3);
        }
      }
    }
  }
  return out;
}

function arcTile(out, x, y, w, h, orient, segments, r, c) {
  if (orient === 0) {
    arc(out, x, y, r, 0, Math.PI / 2, segments, c);
    arc(out, x + w, y + h, r, Math.PI, 3 * Math.PI / 2, segments, c);
  } else {
    arc(out, x + w, y, r, Math.PI / 2, Math.PI, segments, c);
    arc(out, x, y + h, r, 3 * Math.PI / 2, 2 * Math.PI, segments, c);
  }
}

function arc(out, cx, cy, r, start, end, segments, c) {
  for (let i = 0; i < segments; i++) {
    const a1 = start + (end - start) * i / segments, a2 = start + (end - start) * (i + 1) / segments;
    out.line(cx + r * Math.cos(a1), cy + r * Math.sin(a1), cx + r * Math.cos(a2), cy + r * Math.sin(a2), c);
  }
}

// --- voronoi.py -----------------------------------------------------------------------------------------------------
export function voronoi(width, height, params, margin = 40) {
  const n = get(params, 'num_points', 50), seed = get(params, 'seed', 42), relax = get(params, 'relax_steps', 2);
  const showPts = get(params, 'show_points', true), dual = get(params, 'dual_mode', false);
  random.seed(seed);
  const out = new Commands();
  const x0 = margin, y0 = margin, w = width - 2 * margin, h = height - 2 * margin;
  let pts = [];
  for (let i = 0; i < n; i++) { const px = random.random() * w + x0; pts.push([px, random.random() * h + y0]); }
  for (let s = 0; s < relax; s++) pts = lloydRelax(pts, x0, y0, w, h);
  if (dual) {
    for (const [i1, i2, i3] of delaunay(pts)) {
      const p1 = pts[i1], p2 = pts[i2], p3 = pts[i3];
      out.line(p1[0], p1[1], p2[0], p2[1], 0); out.line(p2[0], p2[1], p3[0], p3[1], 0); out.line(p3[0], p3[1], p1[0], p1[1], 0);
    }
  } else voronoiEdges(out, pts, x0, y0, w, h);
  if (showPts) for (const [px, py] of pts) out.circle(px, py, 2, 2);
  return out;
}

function lloydRelax(pts, x0, y0, w, h) {
  const res = 100, dx = w / res, dy = h / res, n = pts.length;
  const sx = new Float64Array(n), sy = new Float64Array(n), cnt = new Int32Array(n);
  for (let gi = 0; gi < res; gi++) {
    for (let gj = 0; gj < res; gj++) {
      const x = x0 + (gi + 0.5) * dx, y = y0 + (gj + 0.5) * dy;
      let best = 0, bestD = Infinity;
      for (let p = 0; p < n; p++) {
        const d = (x - pts[p][0]) ** 2 + (y - pts[p][1]) ** 2;
        if (d < bestD) { bestD = d; best = p; }
      }
      sx[best] += x; sy[best] += y; cnt[best]++;
    }
  }
  return pts.map((p, i) => (cnt[i] > 0 ? [sx[i] / cnt[i], sy[i] / cnt[i]] : p));
}

function circumcenter(p1, p2, p3) {
  const [ax, ay] = p1, [bx, by] = p2, [cx, cy] = p3;
  const d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by));
  if (Math.abs(d) < 1e-10) return null;
  const ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d;
  const uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d;
  return [ux, uy];
}

const sameTri = (a, b) => a[0] === b[0] && a[1] === b[1] && a[2] === b[2];

function voronoiEdges(out, pts, x0, y0, w, h) {
  const tris = delaunay(pts), drawn = new Set();
  const clampX = v => Math.max(x0, Math.min(x0 + w, v)), clampY = v => Math.max(y0, Math.min(y0 + h, v));
  for (const tri of tris) {
    const [i1, i2, i3] = tri;
    const cc = circumcenter(pts[i1], pts[i2], pts[i3]);
    if (cc === null) continue;
    for (const edge of [[i1, i2], [i2, i3], [i3, i1]]) {
      const e = edge[0] < edge[1] ? edge : [edge[1], edge[0]];
      const key = e[0] + ',' + e[1];
      if (drawn.has(key)) continue;
      let ncc = null;
      for (const t2 of tris) {
        if (sameTri(t2, tri)) continue;
        if (t2.includes(e[0]) && t2.includes(e[1])) { ncc = circumcenter(pts[t2[0]], pts[t2[1]], pts[t2[2]]); break; }
      }
      drawn.add(key);
      if (ncc) out.line(clampX(cc[0]), clampY(cc[1]), clampX(ncc[0]), clampY(ncc[1]), 0);
    }
  }
}

// Bowyer-Watson, as written in voronoi.py (super-triangle, bad triangles, boundary polygon).
function delaunay(points) {
  if (points.length < 3) return [];
  const xs = points.map(p => p[0]), ys = points.map(p => p[1]);
  const minX = Math.min(...xs) - 1, minY = Math.min(...ys) - 1, maxX = Math.max(...xs) + 1, maxY = Math.max(...ys) + 1;
  const dx = maxX - minX, dy = maxY - minY, dmax = Math.max(dx, dy) * 10;
  const all = [...points, [minX - dmax, minY - 1], [minX + dmax * 2, minY - 1], [minX + dx / 2, maxY + dmax]];
  const n = points.length;
  let tris = [[n, n + 1, n + 2]];
  for (let pi = 0; pi < n; pi++) {
    const [px, py] = all[pi];
    const bad = [];
    for (const t of tris) {
      const cc = circumcenter(all[t[0]], all[t[1]], all[t[2]]);
      if (cc === null) continue;
      const r2 = (all[t[0]][0] - cc[0]) ** 2 + (all[t[0]][1] - cc[1]) ** 2;
      if ((px - cc[0]) ** 2 + (py - cc[1]) ** 2 < r2) bad.push(t);
    }
    const polygon = [];
    for (const t of bad) {
      for (const edge of [[t[0], t[1]], [t[1], t[2]], [t[2], t[0]]]) {
        let shared = false;
        for (const o of bad) {
          if (sameTri(o, t)) continue;
          for (const oe of [[o[0], o[1]], [o[1], o[2]], [o[2], o[0]]]) {
            if ((edge[0] === oe[1] && edge[1] === oe[0]) || (edge[0] === oe[0] && edge[1] === oe[1])) { shared = true; break; }
          }
          if (shared) break;
        }
        if (!shared) polygon.push(edge);
      }
    }
    for (const t of bad) { const k = tris.findIndex(x => sameTri(x, t)); tris.splice(k, 1); } // list.remove
    for (const e of polygon) tris.push([pi, e[0], e[1]]);
  }
  return tris.filter(t => t[0] < n && t[1] < n && t[2] < n);
}

// --- hexagonal.py ---------------------------------------------------------------------------------------------------
export function hexagonal(width, height, params, margin = 40) {
  const size = get(params, 'size', 35), decoration = get(params, 'decoration', 1);
  const innerScale = get(params, 'inner_hex', 0.5), pointy = get(params, 'pointy_top', true);
  const out = new Commands();
  const start = pointy ? -Math.PI / 6 : 0;
  const colSp = pointy ? size * Math.sqrt(3) : size * 1.5, rowSp = pointy ? size * 1.5 : size * Math.sqrt(3);
  const x0 = margin + size, y0 = margin + size;
  const cols = Math.trunc((width - 2 * margin) / colSp) + 1, rows = Math.trunc((height - 2 * margin) / rowSp) + 1;
  const L = (a, b, k) => out.line(a[0], a[1], b[0], b[1], k);
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const cx = pointy ? x0 + col * colSp + (row % 2) * colSp / 2 : x0 + col * colSp;
      const cy = pointy ? y0 + row * rowSp : y0 + row * rowSp + (col % 2) * rowSp / 2;
      if (cx > width - margin || cy > height - margin) continue;
      const verts = polygonVertices([cx, cy], size, 6, start);
      for (let i = 0; i < 6; i++) L(verts[i], verts[(i + 1) % 6], 0);
      let inner = null;
      if (decoration >= 1) {
        inner = polygonVertices([cx, cy], size * innerScale, 6, start);
        for (let i = 0; i < 6; i++) L(inner[i], inner[(i + 1) % 6], 1);
      }
      if (decoration >= 2) for (let i = 0; i < 6; i++) L(verts[i], inner[i], 1);
      if (decoration >= 3) for (let i = 0; i < 6; i++) L(verts[i], verts[(i + 2) % 6], 2);
      if (decoration >= 4) {
        for (let i = 0; i < 12; i++) {
          const a = start + i * Math.PI / 6;
          out.line(cx, cy, cx + size * 0.9 * Math.cos(a), cy + size * 0.9 * Math.sin(a), 2);
        }
        out.circle(cx, cy, size * 0.06, 2);
      }
    }
  }
  return out;
}

// --- sierpinski.py --------------------------------------------------------------------------------------------------
export function sierpinski(width, height, params, margin = 40) {
  const depth = get(params, 'depth', 5), mode = get(params, 'mode', 0), rotation = radians(get(params, 'rotation', 0));
  const out = new Commands();
  const cx = width / 2, cy = height / 2, size = Math.min(width, height) - 2 * margin;
  if (mode === 0) {
    const h = size * Math.sqrt(3) / 2;
    let p1 = [cx, cy - h * 2 / 3], p2 = [cx - size / 2, cy + h / 3], p3 = [cx + size / 2, cy + h / 3];
    if (rotation !== 0) {
      const c = Math.cos(rotation), s = Math.sin(rotation);
      const rot = p => { const dx = p[0] - cx, dy = p[1] - cy; return [cx + dx * c - dy * s, cy + dx * s + dy * c]; };
      [p1, p2, p3] = [rot(p1), rot(p2), rot(p3)];
    }
    triangle(out, p1, p2, p3, depth);
  } else if (mode === 1) carpet(out, cx - size / 2, cy - size / 2, size, depth);
  else {
    const r = size / 2, verts = [];
    for (let i = 0; i < 6; i++) {
      const a = rotation + i * Math.PI / 3 - Math.PI / 6;
      verts.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]);
    }
    hexagon(out, verts, depth);
  }
  return out;
}

function triangle(out, p1, p2, p3, depth) {
  if (depth === 0) {
    out.line(p1[0], p1[1], p2[0], p2[1], 0); out.line(p2[0], p2[1], p3[0], p3[1], 0); out.line(p3[0], p3[1], p1[0], p1[1], 0);
    return;
  }
  const m12 = midpoint(p1, p2), m23 = midpoint(p2, p3), m31 = midpoint(p3, p1);
  triangle(out, p1, m12, m31, depth - 1);
  triangle(out, m12, p2, m23, depth - 1);
  triangle(out, m31, m23, p3, depth - 1);
}

function square(out, x, y, s, c) {
  out.line(x, y, x + s, y, c); out.line(x + s, y, x + s, y + s, c); out.line(x + s, y + s, x, y + s, c); out.line(x, y + s, x, y, c);
}

function carpet(out, x, y, size, depth) {
  if (depth === 0) { square(out, x, y, size, 0); return; }
  const s = size / 3;
  for (let i = 0; i < 3; i++) {
    for (let j = 0; j < 3; j++) {
      if (i === 1 && j === 1) { square(out, x + s, y + s, s, 1); continue; }
      carpet(out, x + i * s, y + j * s, s, depth - 1);
    }
  }
}

function hexagon(out, verts, depth) {
  if (depth === 0) {
    for (let i = 0; i < 6; i++) { const p = verts[i], q = verts[(i + 1) % 6]; out.line(p[0], p[1], q[0], q[1], 0); }
    return;
  }
  let cx = 0, cy = 0;
  for (const v of verts) cx += v[0];
  for (const v of verts) cy += v[1];
  cx /= 6; cy /= 6;
  for (let i = 0; i < 6; i++) {
    const v = verts[i], ncx = (cx + v[0]) / 2, ncy = (cy + v[1]) / 2, nr = Math.hypot(v[0] - cx, v[1] - cy) / 3;
    const base = Math.atan2(v[1] - cy, v[0] - cx), nv = [];
    for (let j = 0; j < 6; j++) { const a = base + j * Math.PI / 3; nv.push([ncx + nr * Math.cos(a), ncy + nr * Math.sin(a)]); }
    hexagon(out, nv, depth - 1);
  }
}
