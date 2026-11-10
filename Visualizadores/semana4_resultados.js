// Resultados de Python sobre la interfaz y el renderizador del visualizador E07/E08.
const RUN = DATA.resultado_python;
const SUMMARY = RUN.resumen;

function decodeFloat32(encoded, expected) {
  const binary = atob(encoded);
  if (binary.length !== expected * 4) throw Error('Campo térmico incompleto.');
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < bytes.length; i++) bytes[i] = binary.charCodeAt(i);
  const view = new DataView(bytes.buffer);
  const values = new Float32Array(expected);
  for (let i = 0; i < expected; i++) values[i] = view.getFloat32(i * 4, true);
  return values;
}

function historyAt(time) {
  const rows = RUN.historia;
  let lo = 0, hi = rows.length - 1;
  while (hi - lo > 1) {
    const mid = (lo + hi) >> 1;
    if (rows[mid].tiempo_h <= time) lo = mid;
    else hi = mid;
  }
  if (time >= rows[hi].tiempo_h) lo = hi;
  const a = rows[lo], b = rows[hi];
  const f = lo === hi ? 0 : (time - a.tiempo_h) / (b.tiempo_h - a.tiempo_h);
  const row = {...a};
  for (const key of Object.keys(a)) {
    if (key === 'voxeles_activos' || key === 'tiempo_h') continue;
    row[key] = Number.isFinite(a[key]) && Number.isFinite(b[key])
      ? a[key] + f * (b[key] - a[key]) : a[key];
  }
  return row;
}

let thermalDense = null;
let pythonS25 = null;

function refreshThermalFrame() {
  thermalDense = null;
  pythonS25 = null;
  const r = state.thermal, g = grid();
  if (!r || state.time < 0 || state.time > r.p.horizon) return;
  const special = state.pythonSpecial && r.specials[state.pythonSpecial];
  if (special) {
    thermalDense = new Float32Array(g.ids.length).fill(NaN);
    pythonS25 = new Float32Array(g.ids.length).fill(NaN);
    for (let n = 0; n < r.N; n++) {
      thermalDense[r.indices[n]] = special.values[n];
      pythonS25[r.indices[n]] = special.s25[n];
    }
    return;
  }
  let lo = 0, hi = r.times.length - 1;
  while (hi - lo > 1) {
    const mid = (lo + hi) >> 1;
    if (r.times[mid] <= state.time) lo = mid;
    else hi = mid;
  }
  if (state.time >= r.times[hi]) lo = hi;
  const f = lo === hi ? 0 : (state.time - r.times[lo]) / (r.times[hi] - r.times[lo]);
  thermalDense = new Float32Array(g.ids.length).fill(NaN);
  for (let n = 0; n < r.N; n++) {
    const flat = r.indices[n], id = g.ids[flat];
    if (state.time < DATA.vertidas.find(v => v.id === id).inicio) continue;
    const a = r.fields[lo * r.N + n], b = r.fields[hi * r.N + n];
    thermalDense[flat] = Number.isFinite(a) && Number.isFinite(b)
      ? a + f * (b - a) : Number.isFinite(a) ? a : NaN;
  }
}

function sourceDensity(id, time) {
  const pour = DATA.vertidas.find(v => v.id === id);
  if (!pour || time < pour.inicio) return 0;
  return RUN.fuente.q0_W_m3 * Math.exp(-(time - pour.inicio) / RUN.fuente.tau_h);
}

function thermalColor(temperature) {
  if (!Number.isFinite(temperature)) return [.78, .81, .77];
  const scale = state.thermal.scale;
  const f = Math.max(0, Math.min(1, (temperature - scale[0]) / Math.max(.01, scale[1] - scale[0])));
  return f < .5 ? [.14 + f * .5, .35 + f, .82 - f * .45]
    : [.39 + (f - .5) * 1.18, .85 - (f - .5) * 1.35, .595 - (f - .5) * 1.05];
}

function cellThermalTerms(flat) {
  if (!thermalDense || !Number.isFinite(thermalDense[flat])) return null;
  return {T: thermalDense[flat], s25: pythonS25 ? pythonS25[flat] : null};
}

function selectPythonField(name) {
  stopPlay();
  state.pythonSpecial = name;
  state.time = state.thermal.specials[name].time;
  $('time').value = state.time;
  state.temporal = true;
  $('construction').checked = true;
  $('viewMode').value = 'temperature';
  setTab('geometry');
  update(true);
}

function renderThermalCards() {
  const r = state.thermal, maxima = new Map(), row = historyAt(Math.max(0, state.time));
  const special = state.pythonSpecial && r.specials[state.pythonSpecial];
  const metrics = special ? special.metrics : row;
  const current = thermalDense !== null;
  if (current) for (const flat of r.indices) {
    const t = thermalDense[flat], id = grid().ids[flat];
    if (Number.isFinite(t)) maxima.set(id, Math.max(maxima.get(id) ?? -Infinity, t));
  }
  $('tempMax').innerHTML = current ? fmt(metrics.Tmax_C) + ' <span>°C</span>' : '—';
  $('tempMin').innerHTML = current ? fmt(metrics.Tmin_S25_C) + ' <span>°C</span>' : '—';
  $('tempPeak').innerHTML = fmt(SUMMARY.Tmax.valor) + ' <span>°C</span>';
  $('tempTrough').innerHTML = fmt(SUMMARY.DeltaTmax.valor) + ' <span>K</span>';
  $('tempNowNote').textContent = current ? 'Diagnóstico de Python · t = ' + fmt(state.time) + ' h' : 'Hormigón pendiente de colocación';
  $('tempMinNote').textContent = 'Mínimo a 25 mm bajo las caras exteriores';
  $('tempPeakNote').textContent = 't = ' + fmt(SUMMARY.Tmax.tiempo_h) + ' h · límite 70 °C';
  $('tempTroughNote').textContent = 't = ' + fmt(SUMMARY.DeltaTmax.tiempo_h) + ' h · límite 20 K';
  $('pythonFrame').textContent = special
    ? 'Campo guardado en Python · ' + state.pythonSpecial + ' · estado ' + special.phase
    : 'Colores interpolados entre campos guardados · diagnósticos interpolados entre pasos de Python';
  $('pythonAirNow').textContent = 'Aire ' + fmt(row.aire_C) + ' °C · suelo ' + fmt(RUN.entorno.suelo_C) + ' °C';
  renderPourTemperatures(maxima);
  renderLayerStatus();
}

function renderPourTemperatures(currentMax) {
  $('pourTemperatureRows').innerHTML = DATA.vertidas.map(v => {
    const p = RUN.picos_vertidas.find(p => p.id === v.id), now = currentMax.get(v.id);
    return '<tr><td>' + dot(v.id) + v.nombre + '</td><td>'
      + (Number.isFinite(now) ? fmt(now) : state.time < v.inicio ? 'No colocada' : '—')
      + '</td><td>' + (p.value === null ? '—' : fmt(p.value))
      + '</td><td>' + (p.t === null ? '—' : fmt(p.t))
      + '</td><td>' + (p.t === null ? '—' : fmt(p.t - v.inicio)) + '</td></tr>';
  }).join('');
}

function renderLayerStatus() {
  const layers = RUN.entorno.capas_laterales;
  $('layerRows').innerHTML = DATA.vertidas.map(v => {
    const age = state.time - v.inicio;
    const states = layers.map((layer, index) => {
      const retired = layer.retiro_edad_h !== null && age >= layer.retiro_edad_h;
      const before = state.pythonSpecial && state.thermal.specials[state.pythonSpecial].phase === 'previo';
      const active = age >= 0 && (!retired || (before && Math.abs(age - layer.retiro_edad_h) < 1e-7));
      const label = age < 0 ? 'Pendiente' : active ? 'Presente' : 'Retirada';
      return '<td>' + label + ' · R ' + fmt(active ? layer.espesor_m / layer.k_W_mK : 0, 3) + '</td>';
    }).join('');
    return '<tr><td>' + dot(v.id) + v.nombre + '</td><td>' + (age < 0 ? '—' : fmt(age)) + '</td>' + states + '</tr>';
  }).join('');
}

function boundaryColorPython(axis, sign, z, id) {
  const g = grid(), e = RUN.entorno;
  if (axis === 2 && sign === -1 && Math.abs(g.origen[2] + z * g.h - e.plano_suelo_z_m) < 1e-7) return '#916d41';
  if (axis < 2) {
    const age = state.time - DATA.vertidas.find(v => v.id === id).inicio;
    const before = state.pythonSpecial && state.thermal.specials[state.pythonSpecial].phase === 'previo';
    const present = e.capas_laterales.filter(c => c.retiro_edad_h === null
      || age < c.retiro_edad_h || (before && Math.abs(age - c.retiro_edad_h) < 1e-7));
    if (present.length) return '#469b87';
  }
  return '#9873bd';
}

function drawThermalCharts() {
  const rows = RUN.historia, horizon = SUMMARY.horizonte_h;
  const options = label => ({
    ylabel: label, xmax: horizon,
    xticks: [0, .25, .5, .75, 1].map(f => [f * horizon, fmt(f * horizon, 0) + ' h']),
    cursor: state.time
  });
  const line = (key, label, color, factor = 1) => ({
    label, color, points: rows.map(row => [row.tiempo_h, row[key] === null ? null : row[key] * factor])
  });
  const limit = (value, label) => ({label, color:'#a84032', points:[[0,value],[horizon,value]]});
  $('temperatureChart').innerHTML = chart([
    line('Tmax_C','Máxima','#b44a36'), line('nucleo_C','Núcleo','#23806b'),
    line('Tmin_S25_C','Mínimo S25','#3677b0'), limit(70,'Límite 70')
  ], options('Temperatura [°C]'));
  $('observerChart').innerHTML = chart([
    line('aire_C','Aire','#177c7a'),
    {label:'Suelo',color:'#916d41',points:[[0,RUN.entorno.suelo_C],[horizon,RUN.entorno.suelo_C]]}
  ], options('Temperatura del entorno [°C]'));
  $('deltaChart').innerHTML = chart([
    line('DeltaT_K','Tmax − Tmin S25','#7960a9'), limit(20,'Límite 20')
  ], options('Diferencial [K]'));
  $('rateChart').innerHTML = chart([
    line('conduccion_nucleo_K_h','Vecinos','#4383ad'),
    line('borde_nucleo_K_h','Bordes','#9873bd'),
    line('fuente_nucleo_K_h','Hidratación','#c48928')
  ], options('Tasas en la sonda interior [K/h]'));
  $('powerChart').innerHTML = chart([
    line('fuente_W','Hidratación','#c48928',.001),
    line('aire_W','Aire','#177c7a',.001),
    line('suelo_W','Suelo','#916d41',.001)
  ], options('Potencia entrante [kW]'));
  const b = SUMMARY.balance_J;
  $('thermalBalance').textContent = int(SUMMARY.pasos) + ' pasos · energía de hidratación '
    + fmt(b.hidratacion / 1e9, 3) + ' GJ · aire ' + fmt(b.aire / 1e9, 3)
    + ' GJ · suelo ' + fmt(b.suelo / 1e9, 3) + ' GJ · residuo ' + b.residuo.toExponential(3) + ' J.';
}

function initializePythonResult() {
  const g = grid(), indices = new Int32Array(g.ocupados);
  let n = 0;
  for (let flat = 0; flat < g.ids.length; flat++) if (g.ids[flat]) indices[n++] = flat;
  if (n !== RUN.numero_voxeles) throw Error('Los resultados no corresponden a la grilla.');
  const specials = {};
  for (const [name, field] of Object.entries(RUN.especiales)) {
    specials[name] = {
      ...field, values:decodeFloat32(field.values, n), s25:decodeFloat32(field.s25, n)
    };
  }
  state.thermal = {
    gridIndex:0, N:n, indices, times:RUN.tiempos_h,
    fields:decodeFloat32(RUN.temperaturas, n * RUN.tiempos_h.length),
    specials, scale:[RUN.minimo.valor, SUMMARY.Tmax.valor],
    p:{horizon:SUMMARY.horizonte_h}, peak:{value:SUMMARY.Tmax.valor, t:SUMMARY.Tmax.tiempo_h}
  };
  state.settings = {q:RUN.fuente.q0_W_m3};
  state.temporal = true;
  $('construction').checked = true;
  $('construction').disabled = true;
  $('time').max = SUMMARY.horizonte_h;
  $('viewMode').value = 'temperature';
  $('peakPython').onclick = () => selectPythonField('pico');
  $('deltaPython').onclick = () => selectPythonField('diferencial');
  $('finalPython').onclick = () => selectPythonField('final');
  $('openThermal').onclick = () => setTab('heat');
  $('downloadParameters').onclick = () => {
    const url = URL.createObjectURL(new Blob([
      JSON.stringify(SUMMARY.parametros_efectivos,null,2)
    ], {type:'application/json'}));
    const a = document.createElement('a');
    a.href = url;
    a.download = 'parametros-' + SUMMARY.caso + '.json';
    a.click();
    setTimeout(() => URL.revokeObjectURL(url),1000);
  };
  $('showBoundaries').onclick = () => {
    $('viewMode').value = 'bc';
    setTab('geometry');
    rebuildMesh();
    drawSlice();
  };
  $('probeMarkers').onchange = () => {rebuildMesh();drawSlice();};
  state.pythonSpecial = 'pico';
  state.time = SUMMARY.Tmax.tiempo_h;
  $('time').value = state.time;
}

