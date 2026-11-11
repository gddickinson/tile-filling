// Node test: each post-processing effect in effects.js gives the same pixels as rendering/effects.py (Pillow) on a
// 48x36 test image. Reference: tests/fixtures/effects_fixture.json (python scripts/make_engine_fixture.py).
// Run: node web/static/effects.test.mjs
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { chromatic, gaussianGlow, grain, kaleidoscope, scanLines, vignette } from './effects.js';

const FIX = JSON.parse(readFileSync(new URL('../../tests/fixtures/effects_fixture.json', import.meta.url)));
const { width: w, height: h, strengths: S } = FIX;
const rgb = b64 => new Uint8Array(Buffer.from(b64, 'base64'));
const toImg = bytes => {
  const data = new Uint8ClampedArray(w * h * 4);
  for (let i = 0; i < w * h; i++) { data[4 * i] = bytes[3 * i]; data[4 * i + 1] = bytes[3 * i + 1]; data[4 * i + 2] = bytes[3 * i + 2]; data[4 * i + 3] = 255; }
  return { width: w, height: h, data };
};
const input = toImg(rgb(FIX.input));
const RUN = {
  kaleidoscope6: () => kaleidoscope(input, 6), kaleidoscope5: () => kaleidoscope(input, 5),
  gauss_glow: () => gaussianGlow(input, S.gauss_glow), vignette: () => vignette(input, S.vignette),
  chromatic: () => chromatic(input, S.chromatic), scanlines: () => scanLines(input, S.scanlines),
  grain_seed11: () => grain(input, { ...S.grain, seed: 11 }),
};
let pixels = 0;
const mismatches = [];
for (const [name, b64] of Object.entries(FIX.results)) {
  const want = rgb(b64), got = RUN[name]().data;
  let bad = 0, first = -1;
  for (let i = 0; i < w * h; i++) {
    for (let c = 0; c < 3; c++) if (got[4 * i + c] !== want[3 * i + c]) { bad++; if (first < 0) first = i; }
  }
  // kaleidoscope: int() of r*cos/sin can land on the other side of a whole pixel when libm and V8 differ in the
  // last bit, so a handful of source pixels may differ; everything else must be identical
  const allowed = name.startsWith('kaleidoscope') ? Math.ceil(0.01 * w * h * 3) : 0;
  if (bad) mismatches.push(`${name} ${bad}`);
  assert.ok(bad <= allowed, `${name}: ${bad} channel values differ (first at pixel ${first}: js ${got.slice(4 * first, 4 * first + 3)} vs py ${want.slice(3 * first, 3 * first + 3)})`);
  pixels += w * h;
}
console.log(`effects: ${Object.keys(FIX.results).length} effects match Pillow (${pixels} pixels; differing channel values: ${mismatches.join(', ') || 'none'})`);
