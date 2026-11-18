// Construye la presentación F02 (8 principales + índice + B01–B12).
// Datos: recursos/datos.json (generado por preparar_recursos.py, sin simular).
// Las animaciones y ecuaciones OMML se inyectan después con postproceso.py,
// que lee recursos/animaciones.json y recursos/ecuaciones.json.
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const AQUI = __dirname;
const RAIZ = path.resolve(AQUI, "../../..");
const REC = path.join(AQUI, "recursos");
const D = JSON.parse(fs.readFileSync(path.join(REC, "datos.json"), "utf-8"));
const SALIDA = process.argv[2] || path.join(AQUI, "F02_Grupo6_base.pptx");

// ------------------------------------------------------------------ paleta
const K = {
  marfil: "F5F3EE", carbon: "202B33", noche: "13202A", noche2: "1D2E3A",
  petroleo: "166C65", petroleoClaro: "5FB3A8", rojo: "B54830", azul: "1B74AA",
  violeta: "743E99", ocre: "C99A2E", madera: "B8864F", gris: "6B7780",
  grisClaro: "D9D5CC", grisMedio: "9AA3A9", hormigon: "C5CACD", blanco: "FFFFFF",
  tenue: "8C979E", rejilla: "E2DED6",
};
const F = "Segoe UI";
const FS = "Segoe UI Semibold";
const W = 13.333, H = 7.5;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Benjamín García, Luis Noriega, Matías Stierling";
pres.title = "F02 Grupo 6 — Colocación de la fundación El Rosal";
pres.theme = { headFontFace: FS, bodyFontFace: F };

pres.defineSlideMaster({
  title: "CLARO", background: { color: K.marfil },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.32, w: 12.1, h: 0.8,
    fontFace: FS, fontSize: 30, color: K.carbon, valign: "middle", margin: 0 }, text: "" } }],
  slideNumber: { x: 12.35, y: 7.02, w: 0.6, h: 0.3, fontFace: F, fontSize: 11, color: K.tenue, align: "right" },
});
pres.defineSlideMaster({
  title: "OSCURO", background: { color: K.noche },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.32, w: 12.1, h: 0.8,
    fontFace: FS, fontSize: 30, color: K.blanco, valign: "middle", margin: 0 }, text: "" } }],
});
pres.defineSlideMaster({
  title: "CONSULTA", background: { color: K.marfil },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: 1.55, y: 0.32, w: 10.4, h: 0.8,
    fontFace: FS, fontSize: 28, color: K.carbon, valign: "middle", margin: 0 }, text: "" } }],
  slideNumber: { x: 12.35, y: 7.02, w: 0.6, h: 0.3, fontFace: F, fontSize: 11, color: K.tenue, align: "right" },
});

// ------------------------------------------------------------------ ayudas
const ANIM = {};       // índice de diapositiva (1-based) -> [[{n, fx, d, t}]]
const EQ = {};         // nombre de objeto -> {tex, size, color}
const TRANS = {};      // índice -> "fade" | "morph"
let nSlide = 0;

function nueva(master, seccion) {
  if (seccion) pres.addSection({ title: seccion });
  const s = pres.addSlide({ masterName: master, sectionTitle: seccion ? seccion : undefined });
  nSlide += 1;
  s._n = nSlide;
  TRANS[nSlide] = "fade";
  return s;
}
let seccionActual = null;
function slideEn(master, seccion) {
  if (seccion !== seccionActual) { pres.addSection({ title: seccion }); seccionActual = seccion; }
  const s = pres.addSlide({ masterName: master, sectionTitle: seccion });
  nSlide += 1; s._n = nSlide; TRANS[nSlide] = "fade";
  return s;
}
function clics(s, grupos) { ANIM[s._n] = grupos; }
function T(s, text, o) {
  const base = { fontFace: F, fontSize: 18, color: K.carbon, margin: 0, isTextBox: true, valign: "top" };
  s.addText(text, Object.assign(base, o));
}
function R(s, o, forma) {
  s.addShape(forma || pres.shapes.RECTANGLE, Object.assign({ line: { type: "none" } }, o));
}
function linea(s, x1, y1, x2, y2, o) {  // solo horizontales/verticales
  s.addShape(pres.shapes.LINE, Object.assign({ x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1),
    line: { color: K.carbon, width: 1.5 } }, o));
}
function ecuacion(s, nombre, tex, o) {
  // Texto lineal visible como respaldo; postproceso.py lo reemplaza por OMML.
  EQ[nombre] = { tex, size: o.fontSize || 28, color: o.color || K.carbon, align: o.align || "left" };
  T(s, o.respaldo || nombre, Object.assign({}, o, { objectName: nombre, fontFace: "Cambria Math", valign: "middle" }));
}
function etiqueta(s, texto, x, y, o) {
  // Rótulo discreto: resultado calculado / supuesto del modelo / condición de ejecución
  const color = { R: K.petroleo, S: K.ocre, C: K.azul }[o.tipo];
  const nombre = { R: "RESULTADO CALCULADO", S: "SUPUESTO DEL MODELO", C: "CONDICIÓN DE EJECUCIÓN" }[o.tipo];
  T(s, [{ text: nombre + "  ", options: { bold: true, color, fontSize: 11, charSpacing: 1 } },
        { text: texto, options: { color: o.colorTexto || K.gris, fontSize: o.fontSize || 14 } }],
    { x, y, w: o.w || 6, h: o.h || 0.3, objectName: o.objectName, valign: "middle" });
}
function pie(s, texto, oscuro) {
  T(s, texto, { x: 0.6, y: 7.02, w: 9.5, h: 0.3, fontSize: 11, color: oscuro ? K.grisMedio : K.tenue });
}
function notas(s, o) {
  const partes = [];
  if (o.quien) partes.push(`${o.quien}`);
  if (o.habla) partes.push(`DIÁLOGO:\n${o.habla}`);
  if (o.clics) partes.push(`CLICS:\n${o.clics}`);
  if (o.fuente) partes.push(`FUENTE: ${o.fuente}`);
  if (o.cuidado) partes.push(`CUIDADO: ${o.cuidado}`);
  s.addNotes(partes.join("\n\n"));
}
// Sección y = 0 de la fundación (capas reales del modelo, x de la máscara 0,40 m)
function seccion(s, o) {
  const { x0, yb, sx, sz } = o;  // x0: pulgadas donde x=-9 m; yb: base; sx/sz: pulg/m
  const cmap = ["CFE8D9", "B9DEC9", "A1D3BE", "86C6B4", "6CB8AC", "52A8A4", "3C969C", "2C8293", "236E86", "1F5A78", "1C476A"];
  D.seccion.forEach((c, i) => {
    const fill = o.colores === "capas" ? cmap[i] : (o.colores || K.hormigon);
    R(s, { x: x0 + (c.x0 + 9) * sx, y: yb - c.z1 * sz, w: (c.x1 - c.x0) * sx, h: (c.z1 - c.z0) * sz,
      fill: { color: fill }, line: o.borde ? { color: o.borde, width: 0.75 } : { type: "none" },
      objectName: o.prefijo ? `${o.prefijo}${i + 1}` : undefined });
  });
}
const X = (o, xm) => o.x0 + (xm + 9) * o.sx;
const Z = (o, zm) => o.yb - zm * o.sz;

// Configuración común de gráficos
function ejes(extra) {
  return Object.assign({
    catAxisLabelColor: "4A5660", valAxisLabelColor: "4A5660", catAxisLabelFontSize: 14, valAxisLabelFontSize: 14,
    catAxisLabelFontFace: F, valAxisLabelFontFace: F, catAxisTitleFontFace: F, valAxisTitleFontFace: F,
    catAxisTitleFontSize: 14, valAxisTitleFontSize: 14, catAxisTitleColor: "4A5660", valAxisTitleColor: "4A5660",
    valGridLine: { color: K.rejilla, size: 0.75 }, catGridLine: { style: "none" },
    catAxisLineColor: "9AA3A9", valAxisLineShow: false, showLegend: false,
    lineDataSymbol: "none", lineSize: 2.25, plotArea: { fill: { color: K.marfil } },
  }, extra);
}
// Serie de dispersión con huecos: postproceso.py elimina los puntos vacíos.
function scatterData(seriesXY) {
  // seriesXY: [{name, x:[], y:[]}] -> formato pptxgenjs (X compartido)
  const xs = [];
  const filas = [];
  seriesXY.forEach((s, k) => s.x.forEach((xv, i) => { xs.push(xv); filas.push([k, s.y[i]]); }));
  const out = [{ name: "X", values: xs }];
  seriesXY.forEach((s, k) => out.push({ name: s.name, values: filas.map(f => (f[0] === k ? f[1] : null)) }));
  return out;
}

const fmt = (v, d) => Number(v).toLocaleString("es-CL", { minimumFractionDigits: d, maximumFractionDigits: d });
const P = Object.fromEntries(D.planes.map(r => [`${r.plan}_${r.lado_m}_${r.horizonte_h}`, r]));

// =================================================================== S1
{
  const s = slideEn("OSCURO", "Recorrido oral");
  s.addImage({ path: path.join(REC, "iso_oscura.png"), x: 0.35, y: 1.25, w: 7.6, h: 7.6 * 642 / 1056, objectName: "s1_geo" });
  // escala aproximada
  linea(s, 0.9, 6.25, 7.4, 6.25, { line: { color: K.grisMedio, width: 1, beginArrowType: "none" } });
  T(s, "≈ 18 m · vista del modelo voxelizado 0,40 m, vertical exagerada", { x: 0.9, y: 6.33, w: 7, h: 0.3, fontSize: 12, color: K.grisMedio });
  T(s, "FUNDACIÓN EÓLICA · EL ROSAL · GRUPO 6", { x: 8.35, y: 1.0, w: 4.95, h: 0.35, fontSize: 13, bold: true, color: K.petroleoClaro, charSpacing: 1 });
  T(s, [{ text: "10,61", options: { fontSize: 88, fontFace: FS, color: K.blanco } },
        { text: " h", options: { fontSize: 40, color: K.blanco } }],
    { x: 8.3, y: 1.45, w: 4.8, h: 1.45, objectName: "s1_D", valign: "middle" });
  T(s, "de colocación continua", { x: 8.35, y: 2.85, w: 4.6, h: 0.45, fontSize: 22, color: K.grisClaro, objectName: "s1_D2" });
  T(s, "60 m³/h · 12 °C · 9 circuitos idealizados", { x: 8.35, y: 3.4, w: 4.8, h: 0.45, fontSize: 20, color: K.petroleoClaro, objectName: "s1_rec" });
  R(s, { x: 8.35, y: 4.25, w: 4.4, h: 0.012, fill: { color: "3A4B57" }, objectName: "s1_sep" });
  T(s, [{ text: "0 / 24", options: { fontSize: 44, fontFace: FS, color: K.blanco, breakLine: true } },
        { text: "escenarios exceden los límites en el modelo", options: { fontSize: 17, color: K.grisClaro } }],
    { x: 8.35, y: 4.4, w: 4.9, h: 1.2, objectName: "s1_res", valign: "top" });
  T(s, "Tmax ≤ 70 °C  ·  ΔTmax ≤ 20 K  ·  meta P_f ≤ 5 %", { x: 8.35, y: 5.7, w: 4.95, h: 0.4, fontSize: 15, color: K.grisMedio, objectName: "s1_lim" });
  T(s, "Benjamín García · Luis Noriega · Matías Stierling   —   Proyecto 2 · Métodos Computacionales en IOC · Defensa F02 · 19-11-2026",
    { x: 0.6, y: 6.95, w: 12.2, h: 0.35, fontSize: 13, color: K.grisMedio });
  clics(s, [
    [{ n: "s1_D", fx: "fade", t: 400 }, { n: "s1_D2", fx: "fade", d: 150 }, { n: "s1_rec", fx: "fade", d: 300 }],
    [{ n: "s1_sep", fx: "wipeL", t: 300 }, { n: "s1_res", fx: "fade", d: 100 }, { n: "s1_lim", fx: "fade", d: 300 }],
  ]);
  notas(s, { quien: "S1 · Benjamín · 0:00–0:30 (30 s)",
    habla: "Proponemos colocar toda la fundación de El Rosal en una operación continua, a sesenta metros cúbicos por hora y doce grados de colocación, con nueve circuitos de refrigeración idealizados. Eso requiere diez coma sesenta y una horas. Evaluamos tanto la temperatura máxima como el diferencial térmico, con límites de setenta y veinte grados. Ninguno de los veinticuatro escenarios de la candidata los excedió. Vamos a explicar las condiciones que permiten sostener esa decisión.",
    clics: "1) 10,61 h y recursos. 2) 0/24 y límites.",
    fuente: "COMPARACION_CIRCUITOS_FINAL.md; geometría: máscara voxelizada 0,40 m del IFC (comparacion_circuitos/q60).",
    cuidado: "0/24 es del catálogo y del modelo; no es seguridad absoluta. Confirmación fina 0,20 m/300 s: 24 pares, 0 excedencias." });
}

// =================================================================== S2
{
  const s = slideEn("CLARO", "Recorrido oral");
  s.addText("El interior y el contorno no se enfrían al mismo ritmo", { placeholder: "title" });
  const g = { x0: 0.95, yb: 5.85, sx: 0.39, sz: 0.39 * 1.6 };
  // suelo
  R(s, { x: 0.6, y: g.yb, w: 7.7, h: 0.42, fill: { color: "D8CDBB" }, objectName: "s2_suelo" });
  seccion(s, Object.assign({ colores: K.hormigon, borde: "E9E6DF" }, g));
  T(s, "esquema conceptual · corte y = 0 · vertical ×1,6", { x: 0.6, y: 6.4, w: 6, h: 0.3, fontSize: 12, color: K.tenue });
  // 1) hidratación
  s.addShape(pres.shapes.OVAL, { x: X(g, -4.2), y: Z(g, 3.5), w: 8.4 * g.sx, h: 2.6 * g.sz, fill: { color: "E58A4E", transparency: 45 }, line: { type: "none" }, objectName: "s2_calor" });
  T(s, "hidratación Q(a)", { x: X(g, -2.6), y: Z(g, 2.35), w: 2.2, h: 0.35, fontSize: 18, bold: true, color: "7A2E16", align: "center", objectName: "s2_calorT" });
  // 2) puntos
  s.addShape(pres.shapes.OVAL, { x: X(g, 0) - 0.13, y: Z(g, 2.6) - 0.13, w: 0.26, h: 0.26, fill: { color: K.rojo }, line: { color: K.blanco, width: 2 }, objectName: "s2_pc" });
  T(s, "T máx, Ω", { x: X(g, 0) + 0.2, y: Z(g, 2.6) - 0.2, w: 1.4, h: 0.4, fontSize: 18, bold: true, color: K.rojo, objectName: "s2_pcT" });
  s.addShape(pres.shapes.OVAL, { x: X(g, -8.85) - 0.11, y: Z(g, 0.6) - 0.11, w: 0.22, h: 0.22, fill: { color: K.azul }, line: { color: K.blanco, width: 2 }, objectName: "s2_ps" });
  T(s, "T mín, S25", { x: X(g, -8.6), y: Z(g, 0.6) + 0.15, w: 1.6, h: 0.35, fontSize: 18, bold: true, color: K.azul, objectName: "s2_psT" });
  // 3) bordes
  R(s, { x: X(g, -9) - 0.13, y: Z(g, 1.2), w: 0.1, h: 1.2 * g.sz, fill: { color: K.madera }, objectName: "s2_madI" });
  R(s, { x: X(g, 9) + 0.03, y: Z(g, 1.2), w: 0.1, h: 1.2 * g.sz, fill: { color: K.madera }, objectName: "s2_madD" });
  R(s, { x: X(g, -3.4), y: Z(g, 4.3) - 0.1, w: 6.8 * g.sx, h: 0.08, fill: { color: K.ocre }, objectName: "s2_manta" });
  T(s, "mantas", { x: X(g, 3.6), y: Z(g, 4.3) - 0.2, w: 1.2, h: 0.3, fontSize: 16, color: "8A6516", bold: true, objectName: "s2_mantaT" });
  T(s, "madera + mantas", { x: 0.6, y: Z(g, 1.2) - 0.36, w: 2.0, h: 0.3, fontSize: 16, color: "8A6516", bold: true, objectName: "s2_maderaT" });
  [[-6.5, 2.4], [6.2, 2.4]].forEach(([xm, zm], i) => {
    s.addShape(pres.shapes.LEFT_RIGHT_ARROW, { x: X(g, xm) - 0.35, y: Z(g, zm) - 0.35, w: 0.7, h: 0.28, rotate: i ? 45 : -45, fill: { color: K.azul, transparency: 25 }, line: { type: "none" }, objectName: `s2_flecha${i}` });
  });
  T(s, "aire y viento · h(t)\nintercambio", { x: X(g, -9), y: Z(g, 3.3) - 0.8, w: 2.4, h: 0.6, fontSize: 16, color: K.azul, objectName: "s2_aireT" });
  T(s, "suelo equivalente 15 °C", { x: X(g, 1.5), y: g.yb + 0.06, w: 3.0, h: 0.3, fontSize: 16, color: "6E5A3A", bold: true, objectName: "s2_sueloT" });
  // derecha: ecuaciones
  T(s, "Balance local", { x: 8.45, y: 1.5, w: 4.4, h: 0.35, fontSize: 16, color: K.tenue, bold: true });
  ecuacion(s, "eq_s2_cons", "\\rho c_p \\frac{\\partial T}{\\partial t} = \\nabla\\cdot(k\\nabla T) + Q(a) - q_{frío}",
    { x: 8.45, y: 1.85, w: 4.6, h: 0.95, fontSize: 20, respaldo: "ρ cp ∂T/∂t = ∇·(k∇T) + Q(a) − q_frío" });
  T(s, "almacena = conduce + genera − extrae", { x: 8.45, y: 2.9, w: 4.4, h: 0.3, fontSize: 14, color: K.tenue });
  R(s, { x: 8.35, y: 3.6, w: 4.75, h: 1.75, fill: { color: "ECE7F1" }, objectName: "s2_caja" }, pres.shapes.ROUNDED_RECTANGLE);
  ecuacion(s, "eq_s2_dT", "\\Delta T(t) = T_{max,\\Omega}(t) - T_{min,S25}(t)",
    { x: 8.45, y: 3.75, w: 4.6, h: 0.9, fontSize: 23, color: K.violeta, respaldo: "ΔT(t) = Tmax,Ω(t) − Tmin,S25(t)" });
  T(s, "mismo instante · S25 ≈ 25 mm dentro del hormigón", { x: 8.5, y: 4.7, w: 4.5, h: 0.5, fontSize: 14, color: K.violeta, objectName: "s2_mismo" });
  clics(s, [
    [{ n: "s2_calor", fx: "fade", t: 400 }, { n: "s2_calorT", fx: "fade", d: 150 }],
    [{ n: "s2_pc", fx: "zoomIn", t: 300 }, { n: "s2_pcT", fx: "fade" }, { n: "s2_ps", fx: "zoomIn", d: 300, t: 300 }, { n: "s2_psT", fx: "fade", d: 300 },
     { n: "s2_caja", fx: "fade", d: 500 }, { n: "eq_s2_dT", fx: "fade", d: 600 }, { n: "s2_mismo", fx: "fade", d: 800 }],
    [{ n: "s2_flecha0", fx: "fade" }, { n: "s2_flecha1", fx: "fade" }, { n: "s2_aireT", fx: "fade" },
     { n: "s2_madI", fx: "wipeU", d: 250 }, { n: "s2_madD", fx: "wipeU", d: 250 }, { n: "s2_manta", fx: "wipeL", d: 250 }, { n: "s2_mantaT", fx: "fade", d: 400 }, { n: "s2_maderaT", fx: "fade", d: 400 },
     { n: "s2_sueloT", fx: "fade", d: 550 }],
  ]);
  notas(s, { quien: "S2 · Benjamín · 0:30–1:25 (55 s)",
    habla: "El problema aparece porque la hidratación genera calor dentro del hormigón, mientras el exterior intercambia energía con el ambiente y el suelo. El interior y la superficie no se enfrían a la misma velocidad. Por eso controlamos dos indicadores distintos: la temperatura máxima y la diferencia entre el punto más caliente y el punto más frío de S veinticinco, al mismo instante. S veinticinco es hormigón aproximadamente veinticinco milímetros bajo las superficies exteriores; no es el suelo. Modelamos convección horaria a partir del viento, suelo equivalente a quince grados y protección con madera y mantas. La aislación reduce el enfriamiento superficial, pero también puede conservar calor en el interior.",
    clics: "1) Hidratación. 2) Punto caliente, punto S25 y la resta ΔT. 3) Bordes: aire/viento, madera + mantas, suelo.",
    fuente: "MODELO_NUEVE_CIRCUITOS.md; sección: capas reales del modelo (y = 0).",
    cuidado: "Los puntos son ilustrativos: el máximo no está siempre en el centro ni el mínimo siempre en la misma cara. Las flechas son intercambio, no siempre extracción. Consulta B02–B05." });
}

// =================================================================== S3
{
  const s = slideEn("CLARO", "Recorrido oral");
  s.addText("Once capas de colocación y nueve circuitos de control", { placeholder: "title" });
  const g = { x0: 1.25, yb: 5.95, sx: 0.34, sz: 0.34 * 1.6 };
  R(s, { x: 1.0, y: g.yb, w: 6.6, h: 0.3, fill: { color: "E3DCCF" } });
  seccion(s, Object.assign({ colores: "capas", borde: "FFFFFF", prefijo: "s3_capa" }, g));
  T(s, "secuencia esquemática · corte y = 0 · vertical ×1,6", { x: 1.0, y: 6.33, w: 6, h: 0.3, fontSize: 12, color: K.tenue });
  T(s, "0 h", { x: 0.45, y: Z(g, 0.4) + 0.02, w: 0.7, h: 0.3, fontSize: 14, color: K.gris, align: "right", objectName: "s3_t0" });
  T(s, "10,61 h", { x: X(g, 3.4) + 0.15, y: Z(g, 4.3) - 0.05, w: 1.2, h: 0.3, fontSize: 14, color: K.gris, bold: true, objectName: "s3_t1" });
  T(s, "2 frentes × 30 m³/h · capas ≤ 0,40 m · sin esperas", { x: 0.6, y: 1.3, w: 7.6, h: 0.35, fontSize: 18, color: K.petroleo, bold: true, objectName: "s3_frentes" });
  // tubos
  const niveles = [[0.5, 3], [1.5, 3], [2.5, 2], [3.8, 1]];
  niveles.forEach(([zm, n], i) => {
    const c = D.seccion.find(c => zm >= c.z0 && zm < c.z1);
    const xa = X(g, c.x0 + 0.5), xb = X(g, c.x1 - 0.5), y = Z(g, zm);
    s.addShape(pres.shapes.LINE, { x: xa, y, w: xb - xa, h: 0, line: { color: "FFFFFF", width: 3.5, dashType: "dash" }, objectName: `s3_tubo${i}` });
    s.addShape(pres.shapes.LINE, { x: xa, y, w: xb - xa, h: 0, line: { color: "39A0E0", width: 3.5 }, objectName: `s3_agua${i}` });
    T(s, `${fmt(zm, 2)} m · ${n}`, { x: X(g, 9) + 0.15, y: y - 0.17, w: 1.4, h: 0.34, fontSize: 16, bold: true, color: K.azul, objectName: `s3_niv${i}` });
  });
  // derecha: cifras
  const cifras = [["9", "ramales en paralelo"], ["18 L/min", "por ramal abierto · 162 con bypass"], ["≤ 15 kW", "tope térmico conjunto"]];
  cifras.forEach(([a, b], i) => {
    T(s, [{ text: a, options: { fontSize: 30, fontFace: FS, color: K.azul } }, { text: "\n" + b, options: { fontSize: 14, color: K.gris } }],
      { x: 9.0, y: 1.3 + i * 0.85, w: 3.9, h: 0.8, objectName: `s3_cifra${i}` });
  });
  // histéresis
  const hx = 9.15, hy = 4.75, hw = 3.4, hh = 1.2;
  const tx = (Tc) => hx + (Tc - 16.5) / (20.5 - 16.5) * hw;
  const grupo = [];
  const add = (nm, fn) => { fn(); grupo.push(nm); };
  add("s3_hx", () => s.addShape(pres.shapes.LINE, { x: hx, y: hy + hh, w: hw, h: 0, line: { color: K.gris, width: 1, endArrowType: "triangle" }, objectName: "s3_hx" }));
  add("s3_band", () => R(s, { x: tx(18), y: hy - 0.05, w: tx(19) - tx(18), h: hh + 0.05, fill: { color: "DCEAF4" }, objectName: "s3_band" }));
  add("s3_h1", () => s.addShape(pres.shapes.LINE, { x: hx + 0.05, y: hy + hh - 0.15, w: tx(19) - hx - 0.05, h: 0, line: { color: K.gris, width: 3 }, objectName: "s3_h1" }));
  add("s3_h2", () => s.addShape(pres.shapes.LINE, { x: tx(19), y: hy + 0.1, w: 0, h: hh - 0.25, line: { color: K.azul, width: 3, beginArrowType: "triangle" }, objectName: "s3_h2" }));
  add("s3_h3", () => s.addShape(pres.shapes.LINE, { x: tx(18), y: hy + 0.1, w: hx + hw - 0.1 - tx(18), h: 0, line: { color: K.azul, width: 3 }, objectName: "s3_h3" }));
  add("s3_h4", () => s.addShape(pres.shapes.LINE, { x: tx(18), y: hy + 0.1, w: 0, h: hh - 0.25, line: { color: K.gris, width: 3, endArrowType: "triangle" }, objectName: "s3_h4" }));
  add("s3_hl1", () => T(s, "abierto", { x: hx + hw - 0.95, y: hy - 0.25, w: 0.95, h: 0.3, fontSize: 13, color: K.azul, align: "right", objectName: "s3_hl1" }));
  add("s3_hl2", () => T(s, "cerrado", { x: hx - 0.05, y: hy + hh - 0.45, w: 0.9, h: 0.3, fontSize: 13, color: K.gris, objectName: "s3_hl2" }));
  add("s3_hl3", () => T(s, "18", { x: tx(18) - 0.3, y: hy + hh + 0.04, w: 0.6, h: 0.3, fontSize: 14, bold: true, color: K.gris, align: "center", objectName: "s3_hl3" }));
  add("s3_hl4", () => T(s, "19 °C", { x: tx(19) - 0.3, y: hy + hh + 0.04, w: 0.9, h: 0.3, fontSize: 14, bold: true, color: K.azul, align: "center", objectName: "s3_hl4" }));
  add("s3_hl5", () => T(s, "abre: cubierto y mínima ≥ 19 °C · cierra: algún tramo ≤ 18 °C", { x: 9.0, y: 6.35, w: 3.9, h: 0.55, fontSize: 13, color: K.carbon, objectName: "s3_hl5" }));
  etiqueta(s, "agua 18 °C ideal", 9.0, 3.9, { tipo: "S", w: 3.9, objectName: "s3_sup" });
  clics(s, [
    [...D.seccion.map((_, i) => ({ n: `s3_capa${i + 1}`, fx: "wipeU", d: i * 150, t: 250 })), { n: "s3_t0", fx: "fade" }, { n: "s3_t1", fx: "fade", d: 1500 }, { n: "s3_frentes", fx: "fade" }],
    [...[0, 1, 2, 3].flatMap(i => [{ n: `s3_tubo${i}`, fx: "fade", d: i * 120 }, { n: `s3_niv${i}`, fx: "fade", d: i * 120 }]),
     ...[0, 1, 2].map(i => ({ n: `s3_cifra${i}`, fx: "fade", d: 300 + i * 150 })),
     ...[0, 1, 2, 3].map(i => ({ n: `s3_agua${i}`, fx: "wipeL", d: 600, t: 1400 }))],
    [...grupo.map((n, i) => ({ n, fx: n.startsWith("s3_h") && n.length <= 5 ? "wipeL" : "fade", d: i * 80 })), { n: "s3_sup", fx: "fade", d: 400 }],
  ]);
  notas(s, { quien: "S3 · Benjamín · 1:25–2:20 (55 s)",
    habla: "La colocación tiene dos frentes simultáneos de treinta metros cúbicos por hora, coordinados por nivel. Son once capas de hasta cuarenta centímetros; no esperamos a que cada una gane resistencia antes de continuar. Hay cinco objetos geométricos en el IFC, pero eso no significa cinco juntas de construcción. Los nueve ramales están en cuatro alturas y se conectan en paralelo. Cada ramal abierto conduce dieciocho litros por minuto. Solo abre cuando está cubierto y todo su recorrido monitoreado alcanza diecinueve grados; cierra si algún tramo baja a dieciocho. La extracción está limitada a quince kilowatts para todo el sistema, no para cada tubo. Luis explicará cómo comprobamos esta representación.",
    clics: "1) Capas de abajo hacia arriba (secuencia esquemática). 2) Cuatro niveles de tubos (3/3/2/1) y agua circulando en ramales abiertos. 3) Regla de histéresis 19/18 °C.",
    fuente: "resultados/diseno_circuitos_colocacion/esquema.json; cronogramas.csv; CIERRE_BENJAMIN.md.",
    cuidado: "Cubierto no significa abierto automáticamente; la banda 18–19 °C conserva el estado. Tubos = esquema geométrico, no instalación dimensionada hidráulicamente. 15 kW es tope conjunto, no por tubo." });
}

// =================================================================== S4
{
  const s = slideEn("CLARO", "Recorrido oral");
  s.addText("Comprobamos balance y sensibilidad del cálculo", { placeholder: "title" });
  // IFC -> malla
  s.addImage({ path: path.join(REC, "iso_capas.png"), x: 0.55, y: 1.55, w: 2.6, h: 2.6 * 642 / 1056, objectName: "s4_ifc" });
  T(s, "IFC → capas", { x: 0.55, y: 3.2, w: 2.6, h: 0.3, fontSize: 14, color: K.gris, align: "center", objectName: "s4_ifcT" });
  s.addShape(pres.shapes.RIGHT_ARROW, { x: 3.25, y: 2.25, w: 0.5, h: 0.3, fill: { color: K.grisMedio }, line: { type: "none" }, objectName: "s4_fl1" });
  for (let i = 0; i < 5; i++) for (let j = 0; j < 5; j++) {
    R(s, { x: 3.9 + i * 0.3, y: 1.65 + j * 0.3, w: 0.28, h: 0.28, fill: { color: (i === 2 && j === 2) ? K.petroleo : "BFD9D3" }, objectName: `s4_m${i}${j}` });
  }
  T(s, "malla 0,40 m", { x: 3.8, y: 3.2, w: 1.7, h: 0.3, fontSize: 14, color: K.gris, align: "center", objectName: "s4_mallaT" });
  // celda grande
  const cx = 6.25, cy = 1.75, cw = 1.9;
  R(s, { x: cx, y: cy, w: cw, h: cw, fill: { color: K.petroleo }, objectName: "s4_celda" });
  T(s, "almacena\nC dT/dt", { x: cx, y: cy + 0.55, w: cw, h: 0.8, fontSize: 16, color: K.blanco, align: "center", bold: true, objectName: "s4_alm" });
  const fl = [
    ["s4_cond", pres.shapes.LEFT_RIGHT_ARROW, cx - 0.75, cy + 0.8, 0.65, 0.32, K.grisMedio, "conduce", cx - 0.95, cy + 0.4],
    ["s4_hid", pres.shapes.UP_ARROW, cx + cw / 2 - 0.15, cy + cw + 0.08, 0.3, 0.5, "E58A4E", "hidrata", cx + cw / 2 - 0.6, cy + cw + 0.6],
    ["s4_bor", pres.shapes.UP_DOWN_ARROW, cx + cw / 2 - 0.15, cy - 0.6, 0.3, 0.52, K.azul, "intercambia", cx + cw / 2 + 0.2, cy - 0.55],
    ["s4_fri", pres.shapes.RIGHT_ARROW, cx + cw + 0.08, cy + 0.8, 0.6, 0.32, "39A0E0", "extrae", cx + cw + 0.05, cy + 1.15],
  ];
  fl.forEach(([n, sh, x, y, w, h, c, lab, lx, ly]) => {
    s.addShape(sh, { x, y, w, h, fill: { color: c }, line: { type: "none" }, objectName: n });
    T(s, lab, { x: lx, y: ly, w: 1.3, h: 0.3, fontSize: 15, color: K.carbon, bold: true, objectName: n + "T", align: n === "s4_cond" ? "left" : "left" });
  });
  ecuacion(s, "eq_s4", "C_i \\frac{d T_i}{d t} =\\sum_j G_{ij}(T_j - T_i) + Q_i + q_{borde} - q_{frío}",
    { x: 0.6, y: 4.35, w: 8.3, h: 0.95, fontSize: 26, align: "center", respaldo: "Ci dTi/dt = Σ Gij (Tj − Ti) + Qi + q_borde − q_frío" });
  T(s, [{ text: "✓ ", options: { color: K.petroleo, bold: true } }, { text: "conservación de energía      " },
        { text: "✓ ", options: { color: K.petroleo, bold: true } }, { text: "caso conocido" }],
    { x: 0.6, y: 5.45, w: 8.3, h: 0.4, fontSize: 18, align: "center", objectName: "s4_chk" });
  // tabla sensibilidad
  const th = { bold: true, color: K.blanco, fill: { color: K.carbon }, fontSize: 16, fontFace: FS, align: "center", valign: "middle" };
  const td = { fontSize: 15, color: K.carbon, fontFace: F, align: "center", valign: "middle", fill: { color: K.blanco } };
  const tg = Object.assign({}, td, { bold: true, color: K.violeta, fontSize: 20, fontFace: FS });
  s.addTable([
    [{ text: "Espacio", options: th }, { text: "Tiempo", options: th }],
    [{ text: "0,40 → 0,20 m", options: td }, { text: "300 → 150 s", options: td }],
    [{ text: "24 escenarios", options: td }, { text: "3 casos decisivos", options: td }],
    [{ text: "ΔT cambia ≤ 0,76 K", options: tg }, { text: "ΔT cambia ≤ 0,004 K", options: tg }],
    [{ text: "misma clasificación", options: Object.assign({}, td, { color: K.petroleo, bold: true }) }, { text: "misma clasificación", options: Object.assign({}, td, { color: K.petroleo, bold: true }) }],
  ], { x: 9.2, y: 1.6, w: 3.6, colW: [1.8, 1.8], rowH: [0.5, 0.55, 0.55, 0.75, 0.55], border: { type: "solid", color: K.rejilla, pt: 1 }, objectName: "s4_tabla" });
  T(s, "mayor cambio por par emparejado", { x: 9.2, y: 4.6, w: 3.6, h: 0.3, fontSize: 13, color: K.tenue, align: "center", objectName: "s4_tablaT" });
  etiqueta(s, "sensibilidad ≠ calibración ni validación de tubos", 0.6, 6.3, { tipo: "R", w: 9, fontSize: 14, objectName: "s4_et" });
  clics(s, [
    [{ n: "s4_ifc", fx: "fade" }, { n: "s4_ifcT", fx: "fade" }, { n: "s4_fl1", fx: "wipeL", d: 200 },
     ...[0, 1, 2, 3, 4].flatMap(i => [0, 1, 2, 3, 4].map(j => ({ n: `s4_m${i}${j}`, fx: "fade", d: 300 + (i + j) * 40, t: 200 }))), { n: "s4_mallaT", fx: "fade", d: 400 },
     { n: "s4_celda", fx: "zoomIn", d: 700 }, { n: "s4_alm", fx: "fade", d: 800 },
     ...fl.flatMap(([n], i) => [{ n, fx: "fade", d: 950 + i * 120 }, { n: n + "T", fx: "fade", d: 950 + i * 120 }])],
    [{ n: "eq_s4", fx: "fade" }, { n: "s4_chk", fx: "fade", d: 300 }],
    [{ n: "s4_tabla", fx: "wipeU", t: 500 }, { n: "s4_tablaT", fx: "fade", d: 300 }, { n: "s4_et", fx: "fade", d: 400 }],
  ]);
  notas(s, { quien: "S4 · Luis · 2:20–3:20 (60 s)",
    habla: "Usamos un balance de energía propio por celda. Cada celda almacena calor, conduce hacia sus vecinas y recibe los aportes de hidratación y de los bordes, descontando la extracción. Las celdas futuras quedan fuera del dominio y una cara cubierta pasa de intercambiar con el exterior a conducir internamente. Comprobamos conservación de energía y un caso conocido. Después separamos dos sensibilidades: reducir la malla de cuarenta a veinte centímetros, con los veinticuatro escenarios de la candidata, y reducir el paso de trescientos a ciento cincuenta segundos en tres casos decisivos. El mayor cambio espacial del diferencial fue cero coma setenta y seis grados; el temporal, menos de cuatro milésimas. Se mantuvo el cumplimiento.",
    clics: "1) IFC → malla → una celda con sus flujos. 2) Ecuación de balance + comprobaciones. 3) Tabla de sensibilidad.",
    fuente: "MODELO_NUEVE_CIRCUITOS.md; sensibilidad_espacial.csv (máx. |ΔΔT| = 0,7607 K); CONFIRMACION_CIRCUITOS.md (temporal ≤ 0,0038 K).",
    cuidado: "Paso explícito con cota de estabilidad y cortes en eventos. La temporal es selectiva (3 pares), no 24 a 150 s. Dos mallas no demuestran orden de convergencia. Las 11 capas y la zona de frío se conservan al refinar. Detalle en B08." });
}

// =================================================================== S5
{
  const s = slideEn("CLARO", "Recorrido oral");
  s.addText("El mayor diferencial aparece después del pico de temperatura", { placeholder: "title" });
  const h = D.historia;
  const top = scatterData([
    { name: "Tmax hormigón", x: h.t, y: h.Tmax },
    { name: "Tmin S25", x: h.t, y: h.S25 },
    { name: "14 días", x: [336, 336], y: [0, 50] },
  ]);
  s.addChart(pres.charts.SCATTER, top, ejes({
    x: 0.45, y: 1.3, w: 8.2, h: 2.75, chartColors: [K.rojo, K.azul, "4A5660"],
    valAxisMinVal: 0, valAxisMaxVal: 50, valAxisMajorUnit: 10, catAxisMinVal: 0, catAxisMaxVal: 600, catAxisMajorUnit: 48,
    showValAxisTitle: true, valAxisTitle: "°C", catAxisHidden: false, objectName: "s5_top",
  }));
  const bot = scatterData([
    { name: "ΔT", x: h.t, y: h.dT },
    { name: "límite 20 K", x: [0, 600], y: [20, 20] },
    { name: "14 días", x: [336, 336], y: [0, 25] },
    { name: "evento 428 h", x: [428], y: [19.3581] },
  ]);
  s.addChart(pres.charts.SCATTER, bot, ejes({
    x: 0.45, y: 4.05, w: 8.2, h: 2.55, chartColors: [K.violeta, K.carbon, "4A5660", K.violeta],
    valAxisMinVal: 0, valAxisMaxVal: 25, valAxisMajorUnit: 5, catAxisMinVal: 0, catAxisMaxVal: 600, catAxisMajorUnit: 48,
    showValAxisTitle: true, valAxisTitle: "ΔT [K]", showCatAxisTitle: true, catAxisTitle: "tiempo desde el inicio [h]", objectName: "s5_bot",
  }));
  T(s, "M4_SS × ERA5-2024 · base común 0,40 m / 300 s", { x: 0.6, y: 6.68, w: 6, h: 0.3, fontSize: 13, color: K.tenue });
  T(s, [{ text: "Tmax ", options: { color: K.rojo, bold: true } }, { text: "Tmin S25", options: { color: K.azul, bold: true } }],
    { x: 6.6, y: 1.25, w: 2.0, h: 0.3, fontSize: 14, align: "right" });
  T(s, "pico 45,7 °C\n≈ 127 h", { x: 1.75, y: 1.35, w: 1.6, h: 0.55, fontSize: 13, color: K.rojo, objectName: "s5_pico" });
  T(s, "14 días", { x: 5.33, y: 4.1, w: 1.0, h: 0.3, fontSize: 13, color: "4A5660", bold: true, objectName: "s5_14d" });
  // derecha
  s.addImage({ path: path.join(REC, "corte_428h.png"), x: 8.85, y: 1.45, w: 4.1, h: 4.1 * 718 / 1552, objectName: "s5_corte" });
  T(s, "corte y = 0 · misma corrida", { x: 8.85, y: 1.2, w: 4.1, h: 0.3, fontSize: 13, color: K.tenue, objectName: "s5_corteT" });
  T(s, "428 h ≈ 17,8 días", { x: 8.85, y: 3.55, w: 4.1, h: 0.45, fontSize: 22, bold: true, color: K.carbon, objectName: "s5_428" });
  T(s, [{ text: "28,70", options: { color: K.rojo } }, { text: " − " }, { text: "9,34", options: { color: K.azul } }, { text: " = " }, { text: "19,36 K", options: { color: K.violeta } }],
    { x: 8.85, y: 4.05, w: 4.3, h: 0.7, fontSize: 30, fontFace: FS, objectName: "s5_resta", valign: "middle" });
  T(s, "ambas temperaturas en el mismo instante", { x: 8.85, y: 4.75, w: 4.1, h: 0.3, fontSize: 13, color: K.tenue, objectName: "s5_restaT" });
  etiqueta(s, "confirmación fina del catálogo: ΔTmax 19,17 K", 8.85, 5.45, { tipo: "R", w: 4.2, h: 0.6, fontSize: 14, objectName: "s5_fino" });
  clics(s, [
    [{ n: "s5_top", fx: "wipeL", t: 1000 }, { n: "s5_pico", fx: "fade", d: 700 }],
    [{ n: "s5_bot", fx: "wipeL", t: 1000 }, { n: "s5_14d", fx: "fade", d: 600 }],
    [{ n: "s5_corte", fx: "fade" }, { n: "s5_corteT", fx: "fade" }, { n: "s5_428", fx: "fade", d: 250 }, { n: "s5_resta", fx: "fade", d: 450 }, { n: "s5_restaT", fx: "fade", d: 450 }, { n: "s5_fino", fx: "fade", d: 700 }],
  ]);
  notas(s, { quien: "S5 · Luis · 3:20–4:35 (75 s)",
    habla: "Esta figura muestra el mismo escenario y la malla común de cuarenta centímetros. Aquí seguimos la máxima del hormigón y la mínima en S veinticinco. La diferencia se calcula entre ambas en cada instante. La mayor temperatura ocurre primero, pero el mayor diferencial aparece después, cuando el interior conserva calor y el contorno se enfría. En el caso mostrado, a las cuatrocientas veintiocho horas tenemos veintiocho coma setenta grados en el punto caliente y nueve coma treinta y cuatro en S veinticinco: la diferencia es diecinueve coma treinta y seis. Por eso informamos los catorce días exigidos y extendemos a veinticinco para capturar el máximo tardío. Con malla fina, el peor diferencial del catálogo es diecinueve coma diecisiete. Matías explicará qué significa ese resultado para la incertidumbre.",
    clics: "1) Tmax y Tmin S25 (barrido temporal, ejes fijos). 2) ΔT con límite 20 K y marca de 14 días. 3) Corte a 428 h y resta simultánea.",
    fuente: "resultados/comparacion_circuitos/q60/malla_0.4/M4_SS_ERA5-2024.json (historia muestreada cada 2 h para el gráfico) y .npz (comun_428h_T_C). Evento 428 h: COMPARACION_CIRCUITOS_FINAL.md (28,7009 − 9,3429 = 19,3581 K, fase previa al evento).",
    cuidado: "No restar 46,02 − 9,34: son instantes y resoluciones distintos. No decir que el máximo térmico ocurre necesariamente a 428 h. La curva es una historia ya calculada, no una simulación en vivo. El punto de 428 h usa el valor del evento (antes del cambio de estado); la curva muestreada puede verse levemente distinta." });
}

// =================================================================== S6
{
  const s = slideEn("CLARO", "Recorrido oral");
  s.addText("Ocho fuentes y tres climas forman 24 escenarios", { placeholder: "title" });
  const nombres = ["M1_SS", "M2_SS", "M3_SS", "M4_SS", "M1_22A", "M2_22A", "M3_22A", "M4_22A"];
  const colM = ["1B74AA", "166C65", "C99A2E", "B54830"];
  const series = nombres.map(n => ({ name: n, x: D.fuentes_t, y: D.fuentes[n] }));
  s.addChart(pres.charts.SCATTER, scatterData(series), ejes({
    x: 0.45, y: 1.3, w: 5.4, h: 4.6, chartColors: [...colM, ...colM], lineSize: 2,
    valAxisMinVal: 0, valAxisMaxVal: 700, valAxisMajorUnit: 100, catAxisMinVal: 0, catAxisMaxVal: 240, catAxisMajorUnit: 48,
    showValAxisTitle: true, valAxisTitle: "Q [W/m³]", showCatAxisTitle: true, catAxisTitle: "edad [h]",
    showLegend: true, legendPos: "b", legendFontSize: 13, legendFontFace: F, legendColor: "4A5660", objectName: "s6_fuentes",
  }));
  T(s, "8 curvas completas · trazo continuo SS · discontinuo 22A", { x: 0.6, y: 5.95, w: 5.3, h: 0.3, fontSize: 13, color: K.tenue, objectName: "s6_fT" });
  // climas
  ["2023", "2024", "2025"].forEach((a, i) => {
    const c = D.clima[a];
    s.addChart(pres.charts.SCATTER, scatterData([{ name: a, x: c.t, y: c.T }]), ejes({
      x: 6.05, y: 1.45 + i * 1.3, w: 2.75, h: 1.2, chartColors: ["4A5660"], lineSize: 1.25,
      valAxisMinVal: 0, valAxisMaxVal: 35, valAxisMajorUnit: 35, catAxisMinVal: 0, catAxisMaxVal: 336, catAxisMajorUnit: 336,
      catAxisLabelFontSize: 10, valAxisLabelFontSize: 10, objectName: `s6_clima${i}`,
    }));
    T(s, `ERA5 ${a}`, { x: 6.15, y: 1.3 + i * 1.3, w: 1.5, h: 0.28, fontSize: 13, bold: true, color: K.carbon, objectName: `s6_climaT${i}` });
  });
  T(s, "aire [°C] · 0–336 h", { x: 6.05, y: 5.35, w: 2.75, h: 0.3, fontSize: 12, color: K.tenue, align: "center", objectName: "s6_climaU" });
  // matriz 8x3
  const mx = 9.95, my = 2.05, cs = 0.34, gap = 0.06;
  T(s, "8 × 3 = 24", { x: 8.95, y: 1.2, w: 3.9, h: 0.45, fontSize: 22, bold: true, fontFace: FS, color: K.carbon, align: "center", objectName: "s6_8x3" });
  nombres.forEach((n, r) => T(s, n, { x: 8.95, y: my + r * (cs + gap), w: 0.95, h: cs, fontSize: 11, color: K.gris, valign: "middle", align: "right", objectName: `s6_fila${r}` }));
  [0, 1, 2].forEach(c => {
    T(s, ["23", "24", "25"][c], { x: mx + c * (cs + gap) + 0.04, y: my - 0.3, w: cs, h: 0.25, fontSize: 11, color: K.gris, align: "center", objectName: `s6_colT${c}` });
    nombres.forEach((n, r) => R(s, { x: mx + 0.04 + c * (cs + gap), y: my + r * (cs + gap), w: cs, h: cs, fill: { color: "A9D3CB" }, objectName: `s6_c${c}_${r}` }, pres.shapes.ROUNDED_RECTANGLE));
  });
  T(s, "peso 1/24 c/u", { x: 11.35, y: my + 1.2, w: 1.5, h: 0.6, fontSize: 14, color: K.petroleo, bold: true, objectName: "s6_peso" });
  // ecuaciones
  ecuacion(s, "eq_s6_F", "F_s = \\{T_{max} > 70\\} \\cup \\{\\Delta T_{max} > 20\\}",
    { x: 6.05, y: 5.75, w: 6.9, h: 0.55, fontSize: 20, respaldo: "Fs = {Tmax > 70} ∪ {ΔTmax > 20}" });
  ecuacion(s, "eq_s6_P", "P_f = \\sum_s w_s I(F_s) = 0\\ \\%",
    { x: 6.05, y: 6.3, w: 4.0, h: 0.8, fontSize: 22, color: K.petroleo, respaldo: "Pf = Σ ws I(Fs) = 0 %" });
  T(s, "en el catálogo", { x: 9.6, y: 6.45, w: 1.8, h: 0.45, fontSize: 15, color: K.petroleo, objectName: "s6_cat", valign: "middle" });
  T(s, [{ text: "SUPUESTO DEL MODELO\n", options: { bold: true, color: K.ocre, fontSize: 11, charSpacing: 1 } }, { text: "pesos iguales e independencia", options: { color: K.gris, fontSize: 13 } }],
    { x: 11.3, y: my + 1.95, w: 1.75, h: 1.1, objectName: "s6_sup" });
  clics(s, [
    [{ n: "s6_fuentes", fx: "wipeL", t: 900 }, { n: "s6_fT", fx: "fade", d: 500 }],
    [...[0, 1, 2].flatMap(i => [{ n: `s6_clima${i}`, fx: "wipeL", d: i * 150, t: 500 }, { n: `s6_climaT${i}`, fx: "fade", d: i * 150 }]), { n: "s6_climaU", fx: "fade" },
     { n: "s6_8x3", fx: "fade", d: 300 }, ...[0, 1, 2, 3, 4, 5, 6, 7].map(r => ({ n: `s6_fila${r}`, fx: "fade", d: 300 })),
     ...[0, 1, 2].flatMap(c => [{ n: `s6_colT${c}`, fx: "fade", d: 400 + c * 250 }, ...[0, 1, 2, 3, 4, 5, 6, 7].map(r => ({ n: `s6_c${c}_${r}`, fx: "fade", d: 400 + c * 250 + r * 25, t: 200 }))]),
     { n: "s6_peso", fx: "fade", d: 1200 }, { n: "s6_sup", fx: "fade", d: 1300 }],
    [{ n: "eq_s6_F", fx: "fade" }, { n: "eq_s6_P", fx: "fade", d: 500 }, { n: "s6_cat", fx: "fade", d: 600 }],
  ]);
  notas(s, { quien: "S6 · Matías · 4:35–5:20 (45 s)",
    habla: "No usamos una curva promedio. Conservamos ocho fuentes completas del profesor y tres historias climáticas de El Rosal, de dos mil veintitrés, veinticuatro y veinticinco. Eso da veinticuatro combinaciones por plan. Cada combinación pesa un veinticuatroavo, bajo equiprobabilidad e independencia supuestas. Una corrida falla si supera cualquiera de los dos límites; si supera ambos, se cuenta una sola vez. El riesgo se obtiene sumando los pesos de las corridas fallidas. La meta es no superar el cinco por ciento. Aquí da cero dentro del catálogo. Eso no representa climas ausentes ni demuestra riesgo real cero.",
    clics: "1) Ocho fuentes Q(edad). 2) Tres climas ERA5 y matriz 8×3 por columnas. 3) Unión de límites y P_f.",
    fuente: "datos/hidratacion/source_terms.txt (W/m³, muestreado cada 1 h); ERA5 Open-Meteo, aire 2 m alineado al inicio hipotético 2026; escenarios.csv.",
    cuidado: "M1–M4 son probetas, SS/22A campañas; no son mezclas comerciales seleccionables ni sensores de la fundación. ERA5 histórico no es pronóstico 2026. Una curva común a todas las capas por realización." });
}

// =================================================================== S7
{
  const s = slideEn("CLARO", "Recorrido oral");
  s.addText("Sesenta metros cúbicos por hora alcanza la cota de duración", { placeholder: "title" });
  const th = { bold: true, color: K.blanco, fill: { color: K.carbon }, fontSize: 15, fontFace: FS, align: "center", valign: "middle" };
  const filas = [[{ text: "Ritmo [m³/h]", options: th }, { text: "D [h]", options: th }, { text: "P_T", options: th }, { text: "P_Δ", options: th }, { text: "P_f", options: th }, { text: "Cumple", options: th }]];
  ["q60", "q55", "q50", "q45"].forEach((q, i) => {
    const r = P[`${q}_0.4_600`];
    const st = { fontSize: 16, fontFace: i === 0 ? FS : F, color: i === 0 ? K.blanco : K.carbon, align: "center", valign: "middle", fill: { color: i === 0 ? K.petroleo : K.blanco }, bold: i === 0 };
    filas.push([r.caudal_m3_h, fmt(r.D_h, 2), "0 %", "0 %", "0 %", "Sí"].map(t => ({ text: String(t), options: st })));
  });
  s.addTable(filas, { x: 0.6, y: 1.35, w: 7.4, colW: [1.6, 1.2, 1.1, 1.1, 1.1, 1.3], rowH: 0.42, border: { type: "solid", color: K.rejilla, pt: 1 }, objectName: "s7_tabla" });
  T(s, "mismos controles · 24 pares por plan · 0,40 m / 300 s · horizonte 600 h", { x: 0.6, y: 3.55, w: 7.4, h: 0.3, fontSize: 13, color: K.tenue, objectName: "s7_tablaT" });
  // ecuación cota
  ecuacion(s, "eq_s7", "D \\geq \\frac{V}{Q} = \\frac{636{,}775\\ \\mathrm{m}^3}{60\\ \\mathrm{m}^3/\\mathrm{h}} = 10{,}61\\ \\mathrm{h}",
    { x: 8.35, y: 1.35, w: 4.7, h: 1.3, fontSize: 26, color: K.petroleo, respaldo: "D ≥ V/Q = 636,775 m³ / 60 m³/h = 10,61 h" });
  etiqueta(s, "60 m³/h = capacidad máxima adoptada", 8.4, 2.75, { tipo: "S", w: 4.6, h: 0.55, fontSize: 13, objectName: "s7_sup" });
  // cronogramas (Gantt)
  const gx = 1.45, gy = 4.4, gw = 5.9, rh = 0.4, tmax = 15;
  const tx = t => gx + t / tmax * gw;
  ["q60", "q55", "q50", "q45"].forEach((q, i) => {
    T(s, q.slice(1), { x: 0.6, y: gy + i * (rh + 0.12), w: 0.75, h: rh, fontSize: 15, bold: i === 0, color: i === 0 ? K.petroleo : K.gris, align: "right", valign: "middle", objectName: `s7_gl${i}` });
    D.cronogramas.filter(c => c.plan === q).forEach((c, k) => {
      R(s, { x: tx(+c.inicio_h), y: gy + i * (rh + 0.12), w: (c.fin_h - c.inicio_h) / tmax * gw - 0.01, h: rh,
        fill: { color: i === 0 ? (k % 2 ? "2C8A80" : K.petroleo) : (k % 2 ? "B5BCC1" : "9AA3A9") }, objectName: `s7_g${i}_${k}` });
    });
    const Dh = +P[`${q}_0.4_600`].D_h;
    T(s, fmt(Dh, 2) + " h", { x: tx(Dh) + 0.08, y: gy + i * (rh + 0.12), w: 1.0, h: rh, fontSize: 14, bold: i === 0, color: i === 0 ? K.petroleo : K.gris, valign: "middle", objectName: `s7_gD${i}` });
  });
  [0, 5, 10, 15].forEach(t => T(s, `${t} h`, { x: tx(t) - 0.3, y: gy + 4 * (rh + 0.12), w: 0.6, h: 0.28, fontSize: 12, color: K.tenue, align: "center", objectName: `s7_gx${t}` }));
  T(s, "once capas por plan", { x: gx, y: gy - 0.38, w: 3, h: 0.3, fontSize: 13, color: K.tenue, objectName: "s7_gT" });
  // D vs Pf
  const pts = ["q60", "q55", "q50", "q45"].map(q => +P[`${q}_0.4_600`].D_h);
  s.addChart(pres.charts.SCATTER, scatterData([
    { name: "planes", x: pts, y: [0, 0, 0, 0] },
    { name: "meta 5 %", x: [10, 15], y: [5, 5] },
  ]), ejes({
    x: 8.3, y: 3.6, w: 4.75, h: 3.0, chartColors: [K.petroleo, K.carbon], lineDataSymbol: "circle", lineDataSymbolSize: 11,
    valAxisMinVal: 0, valAxisMaxVal: 10, valAxisMajorUnit: 5, catAxisMinVal: 10, catAxisMaxVal: 15, catAxisMajorUnit: 1,
    showValAxisTitle: true, valAxisTitle: "P_f [%]", showCatAxisTitle: true, catAxisTitle: "D [h]", objectName: "s7_dp",
  }));
  T(s, "meta 5 %", { x: 11.75, y: 4.2, w: 1.1, h: 0.3, fontSize: 13, color: K.carbon, bold: true, objectName: "s7_meta" });
  R(s, { x: 0.53, y: 1.74, w: 7.54, h: 0.5, fill: { type: "none" }, line: { color: K.ocre, width: 3 }, objectName: "s7_hl" }, pres.shapes.ROUNDED_RECTANGLE);
  clics(s, [
    [{ n: "s7_tabla", fx: "fade", t: 400 }, { n: "s7_tablaT", fx: "fade", d: 200 }],
    [{ n: "s7_gT", fx: "fade" }, ...[0, 1, 2, 3].flatMap(i => [{ n: `s7_gl${i}`, fx: "fade", d: i * 120 }, ...Array.from({ length: 11 }, (_, k) => ({ n: `s7_g${i}_${k}`, fx: "wipeL", d: i * 120 + k * 60, t: 150 })), { n: `s7_gD${i}`, fx: "fade", d: i * 120 + 700 }]),
     ...[0, 5, 10, 15].map(t => ({ n: `s7_gx${t}`, fx: "fade" })), { n: "s7_dp", fx: "fade", d: 400 }, { n: "s7_meta", fx: "fade", d: 600 }],
    [{ n: "eq_s7", fx: "fade" }, { n: "s7_sup", fx: "fade", d: 300 }, { n: "s7_hl", fx: "zoomIn", d: 500, t: 300 }],
  ]);
  notas(s, { quien: "S7 · Matías · 5:20–6:25 (65 s)",
    habla: "Comparamos sesenta, cincuenta y cinco, cincuenta y cuarenta y cinco metros cúbicos por hora, manteniendo geometría, materiales, clima y controles. Los cuatro cumplen en la malla común. Al bajar a cuarenta y cinco, la colocación aumenta de diez coma sesenta y una a catorce coma quince horas, sin mejorar el peor diferencial del catálogo. Las pequeñas diferencias térmicas no justifican por sí solas la elección. Elegimos el plazo menor. Con seiscientos treinta y seis coma setenta y cinco metros cúbicos y una capacidad máxima adoptada de sesenta por hora, la cota es volumen dividido por caudal: diez coma sesenta y una horas. Una alternativa más rápida requeriría cambiar ese recurso. Esta capacidad es un supuesto docente, no un rendimiento medido en El Rosal.",
    clics: "1) Tabla de cuatro planes. 2) Cronogramas (11 capas) y gráfico D–P_f con meta 5 %. 3) Cota V/Q y énfasis en la fila 60.",
    fuente: "evidencia_circuitos/comparacion_planes.csv y cronogramas.csv. Los 14 días también cumplen; tablas completas en B10.",
    cuidado: "Diferencias térmicas de centésimas son menores que la sensibilidad espacial: elegir por D. No inventar riesgo a 75 m³/h (no simulado). Los puntos del gráfico son todos de malla gruesa homogénea; no es una curva optimizada. Una sola vertida y propuesta son la misma fila 60." });
}

// =================================================================== S8
{
  const s = slideEn("OSCURO", "Recorrido oral");
  T(s, "RECOMENDACIÓN", { x: 0.6, y: 0.75, w: 6, h: 0.35, fontSize: 14, bold: true, color: K.petroleoClaro, charSpacing: 2 });
  T(s, "Colocar en 10,61 h y mantener el control térmico", { x: 0.6, y: 1.1, w: 7.6, h: 1.2, fontSize: 34, fontFace: FS, color: K.blanco });
  T(s, "60 m³/h · 12 °C · 9 circuitos", { x: 0.6, y: 2.4, w: 7.4, h: 0.5, fontSize: 24, color: K.petroleoClaro });
  T(s, [{ text: "Confirmación fina 0,20 m: ", options: { color: K.grisMedio } }, { text: "46,02 °C · 19,17 K · 0/24 excedencias", options: { color: K.blanco } }],
    { x: 0.6, y: 3.05, w: 7.6, h: 0.4, fontSize: 18 });
  // margen
  const bx = 0.6, by = 3.85, bw = 6.4;
  R(s, { x: bx, y: by, w: bw, h: 0.16, fill: { color: "2B3F4C" } });
  R(s, { x: bx, y: by, w: bw * 19.17 / 20, h: 0.16, fill: { color: K.violeta } });
  R(s, { x: bx + bw - 0.015, y: by - 0.12, w: 0.03, h: 0.4, fill: { color: K.blanco } });
  T(s, "ΔTmax 19,17 K", { x: bx, y: by + 0.25, w: 3, h: 0.3, fontSize: 14, color: "C9A6E0" });
  T(s, "20 K · margen ≈ 0,83 K", { x: bx + bw - 3.2, y: by + 0.25, w: 3.2, h: 0.3, fontSize: 14, color: K.grisClaro, align: "right" });
  // monitoreo
  T(s, [{ text: "Medir ", options: { color: K.grisMedio } }, { text: "núcleo, S25 y circuitos", options: { color: K.blanco, bold: true } }, { text: " · condicionar retiros", options: { color: K.grisMedio } }],
    { x: 0.6, y: 4.75, w: 7.6, h: 0.4, fontSize: 19, objectName: "s8_med" });
  T(s, [{ text: "Cambia suministro, clima o frío ", options: { color: K.grisMedio } }, { text: "⇒ recalcular el plan", options: { color: K.blanco, bold: true } }],
    { x: 0.6, y: 5.25, w: 7.6, h: 0.4, fontSize: 19, objectName: "s8_cond" });
  R(s, { x: 0.6, y: 5.95, w: 7.9, h: 0.62, fill: { color: "3A2A1E" }, objectName: "s8_limC" }, pres.shapes.ROUNDED_RECTANGLE);
  T(s, [{ text: "LIMITACIÓN  ", options: { bold: true, color: "E0B354", fontSize: 13, charSpacing: 1 } }, { text: "agua 18 °C y transferencia equivalente idealizadas", options: { color: K.blanco, fontSize: 17 } }],
    { x: 0.8, y: 5.95, w: 7.6, h: 0.62, valign: "middle", objectName: "s8_lim" });
  // esquema de monitoreo
  const g = { x0: 8.3, yb: 5.2, sx: 0.25, sz: 0.25 * 1.6 };
  seccion(s, Object.assign({ colores: "2F4654", borde: K.noche }, g));
  const sens = [
    ["s8_sn", 0, 2.5, K.rojo, "núcleo"], ["s8_sp", 0, 4.0, K.rojo, ""], ["s8_s1", -8.9, 0.6, "4FA3E0", "S25"], ["s8_s2", 8.9, 0.6, "4FA3E0", ""],
    ["s8_s3", -3.3, 3.8, "4FA3E0", ""], ["s8_c1", -4.5, 0.5, K.petroleoClaro, "circuitos"], ["s8_c2", 3.0, 1.5, K.petroleoClaro, ""], ["s8_c3", 1.5, 2.5, K.petroleoClaro, ""],
  ];
  sens.forEach(([n, xm, zm, c]) => s.addShape(pres.shapes.OVAL, { x: X(g, xm) - 0.09, y: Z(g, zm) - 0.09, w: 0.18, h: 0.18, fill: { color: c }, line: { color: K.blanco, width: 1.5 }, objectName: n }));
  T(s, [{ text: "● núcleo   ", options: { color: "E07A5F" } }, { text: "● S25   ", options: { color: "4FA3E0" } }, { text: "● circuitos", options: { color: K.petroleoClaro } }],
    { x: 8.3, y: 5.4, w: 4.6, h: 0.3, fontSize: 14, align: "center", objectName: "s8_ley" });
  T(s, "monitoreo propuesto · esquema", { x: 8.3, y: 5.75, w: 4.6, h: 0.3, fontSize: 12, color: K.grisMedio, align: "center", objectName: "s8_leyT" });
  T(s, "Preguntas  ·  consulta B01–B12", { x: 0.6, y: 6.95, w: 6, h: 0.35, fontSize: 13, color: K.grisMedio });
  clics(s, [
    [{ n: "s8_med", fx: "fade" }, ...sens.map(([n], i) => ({ n, fx: "zoomIn", d: 150 + i * 80, t: 250 })), { n: "s8_ley", fx: "fade", d: 600 }, { n: "s8_leyT", fx: "fade", d: 600 }, { n: "s8_cond", fx: "fade", d: 900 }],
    [{ n: "s8_limC", fx: "fade" }, { n: "s8_lim", fx: "fade" }],
  ]);
  notas(s, { quien: "S8 · Matías · 6:25–7:00 (35 s)",
    habla: "Recomendamos entonces sesenta metros cúbicos por hora, doce grados y el control de nueve circuitos. El plazo corresponde a colocación; el curado y el control térmico continúan después. La principal limitación es la refrigeración equivalente: agua idealizada a dieciocho grados y transferencia sin calibración en obra. Por eso proponemos medir núcleo, S veinticinco y circuitos, condicionar los retiros y actualizar el cálculo si cambian el suministro, el clima o la refrigeración.",
    clics: "Decisión visible al entrar. 1) Monitoreo y condición de actualización. 2) Limitación.",
    fuente: "comparacion_planes.csv (0,20 m: 46,0192 °C; 19,1731 K); CIERRE_BENJAMIN.md (sensores y contingencias).",
    cuidado: "El margen ≈ 0,83 K no es holgado. El registro continúa después de colocar; no hay fecha de apagado definitivo demostrada. Navegación: la diapositiva 9 es el índice de consulta con enlaces a B01–B12. Consulta B11 y B12." });
}

// =================================================================== Índice de consulta
const temasB = [
  ["B01", "Geometría, capas y tubos", "Benjamín"], ["B02", "Viento y clima histórico", "Matías"], ["B03", "Balance continuo y bordes", "Luis"],
  ["B04", "Mantas y retiro condicionado", "Benjamín"], ["B05", "Fuente y propiedades", "Matías"], ["B06", "Qué son 15 kW y 18 L/min", "Benjamín/Luis"],
  ["B07", "Recepción a 12 °C y unión", "Benjamín"], ["B08", "Balance discreto y sensibilidad", "Luis"], ["B09", "Una fila, la unión y los pesos", "Matías"],
  ["B10", "Comparación completa", "Matías/Luis"], ["B11", "Medición y desviaciones", "Benjamín"], ["B12", "Alcance y qué no se validó", "Los tres"],
];
const nIndice = nSlide + 1;
{
  const s = slideEn("OSCURO", "Consulta");
  T(s, "Consulta para preguntas", { x: 0.6, y: 0.5, w: 10, h: 0.7, fontSize: 30, fontFace: FS, color: K.blanco });
  T(s, "Fuera del recorrido de 7 minutos · clic en un tema para saltar", { x: 0.6, y: 1.15, w: 10, h: 0.4, fontSize: 15, color: K.grisMedio });
  temasB.forEach(([id, tema, quien], i) => {
    const c = i % 3, r = Math.floor(i / 3);
    const x = 0.6 + c * 4.1, y = 1.9 + r * 1.2;
    R(s, { x, y, w: 3.9, h: 1.0, fill: { color: K.noche2 }, hyperlink: { slide: nIndice + 1 + i, tooltip: tema } }, pres.shapes.ROUNDED_RECTANGLE);
    T(s, [{ text: id + "  ", options: { bold: true, color: K.petroleoClaro, fontSize: 20, fontFace: FS, hyperlink: { slide: nIndice + 1 + i } } },
          { text: tema, options: { color: K.blanco, fontSize: 16, hyperlink: { slide: nIndice + 1 + i } } },
          { text: "\n" + quien, options: { color: K.grisMedio, fontSize: 12, breakLine: false } }],
      { x: x + 0.2, y, w: 3.6, h: 1.0, valign: "middle" });
  });
  notas(s, { quien: "Índice de consulta (no forma parte de los 7 minutos)",
    habla: "Cada tarjeta enlaza a su diapositiva B. Desde cada B, el enlace «índice» vuelve aquí. También se puede escribir el número de diapositiva y presionar Enter en modo presentación.",
    cuidado: "Cualquier integrante debe poder responder aunque figure un referente." });
}

// =================================================================== B01–B12
function consulta(id, titulo, notasB) {
  const s = slideEn("CONSULTA", "Consulta");
  R(s, { x: 0.6, y: 0.47, w: 0.8, h: 0.5, fill: { color: K.carbon } }, pres.shapes.ROUNDED_RECTANGLE);
  T(s, id, { x: 0.6, y: 0.47, w: 0.8, h: 0.5, fontSize: 16, bold: true, color: K.blanco, align: "center", valign: "middle" });
  s.addText(titulo, { placeholder: "title" });
  T(s, "← índice", { x: 11.7, y: 0.55, w: 1.1, h: 0.35, fontSize: 13, color: K.petroleo, align: "right", hyperlink: { slide: nIndice, tooltip: "Volver al índice" } });
  notas(s, notasB);
  return s;
}
const th = { bold: true, color: K.blanco, fill: { color: K.carbon }, fontSize: 14, fontFace: FS, align: "center", valign: "middle" };
const td = (o) => Object.assign({ fontSize: 14, color: K.carbon, fontFace: F, align: "center", valign: "middle", fill: { color: K.blanco } }, o || {});
const tabla = (s, filas, o) => s.addTable(filas.map((f, i) => f.map(c => (typeof c === "object" ? c : { text: String(c), options: i === 0 ? th : td() }))),
  Object.assign({ border: { type: "solid", color: K.rejilla, pt: 1 } }, o));
const bullets = (s, items, o) => T(s, items.map((t, i) => ({ text: t, options: { bullet: { indent: 18 }, breakLine: i < items.length - 1, paraSpaceAfter: 8 } })), Object.assign({ fontSize: 17 }, o));

// B01
{
  const s = consulta("B01", "Geometría, capas y trazado de tubos", { quien: "B01 · Referente Benjamín", habla: "Preguntas 11, 19: ¿cinco vertidas u once? ¿cómo son los tubos?", fuente: "resultados/diseno_circuitos_colocacion/circuitos_planta.png y esquema.json.", cuidado: "Razonamiento + esquema geométrico. Radios comerciales, accesorios, montaje e interferencias con armadura no están dimensionados." });
  s.addImage({ path: path.join(RAIZ, "resultados/diseno_circuitos_colocacion/circuitos_planta.png"), x: 0.6, y: 1.3, w: 5.9, h: 5.9 * 1500 / 1650 });
  tabla(s, [["Cota", "Circuitos", "Longitud"], ["0,50 m", "3", "282 m"], ["1,50 m", "3", "224 m"], ["2,50 m", "2", "99 m"], ["3,80 m", "1", "33 m"], [{ text: "Total", options: td({ bold: true }) }, { text: "9", options: td({ bold: true }) }, { text: "≈ 639 m", options: td({ bold: true }) }]],
    { x: 7.0, y: 1.4, w: 5.8, colW: [1.9, 1.9, 2.0], rowH: 0.42 });
  T(s, [{ text: "5", options: { fontSize: 40, fontFace: FS, color: K.gris } }, { text: "  objetos IFC (geometría)", options: { fontSize: 17, color: K.gris } }], { x: 7.0, y: 4.25, w: 5.8, h: 0.65, valign: "middle" });
  T(s, [{ text: "11", options: { fontSize: 40, fontFace: FS, color: K.petroleo } }, { text: "  capas térmicas de colocación", options: { fontSize: 17, color: K.petroleo } }], { x: 7.0, y: 4.9, w: 5.8, h: 0.65, valign: "middle" });
  T(s, "Ø interior de cálculo 25 mm · separación ≈ 1 m · colectores exteriores, ramales paralelos", { x: 7.0, y: 5.75, w: 5.8, h: 0.6, fontSize: 14, color: K.gris });
  etiqueta(s, "montaje y accesorios no dimensionados", 7.0, 6.45, { tipo: "C", w: 5.8 });
}
// B02
{
  const s = consulta("B02", "Viento y clima histórico", { quien: "B02 · Referente Matías, apoyo Benjamín", habla: "Preguntas 2–4: ¿más viento siempre enfría? ¿por qué 10 → 2 m? ¿por qué h = 17,09?", fuente: "evidencia_circuitos/figuras/02_clima.png; clima_metadatos.csv.", cuidado: "Coordenadas pedidas −37,277929/−72,368271; la API devolvió la celda −37,25/−72,25. Alineación desde 13:00 UTC del 19/11 de cada año al inicio 10:00 UTC−03 de 2026. 696 marcas; 0–682 h disponibles; se usan hasta 600; sin faltantes en el tramo usado. Más h puede enfriar o calentar según el signo de (T_s − T_aire). La media 17,09 no reemplaza la serie horaria." });
  s.addImage({ path: path.join(RAIZ, "entregas/F02/evidencia_circuitos/figuras/02_clima.png"), x: 0.6, y: 1.25, w: 7.6, h: 7.6 * 1039 / 1889 });
  ecuacion(s, "eq_b02_h", "h(t) = 5{,}7 + 3{,}8\\, v_2(t)", { x: 8.5, y: 1.4, w: 4.4, h: 0.7, fontSize: 26, respaldo: "h(t) = 5,7 + 3,8 v2(t)" });
  ecuacion(s, "eq_b02_v", "v_2 = v_{10} \\left(\\frac{2}{10}\\right)^{0{,}14}", { x: 8.5, y: 2.2, w: 4.4, h: 1.0, fontSize: 26, respaldo: "v2 = v10 (2/10)^0,14" });
  T(s, "h medio ≈ 17,09 W/(m² K): solo referencia", { x: 8.5, y: 3.3, w: 4.4, h: 0.35, fontSize: 15, color: K.gris });
  bullets(s, ["ERA5 vía Open-Meteo, descarga 17-11-2026, UTC", "Celda devuelta −37,25 / −72,25", "Se usan 0–600 h; sin faltantes", "Clima histórico ≠ pronóstico 2026"], { x: 8.5, y: 3.9, w: 4.4, h: 2.4, fontSize: 16 });
  etiqueta(s, "perfil de terreno abierto 10 → 2 m", 0.6, 6.55, { tipo: "S", w: 7.6 });
}
// B03
{
  const s = consulta("B03", "Balance continuo y condiciones de borde", { quien: "B03 · Referente Luis, apoyo Benjamín", habla: "Preguntas 5–9: k, cp, suelo 15 °C, suelo más frío, radiación y relleno.", fuente: "MODELO_NUEVE_CIRCUITOS.md.", cuidado: "Razonamiento: relleno, radiación o contacto imperfecto cambian los bordes y requieren nueva evaluación; no inventar números. El ΔT se evalúa en hormigón, no en suelo, aire ni celdas futuras." });
  ecuacion(s, "eq_b03_1", "\\rho c_p \\frac{\\partial T}{\\partial t} = \\nabla\\cdot(k\\nabla T) + Q(a) - q_{frío}", { x: 0.6, y: 1.4, w: 7.2, h: 0.95, fontSize: 28, respaldo: "ρ cp ∂T/∂t = ∇·(k∇T) + Q(a) − q_frío" });
  ecuacion(s, "eq_b03_2", "-k\\frac{\\partial T}{\\partial n} = \\frac{T_s - T_{aire}}{R_{capas} + 1/h}", { x: 0.6, y: 2.55, w: 7.2, h: 1.1, fontSize: 28, color: K.azul, respaldo: "−k ∂T/∂n = (Ts − Taire)/(Rcapas + 1/h)" });
  ecuacion(s, "eq_b03_3", "R_{suelo} = \\frac{0{,}50}{1{,}2} = 0{,}4167\\ \\mathrm{m}^2\\mathrm{K}/\\mathrm{W}", { x: 0.6, y: 3.85, w: 7.2, h: 0.95, fontSize: 24, color: "6E5A3A", respaldo: "Rsuelo = 0,50/1,2 = 0,4167 m²K/W" });
  tabla(s, [["Borde", "Condición"], ["Inicial", "12 °C por capa al colocarse"], ["Entre capas", "contacto perfecto"], ["Base", "reservorio 15 °C, sin inercia"], ["Laterales", "expuestos, sin relleno"], ["Radiación", "no explícita"]],
    { x: 8.2, y: 1.45, w: 4.6, colW: [1.5, 3.1], rowH: 0.45 });
  bullets(s, ["Una cara cubierta deja de llevar Robin y pasa a conducir", "Fuente volumétrica ≠ intercambio superficial", "Normal saliente n"], { x: 0.6, y: 5.0, w: 7.2, h: 1.4, fontSize: 16 });
  etiqueta(s, "bordes simplificados", 8.2, 4.4, { tipo: "S", w: 4.6 });
}
// B04
{
  const s = consulta("B04", "Mantas y retiro condicionado", { quien: "B04 · Referente Benjamín", habla: "Preguntas 15–17: ¿por qué no mantener mantas? ¿cuándo se retiran? ¿aislación entre capas?", fuente: "PROTECCIONES_BENJAMIN.png; CIERRE_BENJAMIN.md.", cuidado: "Más aislación conserva calor y puede desplazar el máximo; retirarla antes puede enfriar S25 bruscamente. No atribuir a nuestros nueve circuitos números del estudio de retiros de Luis con otros controles." });
  s.addImage({ path: path.join(RAIZ, "entregas/F02/PROTECCIONES_BENJAMIN.png"), x: 1.4, y: 1.25, w: 10.5, h: 10.5 * 690 / 1800 });
  const tx = h => 1.2 + h / 400 * 10.8, ty = 6.15;
  R(s, { x: tx(0), y: ty, w: tx(400) - tx(0), h: 0.06, fill: { color: K.grisMedio } });
  [[72, "madera 72 h", K.madera], [240, "1.ª manta 240 h", K.ocre], [360, "2.ª manta 360 h", "8A6516"]].forEach(([h, l, c]) => {
    s.addShape(pres.shapes.OVAL, { x: tx(h) - 0.12, y: ty - 0.09, w: 0.24, h: 0.24, fill: { color: c }, line: { color: K.blanco, width: 1.5 } });
    T(s, l, { x: tx(h) - 1.0, y: ty - 0.5, w: 2.0, h: 0.3, fontSize: 15, bold: true, color: c, align: "center" });
  });
  T(s, "calendario nominal por edad local", { x: 1.2, y: ty + 0.2, w: 5, h: 0.3, fontSize: 14, color: K.gris });
  etiqueta(s, "resistencia para desmolde · sensores y predicción para retiro térmico", 1.2, 6.7, { tipo: "C", w: 11 });
}
// B05
{
  const s = consulta("B05", "Fuente, propiedades y límites de identificación", { quien: "B05 · Referente Matías", habla: "Preguntas 5, 6, 27, 28: cp, k, curvas seleccionables, pesos.", fuente: "datos/hidratacion/source_terms.txt y manifiesto.json; evidencia_circuitos/fuentes_verificadas.csv.", cuidado: "Q original en W/m³ obtenida por inversión de probetas; se integra a J/m³ (paso 600 s) y se interpola por edad; cola nula tras el registro; ventana inicial omite dos horas. 22A tiene menor confianza. La fuente por edad no incorpora retraso cinético por colocar a 12 °C. Cambiar cp exige revisar la coherencia de Q." });
  tabla(s, [["Propiedad", "Valor", "Origen"], ["ρ", "2476 kg/m³", "fuente"], ["c_p", "1023 J/(kg K)", "fuente"], ["k", "2 W/(m K)", "supuesto"]], { x: 0.6, y: 1.4, w: 5.2, colW: [1.4, 2.1, 1.7], rowH: 0.45 });
  const fv = [["M1_SS", 88.15], ["M2_SS", 95.72], ["M3_SS", 94.15], ["M4_SS", 100.17], ["M1_22A", 61.21], ["M2_22A", 82.45], ["M3_22A", 73.29], ["M4_22A", 73.63]];
  s.addChart(pres.charts.BAR, [{ name: "Energía", labels: fv.map(f => f[0]), values: fv.map(f => f[1]) }], ejes({
    x: 6.2, y: 1.3, w: 6.6, h: 4.2, barDir: "col", chartColors: ["1B74AA", "166C65", "C99A2E", "B54830", "1B74AA", "166C65", "C99A2E", "B54830"],
    valAxisMinVal: 0, valAxisMaxVal: 120, valAxisMajorUnit: 20, showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 12, dataLabelColor: "4A5660", dataLabelFormatCode: "0.0",
    showValAxisTitle: true, valAxisTitle: "MJ/m³ en el registro", barGapWidthPct: 40, varyColors: true,
  }));
  bullets(s, ["Q por edad, común a todas las capas", "M1–M4 = probetas; SS/22A = campañas", "Dosificaciones: correspondencia no confirmada", "22A: menor confianza de ajuste", "Sin retraso cinético por 12 °C"], { x: 0.6, y: 3.45, w: 5.2, h: 2.8, fontSize: 16 });
  etiqueta(s, "no son recetas comerciales seleccionables", 6.2, 5.75, { tipo: "S", w: 6.6 });
}
// B06
{
  const s = consulta("B06", "Qué representan 15 kW y 18 L/min", { quien: "B06 · Referentes Benjamín/Luis", habla: "Preguntas 21–25: enfriar desde el inicio, 15 kW siempre, 18 L/min y 15 kW, agua a 18 °C, cambiar agua/potencia.", fuente: "MODELO_NUEVE_CIRCUITOS.md; esquema.json.", cuidado: "U [W/(m³ K)] es volumétrico, distinto de h [W/(m² K)]. A 162 L/min y 15 kW el aumento medio sería ≈ 1,33 K; no se impone como retorno simulado. No hay salida 23 °C. Agua uniforme 18 °C = reservorio ideal permitido, no resultado de red hidráulica." });
  ecuacion(s, "eq_b06_1", "q_{frío} = \\min\\left(\\sum_{c} U V_c \\max(T - 18, 0),\\ 15\\ \\mathrm{kW}\\right)", { x: 0.6, y: 1.3, w: 8.0, h: 1.0, fontSize: 24, color: K.azul, respaldo: "q_frío = min(Σ U Vc max(T − 18, 0), 15 kW)" });
  T(s, "c: circuitos abiertos · U = 5 W/(m³ K) equivalente · tope conjunto térmico", { x: 0.6, y: 2.45, w: 8, h: 0.35, fontSize: 15, color: K.gris });
  ecuacion(s, "eq_b06_2", "\\Delta T_{agua} = \\frac{P}{\\dot{m} c_{p,agua}} = \\frac{15\\,000}{2{,}7 \\cdot 4186} \\approx 1{,}33\\ \\mathrm{K}", { x: 0.6, y: 2.95, w: 8.0, h: 1.1, fontSize: 24, respaldo: "ΔT_agua = P/(ṁ cp) ≈ 1,33 K" });
  T(s, "balance real de referencia (no impuesto al modelo)", { x: 0.6, y: 4.05, w: 8, h: 0.3, fontSize: 14, color: K.tenue });
  // diagrama de sistema
  const y0 = 4.85;
  const caja = (x, t, c) => { R(s, { x, y: y0, w: 1.55, h: 0.85, fill: { color: c } }, pres.shapes.ROUNDED_RECTANGLE); T(s, t, { x, y: y0, w: 1.55, h: 0.85, fontSize: 14, color: K.blanco, bold: true, align: "center", valign: "middle" }); };
  caja(0.6, "depósito\n18 °C ideal", K.azul); caja(2.65, "bomba", K.gris); caja(4.7, "colector", K.petroleo);
  [[2.15, 2.65], [4.2, 4.7]].forEach(([a, b]) => s.addShape(pres.shapes.LINE, { x: a, y: y0 + 0.42, w: b - a, h: 0, line: { color: K.carbon, width: 2, endArrowType: "triangle" } }));
  for (let i = 0; i < 9; i++) s.addShape(pres.shapes.LINE, { x: 6.25, y: y0 - 0.1 + i * 0.13, w: 1.6, h: 0, line: { color: "39A0E0", width: 1.5 } });
  T(s, "9 ramales × 18 L/min", { x: 6.2, y: y0 + 1.1, w: 2.4, h: 0.3, fontSize: 14, color: K.azul, bold: true });
  s.addShape(pres.shapes.LINE, { x: 5.47, y: y0 + 0.85, w: 0, h: 0.75, line: { color: K.ocre, width: 2, dashType: "dash" } });
  T(s, "bypass de ramales cerrados", { x: 3.0, y: y0 + 1.25, w: 2.4, h: 0.3, fontSize: 13, color: "8A6516", align: "right" });
  // histéresis grande
  T(s, "Regla por circuito", { x: 9.0, y: 1.35, w: 3.8, h: 0.35, fontSize: 16, bold: true, color: K.carbon });
  bullets(s, ["Cerrado antes de cubrir", "Abre: cubierto y mínima monitoreada ≥ 19 °C", "Cierra: algún tramo ≤ 18 °C", "Banda 18–19 °C: conserva estado", "Hormigón entra a 12 °C: no se enfría al inicio"], { x: 9.0, y: 1.8, w: 3.8, h: 3.2, fontSize: 15 });
  etiqueta(s, "U no calibrado; 15 kW no acreditados", 9.0, 5.3, { tipo: "S", w: 3.9, h: 0.55 });
}
// B07
{
  const s = consulta("B07", "Recepción a 12 °C y continuidad entre capas", { quien: "B07 · Referente Benjamín", habla: "Preguntas 12–14, 18: esperas entre capas, ventana de unión, cómo lograr 12 °C, interrupciones.", fuente: "CIERRE_BENJAMIN.md; cronogramas.csv (capa mayor 107,364 m³).", cuidado: "La ventana de 150 min es una condición de aceptación a comprobar, no un ensayo. 338 kW es carga térmica sensible de preenfriamiento, no consumo eléctrico, y distinta de los 15 kW embebidos. Si los preparativos retrasan el inicio, la espera se suma a D." });
  const bx = 0.9, bw = 7.0, by = 1.8, s150 = bw / 160;
  [["capa mayor a 60 m³/h", 107.4, K.petroleo], ["capa mayor a 45 m³/h", 143.2, K.grisMedio]].forEach(([l, v, c], i) => {
    R(s, { x: bx, y: by + i * 1.0, w: v * s150, h: 0.6, fill: { color: c } });
    T(s, `${fmt(v, 1)} min`, { x: bx + v * s150 - 1.75, y: by + i * 1.0, w: 1.6, h: 0.6, fontSize: 20, bold: true, color: K.blanco, align: "right", valign: "middle" });
    T(s, l, { x: bx + 0.12, y: by + i * 1.0, w: 4, h: 0.6, fontSize: 15, color: K.blanco, valign: "middle" });
  });
  s.addShape(pres.shapes.LINE, { x: bx + 150 * s150, y: by - 0.3, w: 0, h: 2.3, line: { color: K.carbon, width: 2, dashType: "dash" } });
  T(s, "ventana exigida 150 min", { x: bx + 150 * s150 - 2.0, y: by - 0.65, w: 2.6, h: 0.3, fontSize: 15, bold: true, color: K.carbon, align: "right" });
  etiqueta(s, "ventana de unión ≥ 150 min: por demostrar", bx, 4.05, { tipo: "C", w: 7 });
  T(s, [{ text: "≈ 338 kW", options: { fontSize: 36, fontFace: FS, color: K.azul } }, { text: "\ncarga sensible térmica 20 → 12 °C a 60 m³/h", options: { fontSize: 15, color: K.gris } }], { x: 8.6, y: 1.5, w: 4.3, h: 1.3 });
  bullets(s, ["Preenfriar agua y agregados (propuesta)", "Medir temperatura por camión", "Dos frentes repiten recorrido y vibran", "Reserva ante interrupción", "Perder aptitud de unión ⇒ revisar junta"], { x: 8.6, y: 3.1, w: 4.3, h: 3.0, fontSize: 15 });
  bullets(s, ["Sin esperas de endurecimiento entre capas", "Etapas endurecidas serían otro plan, con juntas"], { x: 0.9, y: 4.75, w: 7, h: 1.2, fontSize: 16 });
}
// B08
{
  const s = consulta("B08", "Balance discreto, estabilidad y sensibilidad", { quien: "B08 · Referente Luis", habla: "Preguntas 30, 33: certeza y mallas más finas.", fuente: "MODELO_NUEVE_CIRCUITOS.md; sensibilidad_espacial.csv; CONFIRMACION_CIRCUITOS.md.", cuidado: "Caso conocido contra recurrencia Euler independiente; el balance no es un error de temperatura. S25 se reconstruye desde centros y caras; geometría voxelizada y muestreo cerca del tubo son aproximaciones. No es demostración de convergencia." });
  ecuacion(s, "eq_b08_1", "C_i = \\rho c_p V_i \\qquad G_{ij} = \\frac{k A_{ij}}{\\Delta x}", { x: 0.6, y: 1.35, w: 6.4, h: 0.9, fontSize: 24, respaldo: "Ci = ρ cp Vi;  Gij = k Aij / Δx" });
  ecuacion(s, "eq_b08_2", "T_i^{n+1} = T_i^n + \\frac{\\Delta t}{C_i}\\left[\\sum_j G_{ij}(T_j^n - T_i^n) + Q_i + q_b - q_f\\right]", { x: 0.6, y: 2.3, w: 6.4, h: 1.0, fontSize: 21, respaldo: "Ti(n+1) = Ti(n) + Δt/Ci [Σ Gij (Tj − Ti) + Qi + qb − qf]" });
  ecuacion(s, "eq_b08_3", "\\Delta t \\leq 0{,}8\\, \\frac{C_i}{\\sum_j G_{ij}},\\quad \\Delta t \\leq 300\\ \\mathrm{s}", { x: 0.6, y: 3.35, w: 6.4, h: 0.95, fontSize: 22, color: K.petroleo, respaldo: "Δt ≤ 0,8 Ci/ΣGij,  Δt ≤ 300 s" });
  tabla(s, [["Volumen", "m³"], ["IFC", "636,775"], ["voxel 0,40 m", "640,704"], ["voxel 0,20 m", "638,944"], ["zona de frío (conservada)", "414,016"]], { x: 0.6, y: 4.5, w: 6.4, colW: [4.0, 2.4], rowH: 0.38 });
  const sv = D.sensibilidad.map(r => +r.cambio_DeltaTmax_K);
  s.addChart(pres.charts.BAR, [{ name: "cambio ΔTmax 0,20 − 0,40 m", labels: D.sensibilidad.map(r => `${r.curva.replace("_", " ")} ${r.clima.slice(-2)}`), values: sv }], ejes({
    x: 7.3, y: 1.3, w: 5.6, h: 4.9, barDir: "bar", chartColors: [K.violeta], valAxisMinVal: -0.6, valAxisMaxVal: 0.8, valAxisMajorUnit: 0.2,
    catAxisLabelFontSize: 10, valAxisLabelFontSize: 12, catAxisLabelPos: "low", catAxisLabelFrequency: 1, showValAxisTitle: true, valAxisTitle: "cambio emparejado de ΔTmax [K]", valAxisLabelFormatCode: "0.0", barGapWidthPct: 35,
  }));
  T(s, "24 pares de la candidata · temporal aparte: 3 pares, ≤ 0,0038 K", { x: 7.3, y: 6.25, w: 5.6, h: 0.3, fontSize: 13, color: K.tenue });
}
// B09
{
  const s = consulta("B09", "Una fila, la unión de límites y los pesos", { quien: "B09 · Referente Matías", habla: "Preguntas 28–30: pesos iguales, ¿una falla ya incumple?, ¿0/24 es certeza?", fuente: "evidencia_circuitos/escenarios.csv (q60, 0,40 m, 600 h, M4_SS × ERA5-2024); sensibilidad_pesos.csv.", cuidado: "Los ejemplos 1/24 y 2/24 son aritméticos, no fallas observadas. Reponderar años o conservar solo SS mantiene 0 % en este catálogo; no incorpora climas extremos omitidos. No añadir intervalo binomial: no son 24 ensayos independientes de obra." });
  const f = D.fila_b09;
  tabla(s, [["Curva", "Clima", "Peso", "Tmax [°C]", "ΔTmax [K]", "I_T", "I_Δ", "I_F"],
    ["M4_SS", "ERA5-2024", "1/24", fmt(f.Tmax_C, 2), fmt(f.DeltaTmax_K, 2), f.I_T, f.I_delta, f.I_union]], { x: 0.6, y: 1.45, w: 12.1, rowH: 0.5 });
  T(s, "fila real · plan 60 · 0,40 m / 300 s · 600 h", { x: 0.6, y: 2.5, w: 8, h: 0.3, fontSize: 13, color: K.tenue });
  ecuacion(s, "eq_b09", "P_f = \\sum_{s=1}^{24} w_s\\, I(F_s), \\qquad w_s = \\frac{1}{24}", { x: 0.6, y: 3.0, w: 7.0, h: 1.2, fontSize: 28, color: K.petroleo, respaldo: "Pf = Σ ws I(Fs), ws = 1/24" });
  T(s, "Si una corrida excede ambos límites, cuenta una sola vez", { x: 0.6, y: 4.6, w: 7, h: 0.4, fontSize: 17, color: K.carbon });
  R(s, { x: 7.95, y: 3.0, w: 4.75, h: 2.2, fill: { color: "ECE7F1" } }, pres.shapes.ROUNDED_RECTANGLE);
  T(s, "EJEMPLO ARITMÉTICO", { x: 8.15, y: 3.1, w: 4.4, h: 0.3, fontSize: 12, bold: true, color: K.violeta, charSpacing: 1 });
  T(s, [{ text: "1/24 = 4,167 %  ≤ 5 %\n", options: { color: K.petroleo } }, { text: "2/24 = 8,333 %  > 5 %", options: { color: K.rojo } }], { x: 8.15, y: 3.5, w: 4.4, h: 1.0, fontSize: 22, fontFace: FS });
  T(s, "no son fallas observadas", { x: 8.15, y: 4.6, w: 4.4, h: 0.3, fontSize: 13, color: K.tenue });
  tabla(s, [["Pesos", "publicados", "solo SS", "doble 2023", "doble 2024", "doble 2025"], ["P_f", "0 %", "0 %", "0 %", "0 %", "0 %"]], { x: 0.6, y: 5.55, w: 12.1, rowH: 0.42 });
}
// B10
{
  const s = consulta("B10", "Comparación completa y máximos identificados", { quien: "B10 · Referentes Matías/Luis", habla: "Preguntas 31, 32: ¿por qué no 75 m³/h? ¿por qué no más lento?", fuente: "comparacion_planes.csv; figuras/07_cortes_comunes.png (escala común 8–35 °C).", cuidado: "La fila fina 0,20 m es solo de la candidata 60; no es una quinta fila homogénea. Los seis refinos de alternativas (55/50/45, dos pares por tasa, máx. 19,4666 K) son selectivos, no matrices completas. Figura 05 (24 curvas por duración) disponible como archivo complementario." });
  const filas = [["Plan", "Malla", "D [h]", "Tmax [°C]", "ΔT 14 d [K]", "ΔT 25 d [K]", "P_f"]];
  ["q60", "q55", "q50", "q45"].forEach(q => {
    const a = P[`${q}_0.4_336`], b = P[`${q}_0.4_600`];
    filas.push([q.slice(1) + " m³/h", "0,40 m", fmt(a.D_h, 2), fmt(a.Tmax_C, 2), fmt(a.DeltaTmax_K, 2), fmt(b.DeltaTmax_K, 2), "0 %"]);
  });
  const a = P["q60_0.2_336"], b = P["q60_0.2_600"];
  filas.push(["60 m³/h · fina", "0,20 m", fmt(a.D_h, 2), fmt(a.Tmax_C, 2), fmt(a.DeltaTmax_K, 2), fmt(b.DeltaTmax_K, 2), "0 %"].map(t => ({ text: t, options: td({ color: K.petroleo, bold: true, fill: { color: "E3F0EE" } }) })));
  tabla(s, filas, { x: 0.6, y: 1.35, w: 12.1, rowH: 0.4 });
  T(s, "24 pares por plan · 600 h · la fila fina confirma solo la candidata", { x: 0.6, y: 3.85, w: 12, h: 0.3, fontSize: 13, color: K.tenue });
  s.addImage({ path: path.join(RAIZ, "entregas/F02/evidencia_circuitos/figuras/07_cortes_comunes.png"), x: 0.6, y: 4.2, w: 9.6, h: 9.6 * 624 / 2224 });
}
// B11
{
  const s = consulta("B11", "Medición y respuesta a desviaciones", { quien: "B11 · Referente Benjamín", habla: "Preguntas 18, 26, 35: interrupción, apagado, qué invalidaría la recomendación.", fuente: "CIERRE_BENJAMIN.md.", cuidado: "Sensores propuestos, no instalados. Umbrales operativos propuestos, no normas. Cambios de control requieren nueva evaluación y no heredan la matriz nominal. No hay fecha definitiva de apagado ni de carga." });
  const g = { x0: 0.8, yb: 5.6, sx: 0.36, sz: 0.36 * 1.6 };
  seccion(s, Object.assign({ colores: K.hormigon, borde: "E9E6DF" }, g));
  [[0, 2.5, K.rojo], [0, 4.0, K.rojo], [-8.9, 0.6, K.azul], [8.9, 0.6, K.azul], [-3.3, 3.8, K.azul], [-4.5, 0.5, K.petroleo], [3.0, 1.5, K.petroleo], [1.5, 2.5, K.petroleo], [-1.0, 3.8, K.petroleo]]
    .forEach(([xm, zm, c]) => s.addShape(pres.shapes.OVAL, { x: X(g, xm) - 0.1, y: Z(g, zm) - 0.1, w: 0.2, h: 0.2, fill: { color: c }, line: { color: K.blanco, width: 1.5 } }));
  T(s, [{ text: "● núcleo y pedestal   ", options: { color: K.rojo } }, { text: "● contorno S25   ", options: { color: K.azul } }, { text: "● ramales", options: { color: K.petroleo } }], { x: 0.8, y: 5.85, w: 6.6, h: 0.3, fontSize: 14 });
  T(s, "+ ambiente y agua · redundancia · adquisición 1 min, archivo ≤ 5 min", { x: 0.8, y: 6.2, w: 6.6, h: 0.3, fontSize: 13, color: K.gris });
  tabla(s, [["Nivel", "Tmax", "ΔT"], [{ text: "Advertencia", options: td({ color: "8A6516", bold: true }) }, "65 °C", "18 K"], [{ text: "Intervención", options: td({ color: K.rojo, bold: true }) }, "68 °C", "19 K"]],
    { x: 7.8, y: 1.4, w: 5.0, colW: [2.0, 1.5, 1.5], rowH: 0.45 });
  etiqueta(s, "umbrales operativos propuestos", 7.8, 2.85, { tipo: "C", w: 5 });
  bullets(s, ["Detener retiros y actualizar predicción", "Dato de circuito perdido: cerrar ramal, usar bypass", "Pérdida de frío: activar reservas", "Cambiar control ⇒ nueva evaluación"], { x: 7.8, y: 3.4, w: 5.0, h: 2.6, fontSize: 16 });
}
// B12
{
  const s = consulta("B12", "Alcance, trazabilidad y qué no se ha validado", { quien: "B12 · Los tres", habla: "Preguntas 34, 35: ¿cumplir 20 K demuestra que no se agrieta? ¿qué invalidaría la recomendación?", fuente: "Repositorio: github.com/benjagarciag/Proyecto-2-MCOC.", cuidado: "SHA FINAL DE DEFENSA: POR CONFIRMAR (no mostrar un SHA no confirmado en pantalla). Los commits de Luis y Matías identifican antecedentes, no el SHA final. El IFC conserva propiedades de práctica; el plan externo fija 12 °C y cronograma: no afirmar que fue reescrito. No se resolvieron tensiones, restricción, fluencia ni resistencia a tracción." });
  const cols = [
    ["Verificado", K.petroleo, ["Conservación de energía", "Caso conocido (recurrencia independiente)", "Auditoría: 5 matrices, 4.700 transiciones"]],
    ["Sensibilidad", K.azul, ["Malla 0,40 → 0,20 m (24 pares)", "Paso 300 → 150 s (3 pares)", "Pesos reponderados: 0 %"]],
    ["No validado", K.rojo, ["Fuente por edad sin cinética de T", "Suelo sin inercia · sin radiación", "Agua 18 °C y U sin calibrar", "Exposición y clima incompletos", "Tensiones y fisuración"]],
  ];
  cols.forEach(([t, c, items], i) => {
    const x = 0.6 + i * 4.1;
    R(s, { x, y: 1.4, w: 3.9, h: 0.55, fill: { color: c } }, pres.shapes.ROUNDED_RECTANGLE);
    T(s, t, { x, y: 1.4, w: 3.9, h: 0.55, fontSize: 18, bold: true, color: K.blanco, align: "center", valign: "middle" });
    bullets(s, items, { x: x + 0.1, y: 2.15, w: 3.7, h: 3.4, fontSize: 16 });
  });
  T(s, "IFC sin reescribir: 12 °C y cronograma son del plan externo · 5 objetos IFC ≠ 11 capas", { x: 0.6, y: 5.75, w: 12.1, h: 0.35, fontSize: 15, color: K.gris });
  T(s, "github.com/benjagarciag/Proyecto-2-MCOC", { x: 0.6, y: 6.25, w: 6, h: 0.35, fontSize: 15, color: K.petroleo, hyperlink: { url: "https://github.com/benjagarciag/Proyecto-2-MCOC" } });
}

// ------------------------------------------------------------------ salida
fs.writeFileSync(path.join(REC, "animaciones.json"), JSON.stringify({ anim: ANIM, eq: EQ, trans: TRANS }, null, 1));
pres.writeFile({ fileName: SALIDA }).then(f => console.log("PPTX base:", f, "diapositivas:", nSlide));
