// Studio files: PNG / hi-res PNG / SVG export, presets in the desktop JSON format, the 10x random batch, and (local app
// only) the same settings drawn by the Python renderer.
import { download, esc } from './core.js';
import { generate, randomParams } from './engine.js';
import { renderToCanvas, renderHighRes, scaled, toSVG } from './render.js';
import { random } from './pyrandom.js';
import { renderOpts } from './studio.js';

const fileName = (S, ext) => `${S.pattern.slug}_${S.palette.toLowerCase().replace(/\s+/g, '-')}.${ext}`;
const toBlob = c => (c.convertToBlob ? c.convertToBlob({ type: 'image/png' }) : new Promise(r => c.toBlob(r, 'image/png')));

// "Export PNG": the image on screen.
export function exportPNG({ S, art, status }) {
  art.toBlob(b => { download(fileName(S, 'png'), b); status.textContent = `Exported ${fileName(S, 'png')}`; }, 'image/png');
}

// "Export Hi-Res PNG": the pattern regenerated, drawn at 4x size and 4x line width without supersampling. The 300 DPI
// tag of the desktop export is not written (browsers save PNGs without a pHYs chunk).
export async function exportHiRes({ S, setup, status }, gen) {
  const k = setup.spec.hires_scale;
  status.textContent = `Rendering hi-res (${k}x)...`;
  const { cmds } = await gen.run(S.pattern.name, S.width, S.height, { ...S.params });
  const c = renderHighRes(scaled(cmds, k), S.width, S.height, renderOpts(S, setup.palettes, setup.spec), k);
  download(fileName(S, 'png').replace('.png', `_${k}x.png`), await toBlob(c));
  status.textContent = `Hi-res exported (${S.width * k} x ${S.height * k})`;
}

// SVG (web addition): the line and circle commands as vector paths; raster effects are not included.
export function exportSVG({ S, setup, status, get }) {
  const cur = get();
  if (!cur) return;
  download(fileName(S, 'svg'), toSVG(cur.cmds, cur.width, cur.height, renderOpts(S, setup.palettes, setup.spec)), 'image/svg+xml');
  status.textContent = `Exported ${fileName(S, 'svg')} (vector lines${S.kaleidoscope >= 2 || S.gauss_glow || S.vignette || S.chromatic || S.scanlines || S.grain ? '; effects are raster-only and left out' : ''})`;
}

// "Save Preset": {"pattern", "params", "settings"} exactly as TileFillingApp._save_preset writes it.
export function savePreset({ S, setup, status }) {
  const settings = { palette: S.palette, line_width: S.line_width, glow: S.glow, gradient: S.gradient, kaleidoscope: S.kaleidoscope };
  for (const t of setup.spec.effects) settings[t.key] = S[t.key];
  const preset = { pattern: S.pattern.name, params: S.params, settings };
  download(`${S.pattern.slug}_preset.json`, JSON.stringify(preset, null, 2), 'application/json');
  status.textContent = 'Preset saved (download)';
}

// "Load Preset": desktop preset files work here and presets saved here load in the desktop app.
export async function loadPresetFile({ setup, status }, file, applyState) {
  try {
    const p = JSON.parse(await file.text());
    const pattern = setup.patterns.find(x => x.name === (p.pattern || 'Grid'));
    // numbers clamped to the slider range, as the desktop app does, so presets from older versions stay valid
    const params = { ...(p.params || {}) };
    for (const d of pattern.params) {
      if ((d.type === 'int' || d.type === 'float') && typeof params[d.name] === 'number') params[d.name] = Math.min(Math.max(params[d.name], d.min), d.max);
    }
    applyState({ pattern, params, settings: p.settings || {} });
    status.textContent = `Loaded preset: ${file.name}`;
  } catch (e) {
    status.textContent = `Could not read preset: ${e.message}`;
  }
}

// "Batch Random (10x)": random parameters and palette, line width 1, no effects (as _batch_export), shown as a grid.
export async function batch({ S, setup, extra, status }) {
  const n = setup.spec.batch_count, names = Object.keys(setup.palettes);
  extra.innerHTML = `<h2>Batch: ${n} random ${esc(S.pattern.name)} variations</h2>
    <p class="small mute">Random parameters and palette, line width 1, no effects, like the desktop batch export. Click an image to save it.</p>
    <div class="batch" id="batch"></div>`;
  const host = document.getElementById('batch');
  for (let i = 0; i < n; i++) {
    status.textContent = `Batch rendering ${i + 1}/${n}...`;
    await new Promise(r => setTimeout(r, 0));
    const params = randomParams(S.pattern.params), pal = random.choice(names);
    const cmds = generate(S.pattern.name, S.width, S.height, params);
    const c = renderToCanvas(cmds, S.width, S.height, { palette: setup.palettes[pal], lineWidth: 1, supersample: setup.spec.supersample });
    const url = URL.createObjectURL(await toBlob(c));
    const name = `${S.pattern.name}_${String(i).padStart(2, '0')}.png`;
    host.insertAdjacentHTML('beforeend', `<a class="card" href="${url}" download="${esc(name)}"><img src="${url}" alt="${esc(S.pattern.name)} variation ${i + 1}, ${esc(pal)} palette"><small>${esc(name)} · ${esc(pal)}</small></a>`);
  }
  status.textContent = `Batch rendered ${n} images`;
}

// Local app only: POST the same settings to /api/render and show the PNG from rendering/renderer.py.
export async function pythonRender({ S, setup, extra, status }) {
  status.textContent = 'Rendering with Python (Pillow)...';
  const settings = { palette: S.palette, line_width: S.line_width, glow: S.glow, gradient: S.gradient, kaleidoscope: S.kaleidoscope };
  for (const t of setup.spec.effects) settings[t.key] = S[t.key];
  const r = await fetch('api/render', { method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pattern: S.pattern.name, params: S.params, settings, width: S.width, height: S.height }) });
  if (!r.ok) { status.textContent = `Python render failed: ${r.status}`; return; }
  const url = URL.createObjectURL(await r.blob());
  extra.innerHTML = `<h2>Drawn by the desktop renderer</h2><p class="small mute">rendering/renderer.py (Pillow) with the same
    pattern, parameters and settings: ${esc(r.headers.get('X-Commands') || '?')} commands. Seeded patterns match the browser exactly;
    Grid jitter and film grain use unseeded randomness, so they differ from run to run.</p>
    <figure class="fig"><img src="${url}" alt="The same pattern rendered by Python"></figure>`;
  status.textContent = 'Python render done';
}
