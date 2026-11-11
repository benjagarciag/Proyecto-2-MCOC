/* DOM real. Instalar jsdom como dependencia de pruebas o en .venv/cache/html-dom. */
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const assert = require('node:assert/strict');
let domLibrary;
try { domLibrary = require('jsdom'); }
catch { domLibrary = require(path.resolve('.venv/cache/html-dom/node_modules/jsdom')); }
const {JSDOM, VirtualConsole} = domLibrary;
const filename = path.resolve(process.argv[2]);
const source = fs.readFileSync(filename, 'utf8');
const errors = [];
const messages = new VirtualConsole();
messages.on('jsdomError', error => errors.push(error.message));
const context2d = new Proxy({}, {get:(object,key) => key in object ? object[key] : () => {}});
const dom = new JSDOM(source, {
  url:pathToFileURL(filename).href, runScripts:'dangerously', virtualConsole:messages,
  beforeParse(window) {
    window.ResizeObserver = class {observe(){}};
    window.requestAnimationFrame = () => 1;
    window.cancelAnimationFrame = () => {};
    window.HTMLCanvasElement.prototype.getContext = type => type === 'webgl' ? null : context2d;
  }
});
const window = dom.window, document = window.document;
const value = expression => window.eval(expression);
const visibleSections = () => [...document.querySelectorAll('.tab-panel')].filter(section => !section.hidden).map(section => section.id);
function checkTabs() {
  for (const link of document.querySelectorAll('[data-tab]')) {
    assert.equal(link.getAttribute('href'), '#' + link.dataset.tab);
    link.click();
    assert.deepEqual(visibleSections(), [link.dataset.tab]);
    assert.equal(document.getElementById('overviewPython').hidden, link.dataset.tab !== 'geometry');
    assert.equal(window.location.hash, '#' + link.dataset.tab);
  }
}
assert.deepEqual(visibleSections(), ['geometry'], 'Solo la sección inicial debe estar visible');
checkTabs();
const options = [...document.querySelectorAll('[data-grid]')];
assert.deepEqual(options.map(button => button.textContent.trim()), ['1,0 m','0,5 m','0,25 m']);
options[2].click();
assert.equal(value('grid().h'), .25);
assert.equal(value('state.thermal.N'), 40536);
assert.equal(value('SUMMARY.lado_m'), .25);
assert.equal(value('state.thermal.gridIndex'), 2);
checkTabs();
document.querySelector('[data-tab="heat"]').click();
document.getElementById('deltaPython').click();
assert.equal(value('state.pythonSpecial'), 'diferencial');
assert.equal(value('state.time'), value('SUMMARY.DeltaTmax.tiempo_h'));
assert.deepEqual(visibleSections(), ['geometry']);
options[0].click();
assert.equal(value('grid().h'), 1);
assert.equal(value('state.thermal'), null);
assert.equal(document.getElementById('tempPeak').textContent, '—');
assert(document.getElementById('pourTemperatureRows').textContent.includes('Sin voxeles'));
checkTabs();
document.querySelector('[data-tab="heat"]').click();
assert(document.getElementById('heat').textContent.includes('V02'));
options[1].click();
assert.equal(value('state.thermal.N'), 5140);
assert.equal(value('SUMMARY.lado_m'), .5);
checkTabs();
document.querySelector('[data-tab="heat"]').click();
assert(document.getElementById('heat').textContent.includes('Robin conductiva equivalente'));
assert(document.getElementById('heat').textContent.includes('Datos meteorológicos usados'));
assert(document.querySelectorAll('.run-facts').length > 0);
assert(document.querySelectorAll('math').length >= 10);
for (const math of document.querySelectorAll('math')) {
  assert.equal(math.namespaceURI,'http://www.w3.org/1998/Math/MathML');
}
for (const description of document.querySelectorAll('.chart-description')) {
  assert(description.querySelectorAll('br').length <= 1, 'Máximo dos líneas de explicación');
}
value("globalThis.recordedCharts=[];globalThis.originalChart=chart;chart=(series,opt)=>{recordedCharts.push(series);return originalChart(series,opt);};drawThermalCharts()");
const actual = value("recordedCharts.find(series=>series[0].label==='Hidratación de la corrida')[0].points");
const active = actual.find(([time,q]) => q > 0);
assert(Math.abs(active[1]-value('RUN.fuente.q0_W_m3'))<1e-8);
const afterTau = actual.find(([time])=>Math.abs(time-active[0]-value('RUN.fuente.tau_h'))<1e-8);
assert(Math.abs(afterTau[1]-active[1]*Math.exp(-1))<1e-8);
const beforeReference = value('JSON.stringify(RUN.resumen)');
const reference = document.getElementById('cosineReference');
reference.checked = true;
reference.dispatchEvent(new window.Event('change',{bubbles:true}));
const sourceSeries = value("recordedCharts.filter(series=>series[0].label==='Hidratación de la corrida').at(-1)");
assert.equal(sourceSeries.length,2);
const peakRef = sourceSeries[1].points.find(([time])=>Math.abs(time-active[0]-6)<1e-8);
assert(Math.abs(peakRef[1]-active[1])<1e-8);
assert.equal(value('JSON.stringify(RUN.resumen)'),beforeReference);
assert.equal(document.querySelectorAll('#sourceChart .chart-legend-item').length,2);
for (const frame of document.querySelectorAll('.chart-frame')) {
  assert(frame.querySelector('.chart-legend'));
  assert.equal(frame.querySelectorAll('svg .chart-legend').length,0);
}
assert.deepEqual(errors, [], 'La navegación, los gráficos y los cambios de malla no deben producir errores de JavaScript');
console.log('OK DOM real: cinco secciones, enlaces, visibilidad, cambios 0,50/0,25/1 m y separación de resultados.');
window.close();
