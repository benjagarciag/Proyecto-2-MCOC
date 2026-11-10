/* node desarrollo/tests/test_semana4_html.cjs ruta/visualizador.html */
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync(process.argv[2], 'utf8');
const match = html.match(/<script id="e07-data" type="application\/json">([\s\S]*?)<\/script>/);
assert(match, 'Datos incorporados');
const data = JSON.parse(match[1]);
const script = html.match(/<script>\s*([\s\S]*?)<\/script>/)[1];
new vm.Script(script);
assert(!script.includes('solveVoxelHeat'), 'La página debe visualizar resultados de Python');
assert(!script.includes('new Worker'), 'La física se ejecuta en Python');
const nodes = new Map();
const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(m => m[1]);
const noop = () => {};
const canvas2d = new Proxy({}, {get:(obj,key) => key in obj ? obj[key] : noop});
const gl = new Proxy({}, {get:(obj,key) => {
  if (key in obj) return obj[key];
  if (/^[A-Z_]+$/.test(key)) return 1;
  if (['createShader','createProgram','createBuffer'].includes(key)) return () => ({});
  if (['getShaderParameter','getProgramParameter'].includes(key)) return () => true;
  if (key === 'getAttribLocation') return () => 0;
  return noop;
}});
function node(id) {
  assert(ids.includes(id), 'Elemento requerido ausente: ' + id);
  if (!nodes.has(id)) nodes.set(id, {
    id, style:{}, value:'', checked:false, hidden:false, innerHTML:'', textContent:'',
    classList:{toggle:noop,add:noop,remove:noop},
    parentElement:{}, setAttribute:noop, addEventListener:noop,
    querySelectorAll:() => [], getBoundingClientRect:() => ({width:900,height:420,left:0,top:0}),
    getContext:type => type === 'webgl' ? gl : canvas2d,
    click:noop
  });
  return nodes.get(id);
}
node('e07-data').textContent = match[1];
node('clipAxis').value = 'none';
node('slicePlane').value = 'XZ';
node('probeMarkers').checked = true;
const frames = [];
const context = vm.createContext({
  document:{getElementById:node,querySelectorAll:() => [],createElement:() => ({click:noop})},
  window:{addEventListener:noop}, console, Float32Array, Int32Array, Uint8Array, DataView,
  Set, Map, Math, Number, Array, JSON, Error,
  atob:text => Buffer.from(text,'base64').toString('binary'),
  requestAnimationFrame:fn => {frames.push(fn);return frames.length;},
  cancelAnimationFrame:noop, ResizeObserver:class {observe(){}},
  devicePixelRatio:1, performance:{now:() => 0},
  URL:{createObjectURL:() => 'blob:test',revokeObjectURL:noop},Blob,setTimeout:noop
});
vm.runInContext(script,context);
const evaluate = code => vm.runInContext(code,context);
for (let i = 0; i < 4 && frames.length; i++) frames.shift()(0);
const run = data.resultados_python[data.grilla_inicial], summary = run.resumen;
assert.equal(evaluate('state.thermal.N'), run.numero_voxeles);
assert.equal(evaluate('state.time'), summary.Tmax.tiempo_h);
assert.equal(evaluate('state.pythonSpecial'), 'pico');
assert(node('tempPeak').innerHTML.includes(summary.Tmax.valor.toLocaleString('es-CL',{minimumFractionDigits:2,maximumFractionDigits:2})));
const expected = Buffer.from(run.especiales.pico.values,'base64');
for (let n = 0; n < run.numero_voxeles; n += 137) {
  const actual = evaluate('thermalDense[state.thermal.indices[' + n + ']]');
  const original = expected.readFloatLE(n*4);
  assert(Number.isNaN(original) ? Number.isNaN(actual) : actual === original);
}
evaluate("selectPythonField('diferencial')");
assert.equal(evaluate('state.time'),summary.DeltaTmax.tiempo_h);
assert.equal(evaluate('state.pythonSpecial'),'diferencial');
assert.equal(evaluate('state.thermal.specials.diferencial.metrics.Tmin_S25_C'),summary.DeltaTmax.Tmin_S25_C);
const fullCount = evaluate('draws.tri');
evaluate("$('clipAxis').value='0'; setupClip(); state.clipIndex=4; rebuildMesh()");
assert(evaluate('draws.tri') < fullCount, 'El clipping reduce la malla visible');
evaluate("$('slicePlane').value='XY'; setupSlice(); drawSlice()");
evaluate("setTime(0)");
assert.equal(evaluate('state.pythonSpecial'),null);
assert.equal(evaluate('Number.isFinite(thermalDense[state.thermal.indices.find(flat=>grid().ids[flat]===2)] )'),false);
evaluate("setTime(6)");
assert.equal(evaluate('thermalDense[state.thermal.indices.find(flat=>grid().ids[flat]===2)]'),18);
evaluate("setTime(71.5); renderLayerStatus()");
assert(node('layerRows').innerHTML.includes('Presente'));
evaluate("setTime(120); renderLayerStatus()");
assert(node('layerRows').innerHTML.includes('Retirada'));
evaluate("setTime(30); state.playing=false; $('play').onclick()");
const tick = frames.pop();
tick(100000);
assert(evaluate('state.time') <= summary.horizonte_h,'La reproducción respeta el horizonte');
evaluate("stopPlay(); setTab('heat')");
for (const id of ['temperatureChart','observerChart','deltaChart','rateChart','powerChart']) {
  assert(node(id).innerHTML.includes('<svg'),id);
}
evaluate("$('viewMode').value='bc';setTime(0);rebuildMesh()");
assert.equal(evaluate('boundaryColorPython(2,-1,0,1)'),'#916d41');
assert.equal(evaluate('boundaryColorPython(0,1,0,1)'),'#469b87');
evaluate("setTime(120)");
assert.equal(evaluate('boundaryColorPython(0,1,0,1)'),'#9873bd');
console.log('OK HTML Python: arranque, campos, extremos, activación, cortes, clipping, reproducción, curvas y capas.');

