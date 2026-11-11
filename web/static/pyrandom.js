// Python's `random` module in JS: the MT19937 generator with CPython's seeding, random(), getrandbits(), randint().
// The pattern generators call random.seed(seed) on Python's global generator (Truchet, Voronoi, Isometric Cubes,
// Flow Field, Reaction-Diffusion), so this port gives the browser the same tiles, points and seeds as the desktop app.
const N = 624, M = 397;

export class PyRandom {
  constructor(seed) {
    this.mt = new Uint32Array(N);
    this.mti = N + 1;
    this.seed(seed === undefined ? Math.floor(Math.random() * 2 ** 32) : seed);
  }

  initGenrand(s) {
    const mt = this.mt;
    mt[0] = s >>> 0;
    for (let i = 1; i < N; i++) {
      const prev = mt[i - 1] ^ (mt[i - 1] >>> 30);
      mt[i] = (Math.imul(1812433253, prev) + i) >>> 0;
    }
    this.mti = N;
  }

  initByArray(key) {
    const mt = this.mt;
    this.initGenrand(19650218);
    let i = 1, j = 0;
    for (let k = Math.max(N, key.length); k; k--) {
      const prev = mt[i - 1] ^ (mt[i - 1] >>> 30);
      mt[i] = ((mt[i] ^ Math.imul(prev, 1664525)) + key[j] + j) >>> 0;
      i++; j++;
      if (i >= N) { mt[0] = mt[N - 1]; i = 1; }
      if (j >= key.length) j = 0;
    }
    for (let k = N - 1; k; k--) {
      const prev = mt[i - 1] ^ (mt[i - 1] >>> 30);
      mt[i] = ((mt[i] ^ Math.imul(prev, 1566083941)) - i) >>> 0;
      i++;
      if (i >= N) { mt[0] = mt[N - 1]; i = 1; }
    }
    mt[0] = 0x80000000;
  }

  // random.seed(n) for an int n: the absolute value split into 32-bit words (little-endian) feeds init_by_array.
  seed(n) {
    let v = Math.abs(Math.trunc(n));
    const key = [];
    do { key.push(v % 4294967296); v = Math.floor(v / 4294967296); } while (v > 0);
    this.initByArray(key);
  }

  genrand() {
    const mt = this.mt;
    if (this.mti >= N) {
      let kk = 0, y;
      for (; kk < N - M; kk++) {
        y = (mt[kk] & 0x80000000) | (mt[kk + 1] & 0x7fffffff);
        mt[kk] = mt[kk + M] ^ (y >>> 1) ^ (y & 1 ? 0x9908b0df : 0);
      }
      for (; kk < N - 1; kk++) {
        y = (mt[kk] & 0x80000000) | (mt[kk + 1] & 0x7fffffff);
        mt[kk] = mt[kk + (M - N)] ^ (y >>> 1) ^ (y & 1 ? 0x9908b0df : 0);
      }
      y = (mt[N - 1] & 0x80000000) | (mt[0] & 0x7fffffff);
      mt[N - 1] = mt[M - 1] ^ (y >>> 1) ^ (y & 1 ? 0x9908b0df : 0);
      this.mti = 0;
    }
    let y = mt[this.mti++];
    y ^= y >>> 11;
    y ^= (y << 7) & 0x9d2c5680;
    y ^= (y << 15) & 0xefc60000;
    y ^= y >>> 18;
    return y >>> 0;
  }

  // random.random(): 53-bit float from two 32-bit draws.
  random() {
    const a = this.genrand() >>> 5, b = this.genrand() >>> 6;
    return (a * 67108864 + b) / 9007199254740992;
  }

  getrandbits(k) { return k <= 0 ? 0 : this.genrand() >>> (32 - k); } // k <= 32 is all the patterns need

  randbelow(n) {
    const k = 32 - Math.clz32(n);
    let r = this.getrandbits(k);
    while (r >= n) r = this.getrandbits(k);
    return r;
  }

  randint(a, b) { return a + this.randbelow(b - a + 1); }

  choice(seq) { return seq[this.randbelow(seq.length)]; }
}

// Python's module-level generator: patterns seed it, Grid jitter, the film-grain effect and Randomize draw from it.
export const random = new PyRandom();
