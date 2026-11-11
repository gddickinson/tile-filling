// Post-processing effects of rendering/effects.py, ported pixel for pixel (including Pillow's arithmetic for
// GaussianBlur, ImageEnhance.Brightness, ImageChops.screen/multiply/add and Image.composite).
// Images are { width, height, data } with RGBA bytes (alpha ignored, kept 255), like canvas ImageData.
import { random } from './pyrandom.js';

const blank = (w, h) => { const d = new Uint8ClampedArray(w * h * 4); for (let i = 3; i < d.length; i += 4) d[i] = 255; return { width: w, height: h, data: d }; };
const copy = img => ({ width: img.width, height: img.height, data: new Uint8ClampedArray(img.data) });

// apply_kaleidoscope: mirror every wedge onto the first one (source pixels picked with int() truncation).
export function kaleidoscope(img, folds = 6) {
  if (folds < 2) return img;
  const { width: w, height: h, data: src } = img, cx = Math.floor(w / 2), cy = Math.floor(h / 2);
  const out = blank(w, h), d = out.data, wedge = 2 * Math.PI / folds;
  for (let i = 0; i < d.length; i += 4) { d[i] = src[0]; d[i + 1] = src[1]; d[i + 2] = src[2]; }
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const dx = x - cx, dy = y - cy, r = Math.sqrt(dx * dx + dy * dy), o = 4 * (y * w + x);
      let s;
      if (r === 0) s = 4 * (cy * w + cx);
      else {
        let a = Math.atan2(dy, dx);
        if (a < 0) a += 2 * Math.PI;
        const k = Math.trunc(a / wedge);
        let la = a - k * wedge;
        if (k % 2 === 1) la = wedge - la;
        const sx = Math.trunc(cx + r * Math.cos(la)), sy = Math.trunc(cy + r * Math.sin(la));
        if (!(sx >= 0 && sx < w && sy >= 0 && sy < h)) continue;
        s = 4 * (sy * w + sx);
      }
      d[o] = src[s]; d[o + 1] = src[s + 1]; d[o + 2] = src[s + 2];
    }
  }
  return out;
}

// Pillow's GaussianBlur: three passes of an extended box blur (libImaging/BoxBlur.c), float32 radius maths.
const f32 = Math.fround;
function boxRadius(radius, passes) {
  const sigma2 = f32(f32(radius * radius) / passes);
  const L = f32(Math.sqrt(12.0 * sigma2 + 1.0));
  const l = f32(Math.floor((L - 1.0) / 2.0));
  let a = f32(f32(2 * l + 1) * f32(f32(l * f32(l + 1)) - f32(3 * sigma2)));
  a = f32(a / f32(6 * f32(sigma2 - f32(f32(l + 1) * f32(l + 1)))));
  return f32(l + a);
}

function blurLine(inp, outp, n, stride, radius, ww, fw) {
  // inp/outp: arrays of n values read at index i*stride; mirrors ImagingLineBoxBlur8
  const lastx = n - 1, edgeA = Math.min(radius + 1, n), edgeB = Math.max(n - radius - 1, 0);
  const at = i => inp[i * stride];
  let acc = at(0) * (radius + 1);
  for (let x = 0; x < edgeA - 1; x++) acc += at(x);
  acc += at(lastx) * (radius - edgeA + 1);
  const save = (x, l, r) => { outp[x * stride] = Math.floor((acc * ww + (at(l) + at(r)) * fw + (1 << 23)) / 16777216); };
  if (edgeA <= edgeB) {
    for (let x = 0; x < edgeA; x++) { acc += at(x + radius) - at(0); save(x, 0, x + radius + 1); }
    for (let x = edgeA; x < edgeB; x++) { acc += at(x + radius) - at(x - radius - 1); save(x, x - radius - 1, x + radius + 1); }
    for (let x = edgeB; x <= lastx; x++) { acc += at(lastx) - at(x - radius - 1); save(x, x - radius - 1, lastx); }
  } else {
    for (let x = 0; x < edgeB; x++) { acc += at(x + radius) - at(0); save(x, 0, x + radius + 1); }
    for (let x = edgeB; x < edgeA; x++) { acc += at(lastx) - at(0); save(x, 0, lastx); }
    for (let x = edgeA; x <= lastx; x++) { acc += at(lastx) - at(x - radius - 1); save(x, x - radius - 1, lastx); }
  }
}

export function gaussianBlur(img, radius, passes = 3) {
  const { width: w, height: h } = img, br = boxRadius(radius, passes), ri = Math.trunc(br);
  const ww = Math.trunc(f32(16777216 / f32(br * 2 + 1))), fw = Math.floor((16777216 - (ri * 2 + 1) * ww) / 2);
  const out = copy(img), d = out.data, tmp = new Float64Array(Math.max(w, h)), line = new Float64Array(Math.max(w, h));
  for (let c = 0; c < 3; c++) {
    for (let p = 0; p < passes; p++) {                      // horizontal passes
      for (let y = 0; y < h; y++) {
        for (let x = 0; x < w; x++) line[x] = d[4 * (y * w + x) + c];
        blurLine(line, tmp, w, 1, ri, ww, fw);
        for (let x = 0; x < w; x++) d[4 * (y * w + x) + c] = tmp[x];
      }
    }
    for (let p = 0; p < passes; p++) {                      // vertical passes (Pillow transposes and blurs rows)
      for (let x = 0; x < w; x++) {
        for (let y = 0; y < h; y++) line[y] = d[4 * (y * w + x) + c];
        blurLine(line, tmp, h, 1, ri, ww, fw);
        for (let y = 0; y < h; y++) d[4 * (y * w + x) + c] = tmp[y];
      }
    }
  }
  return out;
}

// apply_gaussian_glow: blur, ImageEnhance.Brightness(1 + intensity), ImageChops.screen(img, glow).
export function gaussianGlow(img, { radius = 8, intensity = 0.6 } = {}) {
  const g = gaussianBlur(img, radius), out = copy(img), a = f32(1.0 + intensity);
  for (let i = 0; i < out.data.length; i += 4) {
    for (let c = 0; c < 3; c++) {
      const t = f32(a * g.data[i + c]), b = t <= 0 ? 0 : t >= 255 ? 255 : Math.trunc(t);
      out.data[i + c] = 255 - Math.trunc((255 - img.data[i + c]) * (255 - b) / 255);
    }
  }
  return out;
}

// apply_vignette: mask int(255 * max(0, 1 - s d^2)), Image.composite onto black (Pillow's DIV255 rounding).
export function vignette(img, { strength = 0.5 } = {}) {
  const { width: w, height: h } = img, out = copy(img), cx = w / 2, cy = h / 2;
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const dx = (x - cx) / cx, dy = (y - cy) / cy, d = Math.sqrt(dx * dx + dy * dy);
      const m = Math.trunc(255 * Math.max(0, 1 - strength * d * d)), o = 4 * (y * w + x);
      for (let c = 0; c < 3; c++) { const t = img.data[o + c] * m + 128; out.data[o + c] = ((t >> 8) + t) >> 8; }
    }
  }
  return out;
}

// apply_chromatic_aberration: red shifted left, blue shifted right by `offset`, uncovered columns black.
export function chromatic(img, { offset = 3 } = {}) {
  const { width: w, height: h, data: s } = img, out = copy(img), d = out.data;
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const o = 4 * (y * w + x), xr = x + offset, xb = x - offset;
      d[o] = xr < w ? s[4 * (y * w + xr)] : 0;
      d[o + 2] = xb >= 0 ? s[4 * (y * w + xb) + 2] : 0;
    }
  }
  return out;
}

// apply_scan_lines: every `spacing`-th row multiplied by int(255 * (1 - opacity)) / 255 (integer division).
export function scanLines(img, { spacing = 3, opacity = 0.4 } = {}) {
  const { width: w, height: h } = img, out = copy(img), dark = Math.trunc(255 * (1 - opacity));
  for (let y = 0; y < h; y += spacing) {
    for (let x = 0; x < w; x++) { const o = 4 * (y * w + x); for (let c = 0; c < 3; c++) out.data[o + c] = Math.trunc(img.data[o + c] * dark / 255); }
  }
  return out;
}

// apply_noise_grain: one randint(-amount, amount) per pixel from Python's global generator (seeded if seed given),
// grey noise 128 + v, combined with ImageChops.add(img, noise, scale=2, offset=-64).
export function grain(img, { amount = 30, seed = null } = {}) {
  if (seed !== null) random.seed(seed);
  const out = copy(img);
  for (let i = 0; i < out.data.length; i += 4) {
    const n = 128 + random.randint(-amount, amount);
    for (let c = 0; c < 3; c++) out.data[i + c] = Math.max(0, Math.min(255, Math.trunc((img.data[i + c] + n) / 2 + -64)));
  }
  return out;
}

// render_to_image's post-processing chain, in its order, with the strengths from rendering/settings.py.
export function applyEffects(img, fx, strengths) {
  if (fx.kaleidoscope >= 2) img = kaleidoscope(img, fx.kaleidoscope);
  if (fx.gauss_glow) img = gaussianGlow(img, strengths.gauss_glow);
  if (fx.vignette) img = vignette(img, strengths.vignette);
  if (fx.chromatic) img = chromatic(img, strengths.chromatic);
  if (fx.scanlines) img = scanLines(img, strengths.scanlines);
  if (fx.grain) img = grain(img, strengths.grain);
  return img;
}
