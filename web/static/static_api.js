// Static-site data layer: answers api() calls from the JSON files exported by scripts/build_static.py
// (pattern list, palettes, render settings and the Python cross-check numbers). Rendering with Python
// (POST /api/render) needs the local server; the studio hides that button on the static site.
const files = new Map();
async function file(rel) {
  if (!files.has(rel)) files.set(rel, fetch('api/' + rel + '.json').then(r => { if (!r.ok) throw new Error(`${r.status} ${rel}`); return r.json(); }));
  return files.get(rel);
}

export async function staticApi(path, body) {
  if (body) throw new Error('This needs the local app (Python server).');
  return file(path.split('?')[0].replace(/^\/+/, ''));
}
