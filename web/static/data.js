// Shared page data and helpers: the pattern list, palettes and render settings from the Python code (via api()),
// a worker-backed generator, and small UI builders.
import { api, esc } from './core.js';
import { Commands } from './pyutil.js';
import { generate } from './engine.js';
import { renderToCanvas } from './render.js';

export async function loadSetup() {
  const [patterns, palettes, spec] = await Promise.all([api('/patterns'), api('/palettes'), api('/render-spec')]);
  const bySlug = Object.fromEntries(patterns.map(p => [p.slug, p]));
  return { patterns, palettes, spec, bySlug };
}

const fromArrays = ({ kind, col, xy }) => Object.assign(new Commands(), { kind, col, xy });

// Generator in a module worker; a new request supersedes (terminates) a running one so sliders stay responsive.
export class Generator {
  constructor() { this.seq = 0; this.worker = null; this.pending = null; }
  run(name, width, height, params) {
    if (typeof Worker === 'undefined') return Promise.resolve({ cmds: generate(name, width, height, params), ms: 0 });
    if (this.pending) { this.worker.terminate(); this.worker = null; this.pending.reject(new Error('superseded')); this.pending = null; }
    if (!this.worker) this.worker = new Worker(new URL('./engine_worker.js', import.meta.url), { type: 'module' });
    const id = ++this.seq;
    return new Promise((resolve, reject) => {
      this.pending = { reject };
      this.worker.onmessage = e => {
        if (e.data.id !== id) return;
        this.pending = null;
        if (e.data.error) reject(new Error(e.data.error));
        else resolve({ cmds: fromArrays(e.data), ms: e.data.ms });
      };
      this.worker.onerror = e => { this.pending = null; reject(new Error(e.message || 'worker failed')); };
      this.worker.postMessage({ id, name, width, height, params });
    });
  }
  stop() { if (this.worker) this.worker.terminate(); this.worker = null; this.pending = null; }
}

// Draw a pattern at its defaults (or given params) into a visible <canvas> (gallery thumbnails, hero, palettes).
export function thumb(canvas, pattern, palette, { params = {}, size = 400, lineWidth = 1, glow = false } = {}) {
  const p = Object.fromEntries(pattern.params.map(d => [d.name, d.default]));
  const cmds = generate(pattern.name, size, size, { ...p, ...params });
  const img = renderToCanvas(cmds, size, size, { palette, lineWidth, glow, supersample: 2 });
  canvas.width = size; canvas.height = size;
  canvas.getContext('2d').drawImage(img, 0, 0);
  return cmds.length;
}

// Labelled <select>; options are [value, label] pairs or strings.
export function select(host, id, label, options, value, cb) {
  const wrap = document.createElement('div');
  wrap.className = 'ctl';
  const opts = options.map(o => (Array.isArray(o) ? o : [o, o]));
  wrap.innerHTML = `<label for="${id}">${esc(label)}</label><select id="${id}">${opts.map(([v, l]) =>
    `<option value="${esc(v)}" ${String(v) === String(value) ? 'selected' : ''}>${esc(l)}</option>`).join('')}</select>`;
  host.appendChild(wrap);
  const el = wrap.querySelector('select');
  el.addEventListener('change', () => cb(el.value));
  return el;
}

export function checkbox(host, id, label, value, cb) {
  const wrap = document.createElement('div');
  wrap.className = 'ctl chk';
  wrap.innerHTML = `<label for="${id}"><input type="checkbox" id="${id}" ${value ? 'checked' : ''}> ${esc(label)}</label>`;
  host.appendChild(wrap);
  const el = wrap.querySelector('input');
  el.addEventListener('change', () => cb(el.checked));
  return el;
}

export const swatches = pal => [pal.background, ...pal.lines, pal.accent]
  .map((c, i) => `<i style="background:${c}" title="${i ? '' : 'background '}${c}"></i>`).join('');
