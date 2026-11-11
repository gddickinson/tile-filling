// Home page: hero with a live pattern that changes every few seconds, counts from the API, entry cards.
import { route, api, app, esc, list, onLeave } from './core.js';
import { loadSetup, thumb } from './data.js';

const DOORS = [
  ['#/studio', 'Studio', 'The full app: every pattern, palette, line and effect setting of the desktop control panel, presets, PNG / hi-res / SVG export, random batch.'],
  ['#/gallery', 'Gallery', 'All 22 pattern types at their default settings, drawn live in any palette. Click one to open it in the studio.'],
  ['#/palettes', 'Palettes', 'The 12 colour palettes of rendering/colors.py with their colours, each shown on four patterns.'],
  ['#/check', 'Cross-check', 'The browser engine against the Python generators: every pattern computed both ways and compared number by number.'],
  ['#/about', 'About', 'How the patterns and the renderer work, what the web version covers, how to run the desktop and web apps.'],
];
// README gallery pairings (pattern, palette) for the rotating hero
const HERO = [['Truchet Tiles', 'Cyberpunk'], ['Islamic Star', 'Gold'], ['Penrose Tiling', 'Ocean'], ['Spirograph', 'Neon'],
  ['Phyllotaxis', 'Sunset'], ['3D Wireframe', 'Cyberpunk'], ['Voronoi', 'Arctic'], ['Space-Filling Curves', 'Cyberpunk']];

route('home', async () => {
  const [info, setup] = await Promise.all([api('/info'), loadSetup()]);
  const byName = Object.fromEntries(setup.patterns.map(p => [p.name, p]));
  app().innerHTML = `
  <section class="hero two heroart">
    <div>
      <p class="kicker">Tilings · curves · fractals · 3D wireframes</p>
      <h1 class="glow">Tile Filling Visualizer</h1>
      <p class="lead">Mathematical and geometric line art: Truchet tiles, Penrose tilings, space-filling curves, strange
      attractors, L-systems, Chladni figures and more, with colour palettes and post-processing effects. This is the web
      version of the Python desktop app; the patterns are generated right here in your browser.</p>
      <a class="btn" href="#/studio">Open the studio</a><a class="btn alt" href="#/gallery">Browse the patterns</a>
    </div>
    <figure class="fig"><canvas id="hero" width="520" height="520" role="img" aria-label="A generated pattern"></canvas>
      <figcaption class="small mute" id="herocap"></figcaption></figure>
  </section>
  <div class="tiles">
    <div class="tile"><b>${info.patterns}</b><span>pattern types</span></div>
    <div class="tile"><b>${info.palettes}</b><span>colour palettes</span></div>
    <div class="tile"><b>${info.effects}</b><span>post-processing effects</span></div>
    <div class="tile"><b>${info.categories.length}</b><span>families</span></div>
  </div>
  <div class="grid wide">${list(DOORS, ([href, t, d]) => `<a class="card door" href="${href}"><b>${t}</b><span>${d}</span></a>`)}</div>
  ${list(info.categories, c => `<h2>${esc(c.name)}</h2><p>${list(setup.patterns.filter(p => p.category === c.name),
    p => `<a class="tag a" href="#/studio?p=${p.slug}" title="${esc(p.description)}">${esc(p.name)}</a>`)}</p>`)}`;

  const canvas = document.getElementById('hero'), cap = document.getElementById('herocap');
  let i = 0, timer = 0;
  const show = () => {
    const [name, pal] = HERO[i % HERO.length];
    const n = thumb(canvas, byName[name], setup.palettes[pal], { size: 520, glow: true });
    cap.innerHTML = `<a href="#/studio?p=${byName[name].slug}&pal=${encodeURIComponent(pal)}">${esc(name)}</a>, ${esc(pal)} palette, default settings: ${n.toLocaleString('en')} drawing commands`;
    i++;
  };
  show();
  if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    timer = setInterval(show, 4000);
    onLeave(() => clearInterval(timer));
  }
});
