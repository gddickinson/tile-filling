// Gallery: every pattern type at its default parameters, drawn live in the chosen palette.
import { route, app, esc, list, onLeave } from './core.js';
import { loadSetup, thumb, select } from './data.js';

route('gallery', async (args, query) => {
  const { patterns, palettes, spec } = await loadSetup();
  let pal = palettes[query.pal] ? query.pal : 'Cyberpunk', glow = false, token = 0;
  app().innerHTML = `<p class="kicker">Gallery</p><h1 class="glow">All ${patterns.length} pattern types</h1>
  <p class="lead">Each pattern at the default values of its <code>get_params()</code> sliders, generated and drawn in your
  browser. Click a pattern to open it in the studio.</p>
  <div class="row ctlrow" id="gctl"></div>
  <div class="grid gal">${list(patterns, p => `<a class="card" href="#/studio?p=${p.slug}" data-slug="${p.slug}">
    <canvas width="360" height="360" role="img" aria-label="${esc(p.name)} at default settings"></canvas>
    <b>${esc(p.name)}</b><small>${esc(p.category)}</small><span>${esc(p.description)}</span><small class="n"></small></a>`)}</div>`;
  const ctl = document.getElementById('gctl');
  select(ctl, 'gpal', 'Palette', Object.keys(palettes), pal, v => { pal = v; draw(); });
  const g = document.createElement('div'); g.className = 'ctl';
  g.innerHTML = '<label for="gglow"><input type="checkbox" id="gglow"> Glow effect</label>';
  ctl.appendChild(g);
  g.querySelector('input').addEventListener('change', e => { glow = e.target.checked; draw(); });
  onLeave(() => { token++; });

  function draw() {
    const my = ++token;
    const cards = [...document.querySelectorAll('.gal .card')];
    let k = 0;
    const next = () => {
      if (my !== token || k >= cards.length) return;
      const card = cards[k++], p = patterns.find(x => x.slug === card.dataset.slug);
      card.href = `#/studio?p=${p.slug}&pal=${encodeURIComponent(pal)}`;
      const n = thumb(card.querySelector('canvas'), p, palettes[pal], { size: 360, glow });
      card.querySelector('.n').textContent = `${n.toLocaleString('en')} commands`;
      setTimeout(next, 0);
    };
    next();
  }
  draw();
});
