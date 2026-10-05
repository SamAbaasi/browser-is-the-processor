// Minimal reproduction: the exact frozen P1 microkernels (p1-triple-v6.wasm),
// G = compiler-autovectorized SIMD128, D = i32x4.dot_i16x8_s, P = i16x8.mul + i32x4.extadd_pairwise_i16x8_s.
importScripts("./p1-triple-v6.js");
const NS = [2560, 3200, 6912, 8192];
const ORDERS = [["generic","dot","pairwise","pairwise","dot","generic"],
                ["dot","pairwise","generic","generic","pairwise","dot"],
                ["pairwise","generic","dot","dot","generic","pairwise"]];
const FN = { generic: "p1_measure_generic_ms", dot: "p1_measure_dot_ms", pairwise: "p1_measure_pairwise_ms" };
const median = xs => { const a=[...xs].sort((x,y)=>x-y), m=a.length>>1; return a.length%2 ? a[m] : (a[m-1]+a[m])/2; };
self.onmessage = async (ev) => {
  const { cycles = 4, targetMs = 150, rounds = 5 } = ev.data || {};
  const mod = await createP1TripleV6({ locateFile: p => "./" + p });
  const verify = Object.fromEntries(NS.map(n => [n, mod.ccall("p1_verify", "number", ["number"], [n])]));
  postMessage({ type: "verify", verify });
  const samples = Object.fromEntries(NS.map(n => [n, { generic: [], dot: [], pairwise: [] }]));
  for (let c = 0; c < cycles; c++) {
    for (const n of NS) {
      for (const k of ORDERS[c % ORDERS.length]) {
        samples[n][k].push(mod.ccall(FN[k], "number", ["number","number","number"], [n, targetMs, rounds]));
      }
    }
    postMessage({ type: "progress", cycle: c + 1, cycles });
  }
  const rows = NS.map(n => { const g=median(samples[n].generic), d=median(samples[n].dot), p=median(samples[n].pairwise);
    return { n, generic_ms: g, dot_ms: d, pairwise_ms: p, D_over_G_speedup: g/d, P_over_G_speedup: g/p, P_over_D_speedup: d/p }; });
  const gm = k => Math.exp(rows.reduce((s,r)=>s+Math.log(r[k]),0)/rows.length);
  postMessage({ type: "done", userAgent: navigator.userAgent, hardwareConcurrency: navigator.hardwareConcurrency,
    params: { cycles, targetMs, rounds }, verify, rows, samples,
    geomean: { D_over_G: gm("D_over_G_speedup"), P_over_G: gm("P_over_G_speedup"), P_over_D: gm("P_over_D_speedup") } });
};
