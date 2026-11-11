// About: what the app does (from the README and the code), the pattern list with the generators' own descriptions,
// the renderer and effects, the desktop shortcuts, how to run both apps, credits.
import { route, app, api, esc, list } from './core.js';
import { loadSetup } from './data.js';

const KEYS = [['Space', 'Randomize all parameters (and the palette)'], ['R', 'Regenerate'], ['E', 'Export PNG'],
  ['S', 'Save preset'], ['L', 'Load preset']];

route('about', async () => {
  const [info, { patterns, palettes, spec }] = await Promise.all([api('/info'), loadSetup()]);
  const st = spec.effect_strengths;
  app().innerHTML = `<p class="kicker">About</p><h1 class="glow">How it works</h1>
  <p class="lead">The Tile Filling Visualizer is a Python (tkinter + Pillow) application for generating mathematical and
  geometric art: ${info.patterns} pattern types, ${info.palettes} colour palettes, 3D wireframe surfaces, post-processing
  effects and real-time parameter control with presets. This site is its web version:
  <a href="https://github.com/gddickinson/tile-filling">gddickinson/tile-filling</a>.</p>

  <h2>Patterns are drawing commands</h2>
  <p>Every pattern is a class in <code>patterns/</code> with <code>get_params()</code> (the slider definitions: name, label,
  type, range, default) and <code>generate(width, height, params, margin=${spec.margin})</code>, which returns a list of drawing
  commands: lines, circles and polygons, each with a colour index. The renderer turns the list into an image.</p>
  <div class="scroll"><table><tr><th>Pattern</th><th>Family</th><th>What the code says</th><th>Sliders</th></tr>
  ${list(patterns, p => `<tr><td><a href="#/studio?p=${p.slug}">${esc(p.name)}</a><br><span class="small mute mono">${esc(p.module)}</span></td>
    <td>${esc(p.category)}</td><td>${esc(p.description)}. <span class="mute">${esc(p.doc)}</span></td>
    <td class="small">${list(p.params, d => esc(d.label), ', ')}</td></tr>`)}</table></div>

  <h2>The renderer</h2>
  <ul>
    <li>Fill the palette background, then draw every command in its palette colour (colour index modulo the number of line
    colours) or, with <b>Gradient Colors</b>, in a colour blended along the command list.</li>
    <li>Everything is drawn at ${spec.supersample}x size and scaled down (anti-aliasing). Line width ${spec.line_width.min} to
    ${spec.line_width.max}; <b>Glow Effect</b> first draws each line three times as wide in a quarter of its colour.</li>
    <li>Post-processing, in this order: kaleidoscope (2 to ${spec.kaleidoscope.max} mirrored wedges), Gaussian bloom
    (blur radius ${st.gauss_glow.radius}, brightened by ${st.gauss_glow.intensity}, screen-blended), vignette (strength
    ${st.vignette.strength}), chromatic aberration (red and blue shifted ${st.chromatic.offset} px), scan lines (every
    ${st.scanlines.spacing}rd row at ${Math.round(100 * (1 - st.scanlines.opacity))}% brightness) and film grain (noise of
    ±${st.grain.amount}).</li>
    <li>Export: PNG of the canvas, hi-res PNG (${spec.hires_scale}x size and line width; the desktop file is tagged
    ${spec.hires_dpi} DPI), a batch of ${spec.batch_count} random variations, and presets as JSON
    (<code>{"pattern", "params", "settings"}</code>).</li>
  </ul>

  <h2>What the web version covers</h2>
  <p>All ${patterns.length} generators are ported line by line to JavaScript (<code>web/static/pat_*.js</code>), together with
  Python's <code>random</code> module (Mersenne Twister, seeding, <code>randint</code>) so that seeded patterns come out the
  same, and the renderer and all effects, including Pillow's Gaussian blur and blend arithmetic. The pattern list, slider
  specs, palettes and renderer settings are read from the Python code through the API, not copied. See the
  <a href="#/check">cross-check</a>. Presets are interchangeable with the desktop app. Web additions: SVG export (vector lines,
  no raster effects), a canvas-size field and shareable links to a pattern and palette. The browser cannot write the 300 DPI
  tag into PNGs. On the local web app the studio can also draw the current settings with the Python renderer.</p>

  <h2>Run it yourself</h2>
  <h3>Desktop app (tkinter)</h3>
  <pre>pip install Pillow
python main.py</pre>
  <div class="scroll"><table><tr><th>Key</th><th>Action</th></tr>${list(KEYS, ([k, a]) => `<tr><td class="mono">${k}</td><td>${a}</td></tr>`)}</table></div>
  <p class="small mute">The same keys work in the web studio.</p>
  <h3>Web app (this site, with the Python API)</h3>
  <pre>pip install -r requirements-web.txt
python run_web.py          # http://127.0.0.1:8123</pre>
  <p>The static GitHub Pages site is built by <code>scripts/build_static.py</code>; it needs no server, because the
  patterns are generated in the browser.</p>

  <h2>Credits</h2>
  <p>Tile Filling Visualizer by George Dickinson, MIT licence. ${Object.keys(palettes).length} palettes and all pattern code
  from the repository. Web version built with AI assistance from <a href="https://claude.com/">Claude (Anthropic)</a>.</p>`;
});
