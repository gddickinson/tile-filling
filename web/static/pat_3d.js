// 3D patterns: ports of patterns/iso_cubes.py and patterns/wireframe3d.py (with rendering/projection.py in pyutil.js).
import { Commands, projectIsometric, projectPerspective, radians, rotateXYZ } from './pyutil.js';
import { random } from './pyrandom.js';

const get = (params, k, d) => (params[k] ?? d);

// --- iso_cubes.py -----------------------------------------------------------------------------------------------------
export function isoCubes(width, height, params, margin = 40) {
  const gs = get(params, 'grid_size', 7), maxH = get(params, 'max_height', 4), seed = get(params, 'seed', 42);
  const mode = get(params, 'height_mode', 1), showHidden = get(params, 'show_hidden', false);
  const rotY = radians(get(params, 'rotation', 0.0));
  random.seed(seed);
  const heights = Array.from({ length: gs }, () => new Array(gs).fill(0));
  if (mode === 0) {
    random.seed(seed);
    for (let i = 0; i < gs; i++) for (let j = 0; j < gs; j++) heights[i][j] = random.randint(1, maxH);
  } else if (mode === 1) {
    for (let i = 0; i < gs; i++) {
      for (let j = 0; j < gs; j++) {
        const h = Math.sin(i * 0.8) * Math.cos(j * 0.8);
        heights[i][j] = Math.max(1, Math.trunc((h + 1) / 2 * maxH + 0.5));
      }
    }
  } else if (mode === 2) {
    const center = gs / 2.0;
    for (let i = 0; i < gs; i++) {
      for (let j = 0; j < gs; j++) {
        const dist = Math.max(Math.abs(i - center), Math.abs(j - center)) / center;
        heights[i][j] = Math.max(1, Math.trunc((1 - dist) * maxH + 0.5));
      }
    }
  }
  const cx = width / 2, cy = height / 2, size = Math.min(width, height) / (gs * 2.5);
  const out = new Commands();
  for (let i = 0; i < gs; i++) {
    for (let j = 0; j < gs; j++) {
      if (heights[i][j] <= 0) continue;
      cube(out, i, j, heights[i][j], gs, size, cx, cy, rotY, showHidden);
    }
  }
  return out;
}

function cube(out, gi, gj, h, gs, size, cx, cy, rotY, showHidden) {
  const ox = (gi - gs / 2) * size, oz = (gj - gs / 2) * size, top = h * size * 0.5;
  let v3 = [[ox, 0, oz], [ox + size, 0, oz], [ox + size, 0, oz + size], [ox, 0, oz + size],
    [ox, top, oz], [ox + size, top, oz], [ox + size, top, oz + size], [ox, top, oz + size]];
  if (rotY !== 0) v3 = v3.map(v => rotateXYZ(v, 0, rotY, 0));
  const scale = gs > 0 ? Math.min(cx, cy) * 0.8 / (gs * size * 0.5) : 1;
  const v = v3.map(p => projectIsometric(p, cx, cy, scale)[0]);
  const E = (a, b, c) => out.line(v[a][0], v[a][1], v[b][0], v[b][1], c);
  for (const [a, b] of [[4, 5], [5, 6], [6, 7], [7, 4]]) E(a, b, 0);   // top face
  for (const [a, b] of [[0, 4], [1, 5]]) E(a, b, 1);                   // front verticals
  E(0, 1, 1);                                                           // bottom front
  for (const [a, b] of [[1, 5], [2, 6]]) E(a, b, 1);                   // right verticals
  E(1, 2, 1);                                                           // bottom right
  if (showHidden) for (const [a, b] of [[2, 3], [3, 0], [3, 7], [2, 6], [0, 3]]) E(a, b, 2);
}

// --- wireframe3d.py ---------------------------------------------------------------------------------------------------
export function wireframe(width, height, params, margin = 40) {
  const surface = get(params, 'surface', 0), res = get(params, 'resolution', 30);
  const rx = radians(get(params, 'rot_x', 25.0)), ry = radians(get(params, 'rot_y', 35.0)), rz = radians(get(params, 'rot_z', 0.0));
  const focal = get(params, 'focal', 400);
  const cx = width / 2, cy = height / 2, scale = Math.min(width, height) * 0.3;
  const [verts, edges] = [torus, trefoil, sphere, klein, mobius][[0, 1, 2, 3].includes(surface) ? surface : 4](res, scale);
  const rot = verts.map(p => rotateXYZ(p, rx, ry, rz));
  const data = edges.map(([i1, i2]) => {
    const p1 = rot[i1], p2 = rot[i2];
    return [projectPerspective(p1, focal, cx, cy)[0], projectPerspective(p2, focal, cx, cy)[0], (p1[2] + p2[2]) / 2];
  });
  data.sort((a, b) => a[2] - b[2]);                        // stable, like Python's list.sort(key=...)
  let zMin = 0, zMax = 0;
  if (data.length) { zMin = Infinity; zMax = -Infinity; for (const e of data) { zMin = Math.min(zMin, e[2]); zMax = Math.max(zMax, e[2]); } }
  const out = new Commands();
  for (const [s1, s2, z] of data) {
    const t = zMax > zMin ? (z - zMin) / (zMax - zMin) : 1.0;
    out.line(s1[0], s1[1], s2[0], s2[1], Math.min(2, Math.trunc(t * 3)));
  }
  return out;
}

function gridEdges(nu, nv, wrapV) {
  const edges = [];
  for (let i = 0; i < nu; i++) {
    for (let j = 0; j < nv; j++) {
      const idx = i * nv + j;
      if (wrapV) edges.push([idx, i * nv + (j + 1) % nv, 0]);
      else if (j < nv - 1) edges.push([idx, i * nv + j + 1, 0]);
      edges.push([idx, ((i + 1) % nu) * nv + j, 1]);
    }
  }
  return edges;
}

function torus(res, scale) {
  const R = 1.0, r = 0.4, verts = [];
  for (let i = 0; i < res; i++) {
    const u = 2 * Math.PI * i / res;
    for (let j = 0; j < res; j++) {
      const v = 2 * Math.PI * j / res;
      verts.push([(R + r * Math.cos(v)) * Math.cos(u) * scale, (R + r * Math.cos(v)) * Math.sin(u) * scale, r * Math.sin(v) * scale]);
    }
  }
  return [verts, gridEdges(res, res, true)];
}

function trefoil(res, scale) {
  const n = res * 4, verts = [], edges = [];
  for (let i = 0; i < n; i++) {
    const t = 2 * Math.PI * i / n;
    verts.push([(Math.sin(t) + 2 * Math.sin(2 * t)) * scale * 0.7, (Math.cos(t) - 2 * Math.cos(2 * t)) * scale * 0.7,
      -Math.sin(3 * t) * scale * 0.7]);
  }
  for (let i = 0; i < n; i++) edges.push([i, (i + 1) % n, 0]);
  return [verts, edges];
}

function sphere(res, scale) {
  const nu = res, nv = Math.floor(res / 2), verts = [];
  for (let i = 0; i < nu; i++) {
    const u = 2 * Math.PI * i / nu;
    for (let j = 0; j < nv + 1; j++) {
      const v = Math.PI * j / nv - Math.PI / 2;
      verts.push([Math.cos(v) * Math.cos(u) * scale, Math.cos(v) * Math.sin(u) * scale, Math.sin(v) * scale]);
    }
  }
  return [verts, gridEdges(nu, nv + 1, false)];
}

function klein(res, scale) {
  const verts = [];
  for (let i = 0; i < res; i++) {
    const u = 2 * Math.PI * i / res;
    for (let j = 0; j < res; j++) {
      const v = 2 * Math.PI * j / res, r = 1.0;
      const x = (r + Math.cos(u / 2) * Math.sin(v) - Math.sin(u / 2) * Math.sin(2 * v)) * Math.cos(u);
      const y = (r + Math.cos(u / 2) * Math.sin(v) - Math.sin(u / 2) * Math.sin(2 * v)) * Math.sin(u);
      const z = Math.sin(u / 2) * Math.sin(v) + Math.cos(u / 2) * Math.sin(2 * v);
      verts.push([x * scale * 0.5, y * scale * 0.5, z * scale * 0.5]);
    }
  }
  return [verts, gridEdges(res, res, true)];
}

function mobius(res, scale) {
  const nu = res * 2, nv = Math.max(4, Math.floor(res / 4)), verts = [];
  for (let i = 0; i < nu; i++) {
    const u = 2 * Math.PI * i / nu;
    for (let j = 0; j < nv; j++) {
      const s = -0.5 + j / (nv - 1);
      verts.push([(1 + s * 0.5 * Math.cos(u / 2)) * Math.cos(u) * scale * 0.7, (1 + s * 0.5 * Math.cos(u / 2)) * Math.sin(u) * scale * 0.7,
        s * 0.5 * Math.sin(u / 2) * scale * 0.7]);
    }
  }
  return [verts, gridEdges(nu, nv, false)];
}
