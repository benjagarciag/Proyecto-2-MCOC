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
assert.deepEqual(errors, [], 'La navegación y los cambios de malla no deben producir errores de JavaScript');
console.log('OK DOM real: cinco secciones, enlaces, visibilidad, cambios 0,50/0,25/1 m y separación de resultados.');
window.close();

