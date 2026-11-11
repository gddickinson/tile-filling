// Web worker: runs a pattern generator off the main thread and sends the command arrays back (transferred).
import { generate } from './engine.js';

self.onmessage = e => {
  const { id, name, width, height, params } = e.data;
  try {
    const t0 = performance.now();
    const c = generate(name, width, height, params);
    const kind = Uint8Array.from(c.kind), col = Int32Array.from(c.col), xy = Float64Array.from(c.xy), ex = Float64Array.from(c.ex);
    self.postMessage({ id, kind, col, xy, ex, ms: performance.now() - t0 }, [kind.buffer, col.buffer, xy.buffer, ex.buffer]);
  } catch (err) {
    self.postMessage({ id, error: String(err && err.message || err) });
  }
};
