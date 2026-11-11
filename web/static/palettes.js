// Palettes: the 12 palettes of rendering/colors.py, their colours, and four patterns drawn in each.
import { route, app, esc, list, onLeave } from './core.js';
import { loadSetup, thumb, swatches } from './data.js';

const SHOW = ['Truchet Tiles', 'Spirograph', 'Hexagonal', 'Flow Field'];

route('palettes', async () => {
  const { patterns, palettes } = await loadSetup();
  const byName = Object.fromEntries(patterns.map(p => [p.name, p]));
  app().innerHTML = `<p class="kicker">Palettes</p><h1 class="glow">${Object.keys(palettes).length} colour palettes</h1>
  <p class="lead">Each palette (<code>rendering/colors.py</code>) has a background, a list of line colours and an accent.
  A pattern gives every drawing command a colour index; the renderer cycles through the line colours by index, or, with
  <b>Gradient Colors</b> on, blends through them along the command list.</p>
  ${list(Object.entries(palettes), ([name, p]) => `<div class="palrow"><div><h3>${esc(name)}</h3><div class="sw">${swatches(p)}</div>
    <p class="small mono mute">bg ${esc(p.background)}<br>lines ${p.lines.map(esc).join(' ')}<br>accent ${esc(p.accent)}</p></div>
    <div class="thumbs">${list(SHOW, s => `<a href="#/studio?p=${byName[s].slug}&pal=${encodeURIComponent(name)}"><canvas data-pal="${esc(name)}" data-pat="${esc(s)}" width="220" height="220" role="img" aria-label="${esc(s)} in ${esc(name)}"></canvas></a>`)}</div></div>`)}`;
  let alive = true;
  onLeave(() => { alive = false; });
  const cs = [...document.querySelectorAll('canvas[data-pal]')];
  let k = 0;
  const next = () => {
    if (!alive || k >= cs.length) return;
    const c = cs[k++];
    thumb(c, byName[c.dataset.pat], palettes[c.dataset.pal], { size: 220, params: c.dataset.pat === 'Flow Field' ? { particles: 250 } : {} });
    setTimeout(next, 0);
  };
  next();
});
