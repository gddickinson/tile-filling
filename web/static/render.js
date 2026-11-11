// Drawing commands to pixels, following rendering/renderer.py: background fill, optional glow pass (colour // 4,
// width max(3, int(3 * lw))), main pass (width max(1, int(lw))), all at `supersample` x then downscaled, then the
// post-processing chain of effects.js. Also an SVG export of the same vector pass (web addition).
import { gradientColor, getLineColor, hexToRgb } from './pyutil.js';
import { applyEffects } from './effects.js';

const newCanvas = (w, h) => (typeof OffscreenCanvas !== 'undefined' ? new OffscreenCanvas(w, h)
  : Object.assign(document.createElement('canvas'), { width: w, height: h }));

function colorFn(palette, gradient, total) {
  return gradient ? (i => gradientColor(palette, i / total)) : ((i, c) => getLineColor(palette, c));
}

// One pass: consecutive commands of the same colour and kind go into one path (same pixels, far fewer strokes).
function pass(ctx, cmds, colorOf, ss, width, glow) {
  let path = null, style = null;
  const flush = () => { if (path) { ctx.strokeStyle = style; ctx.stroke(path); path = null; } };
  ctx.lineWidth = width;
  cmds.forEach((k, c, xy, o, i) => {
    if (glow && k === 2) return;                            // the glow pass skips polygons, as in Python
    let col = colorOf(i, c);
    if (glow) { const [r, g, b] = hexToRgb(col); col = `rgb(${r >> 2},${g >> 2},${b >> 2})`; }
    if (col !== style || k !== 0) { flush(); style = col; path = new Path2D(); }
    if (k === 0) { path.moveTo(xy[o] * ss, xy[o + 1] * ss); path.lineTo(xy[o + 2] * ss, xy[o + 3] * ss); }
    else if (k === 1) {
      // PIL's ellipse outline is drawn inside the bounding box; the glow ring uses r + 2 (supersampled pixels)
      const r = xy[o + 2] * ss + (glow ? 2 : 0), rr = Math.max(0, r - width / 2);
      path.moveTo(xy[o] * ss + rr, xy[o + 1] * ss); path.arc(xy[o] * ss, xy[o + 1] * ss, rr, 0, 2 * Math.PI);
      flush();
    } else {
      const n = xy[o];
      for (let j = 0; j < n; j++) (j ? path.lineTo : path.moveTo).call(path, xy[o + 1 + 2 * j] * ss, xy[o + 2 + 2 * j] * ss);
      path.closePath(); ctx.lineWidth = 1; flush(); ctx.lineWidth = width;
    }
  });
  flush();
}

// render_to_image(commands, w, h, palette, line_width, glow, gradient, supersample, **effects) -> canvas of w x h.
export function renderToCanvas(cmds, w, h, { palette, lineWidth = 1, glow = false, gradient = false, supersample = 2,
  effects = {}, strengths = {} }) {
  const ss = supersample, sw = Math.trunc(w * ss), sh = Math.trunc(h * ss), slw = lineWidth * ss;
  const big = newCanvas(sw, sh), ctx = big.getContext('2d');
  ctx.fillStyle = palette.background; ctx.fillRect(0, 0, sw, sh);
  ctx.lineCap = 'butt'; ctx.lineJoin = 'miter';
  const colorOf = colorFn(palette, gradient, cmds.length || 1);
  if (glow) pass(ctx, cmds, colorOf, ss, Math.max(3, Math.trunc(slw * 3)), true);
  pass(ctx, cmds, colorOf, ss, Math.max(1, Math.trunc(slw)), false);
  let out = big;
  if (ss > 1) {
    out = newCanvas(w, h);
    const o = out.getContext('2d');
    o.imageSmoothingEnabled = true; o.imageSmoothingQuality = 'high';
    o.drawImage(big, 0, 0, w, h);
  }
  const any = (effects.kaleidoscope >= 2) || ['gauss_glow', 'vignette', 'chromatic', 'scanlines', 'grain'].some(k => effects[k]);
  if (any) {
    const o = out.getContext('2d'), img = o.getImageData(0, 0, w, h);
    const res = applyEffects({ width: w, height: h, data: img.data }, effects, strengths);
    o.putImageData(new ImageData(res.data, w, h), 0, 0);
  }
  return out;
}

// render_high_res: scale x size and line width, no supersampling (the desktop "Export Hi-Res PNG").
export function renderHighRes(cmdsAtScale, w, h, opts, scale) {
  return renderToCanvas(cmdsAtScale, w * scale, h * scale, { ...opts, lineWidth: opts.lineWidth * scale, supersample: 1 });
}

// Scale every coordinate of a command list (for the hi-res export the pattern is drawn at 1x then scaled, as Python).
export function scaled(cmds, s) {
  const out = Object.create(Object.getPrototypeOf(cmds));
  out.kind = cmds.kind; out.col = cmds.col; out.xy = cmds.xy.slice();
  cmds.forEach((k, c, xy, o) => {
    if (k === 2) { for (let j = 0; j < xy[o]; j++) { out.xy[o + 1 + 2 * j] *= s; out.xy[o + 2 + 2 * j] *= s; } }
    else for (let j = 0; j < (k === 0 ? 4 : 3); j++) out.xy[o + j] *= s;
  });
  return out;
}

// SVG of the vector passes (no raster effects). Line widths are the effective widths of the 2x render.
export function toSVG(cmds, w, h, { palette, lineWidth = 1, glow = false, gradient = false }) {
  const colorOf = colorFn(palette, gradient, cmds.length || 1), f = v => +v.toFixed(2);
  const main = Math.max(1, Math.trunc(lineWidth * 2)) / 2, glowW = Math.max(3, Math.trunc(lineWidth * 6)) / 2;
  const parts = [`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">`,
    `<rect width="100%" height="100%" fill="${palette.background}"/>`];
  const layer = (isGlow, width) => {
    parts.push(`<g fill="none" stroke-width="${width}">`);
    let run = null, d = '';
    const flush = () => { if (d) parts.push(`<path stroke="${run}" d="${d}"/>`); d = ''; };
    cmds.forEach((k, c, xy, o, i) => {
      if (isGlow && k === 2) return;
      let col = colorOf(i, c);
      if (isGlow) { const [r, g, b] = hexToRgb(col); col = `rgb(${r >> 2},${g >> 2},${b >> 2})`; }
      if (col !== run) { flush(); run = col; }
      if (k === 0) d += `M${f(xy[o])} ${f(xy[o + 1])}L${f(xy[o + 2])} ${f(xy[o + 3])}`;
      else if (k === 1) {
        const r = Math.max(0, xy[o + 2] + (isGlow ? 1 : 0) - width / 2);
        d += `M${f(xy[o] - r)} ${f(xy[o + 1])}a${f(r)} ${f(r)} 0 1 0 ${f(2 * r)} 0a${f(r)} ${f(r)} 0 1 0 ${f(-2 * r)} 0`;
      } else {
        for (let j = 0; j < xy[o]; j++) d += `${j ? 'L' : 'M'}${f(xy[o + 1 + 2 * j])} ${f(xy[o + 2 + 2 * j])}`;
        d += 'Z';
      }
    });
    flush();
    parts.push('</g>');
  };
  if (glow) layer(true, glowW);
  layer(false, main);
  parts.push('</svg>');
  return parts.join('\n');
}
