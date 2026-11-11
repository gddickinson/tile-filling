// Node test: the JS pattern engine reproduces the Python generators (patterns/*.py) command for command.
// Reference numbers: tests/fixtures/engine_fixture.json, made by `python scripts/make_engine_fixture.py`
// (tests/test_web.py checks that file is current). Run: node web/static/engine.test.mjs
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { GENERATORS, generate, stats } from './engine.js';
import { LSYSTEM_PRESETS } from './pat_curves2.js';
import { attractorOrbit } from './pat_curves.js';
import { gradientColor, lerpColor } from './pyutil.js';
import { random } from './pyrandom.js';

const FIX = JSON.parse(readFileSync(new URL('../../tests/fixtures/engine_fixture.json', import.meta.url)));
const close = (a, b, tol, what) => assert.ok(Math.abs(a - b) <= tol * Math.max(1, Math.abs(b)), `${what}: js ${a} vs py ${b}`);
let checks = 0;

// registry, palettes helpers, L-system presets
assert.deepEqual(Object.keys(GENERATORS), FIX.registry, 'registry names and order'); checks++;
for (const [name, t, hex] of FIX.gradient) { assert.equal(gradientColor(FIX.palettes[name], t), hex, `gradient ${name} ${t}`); checks++; }
for (const [a, b, t, hex] of FIX.lerp) { assert.equal(lerpColor(a, b, t), hex, `lerp ${a} ${b} ${t}`); checks++; }
assert.deepEqual(LSYSTEM_PRESETS, FIX.lsystem_presets, 'L-system presets'); checks++;

// every pattern at its defaults plus variants covering every mode
const kinds = { line: 0, circle: 1, polygon: 2 };
let compared = 0;
for (const c of FIX.cases) {
  const label = `${c.name} ${JSON.stringify(c.params)}`;
  if (c.global_seed !== null) random.seed(c.global_seed);
  const cmds = generate(c.name, c.width, c.height, c.params);
  const s = stats(cmds), py = c.stats;
  assert.equal(s.count, py.count, `${label}: command count`);
  assert.equal(s.lines, py.lines, `${label}: lines`); assert.equal(s.circles, py.circles, `${label}: circles`);
  assert.equal(s.polygons, py.polygons, `${label}: polygons`); assert.equal(s.fills, py.fills, `${label}: filled polygons`);
  close(s.weights, py.weights, 1e-12, `${label}: line weights`);
  assert.deepEqual(Object.fromEntries(Object.entries(s.colors).map(([k, v]) => [String(k), v])), py.colors, `${label}: colour indices`);
  const list = cmds.toList();
  if (c.chaotic) {
    // chaotic maps amplify last-digit differences between libm builds: compare the start of the orbit and the extent
    const p = c.params, [xs, ys] = attractorOrbit(p.attractor, p.a, p.b, p.c, p.d, c.orbit.length);
    c.orbit.forEach(([x, y], i) => { close(xs[i], x, 1e-9, `${label}: orbit x${i}`); close(ys[i], y, 1e-9, `${label}: orbit y${i}`); });
    s.bbox.forEach((v, j) => close(v, py.bbox[j], 0.05, `${label}: bbox[${j}]`));
  } else {
    close(s.sum, py.sum, 1e-9, `${label}: coordinate sum`);
    assert.equal(s.bbox === null, py.bbox === null, `${label}: empty`);
    (s.bbox || []).forEach((v, j) => close(v, py.bbox[j], 1e-9, `${label}: bbox[${j}]`));
    for (const [i, kind, data, col, ...extra] of c.samples) {
      assert.equal(cmds.kind[i], kinds[kind], `${label}: cmd ${i} kind`); assert.equal(list[i][2], col, `${label}: cmd ${i} colour`);
      assert.deepEqual(list[i].slice(3), extra, `${label}: cmd ${i} weight/fill`);
      data.flat().forEach((v, j) => close(list[i][1].flat()[j], v, 1e-9, `${label}: cmd ${i}[${j}]`));
      compared++;
    }
  }
  checks++;
}
console.log(`engine: ${checks} checks passed (${FIX.cases.length} pattern cases, ${compared} sampled commands, ` +
  `${FIX.gradient.length} gradient colours)`);
