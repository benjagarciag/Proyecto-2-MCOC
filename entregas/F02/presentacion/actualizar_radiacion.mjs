// Edición de texto del deck existente con Artifact Tool.
// El postproceso conserva el paquete original y sus animaciones, que un
// roundtrip de importación/exportación no conserva.
import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,PresentationFile} from 'file:///C:/Users/benja/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const root=process.cwd(),dir=path.join(root,'.venv/cache/f02_radiacion_presentacion');
try {
const d=JSON.parse(await fs.readFile(path.join(root,'entregas/F02/presentacion/recursos/contenido_radiacion.json'),'utf8'));
const source=path.join(root,'entregas/F02/presentacion/F02_Grupo6_presentacion.pptx');
const p=await PresentationFile.importPptx(new FileBlob(new Uint8Array(await fs.readFile(source)),'application/vnd.openxmlformats-officedocument.presentationml.presentation'));
const inspected=await p.inspect({kind:'textbox',maxChars:300000});
const records=inspected.records;const edits=[];
const fmt=(x,n=2)=>x.toFixed(n).replace('.',',');
function replace(slide,name,find,value){
 const r=records.find(r=>r.slideIndex===slide-1&&r.name===name);
 if(!r)throw Error(`No se encontró ${slide}/${name}`);
 if(!r.text.includes(find))throw Error(`Texto distinto en ${slide}/${name}: ${find}`);
 p.resolve(r.id).text.replace(find,value);r.text=r.text.replace(find,value);
 if(!edits.some(e=>e.slide===slide&&e.name===name))edits.push({slide,name});
}
replace(1,'s1_res','escenarios exceden los límites en el modelo','excedencias en 14 días con radiación');
replace(2,'Text 0','El interior y el contorno no se enfrían al mismo ritmo','Generación de calor e intercambio con el ambiente');
replace(2,'s2_aireT','aire y viento · h(t)','viento · h(t)');
replace(2,'s2_aireT','intercambio','solar + onda larga');
replace(2,'Text 31','almacena = conduce + genera − extrae','Borde: convección + solar + onda larga');
replace(3,'s3_cifra2','tope térmico conjunto','tope global equivalente');
replace(3,'s3_sup','agua 18 °C ideal','agua 18 °C / Uv equivalente');
replace(3,'s3_hl5','abre: cubierto y mínima ≥ 19 °C · cierra: algún tramo ≤ 18 °C','Abre: cubierto y Tmin ≥ 19 °C\nCierra: algún tramo ≤ 18 °C');
replace(5,'Text 0','El mayor diferencial aparece después del pico de temperatura','Temperaturas con radiación durante los 14 días');
replace(5,'Text 1','M4_SS × ERA5-2024 · base común 0,40 m / 300 s','M4_SS × ERA5-2024 · solar + LW · 0,40 m / 300 s');
replace(5,'s5_pico','pico 45,7 °C\n≈ 127 h','pico 46,7 °C\n≈ 128 h');
replace(5,'s5_428','428 h ≈ 17,8 días','267 h ≈ 11,1 días');
replace(5,'s5_resta','28,70','42,12');replace(5,'s5_resta','9,34','25,59');replace(5,'s5_resta','19,36 K','16,53 K');
replace(5,'s5_corteT','corte y = 0 · misma corrida','centros de celda · evento 267 h');
replace(5,'s5_fino','confirmación fina del catálogo: ΔTmax 19,17 K',`catálogo fino a 14 d: ΔTmax ${fmt(d.fina.Delta)} K`);
replace(6,'s6_cat','en el catálogo','catálogo de 14 días');
replace(6,'s6_climaU','aire [°C] · 0–336 h','aire [°C] · misma historia radiativa');
replace(7,'s7_tablaT','mismos controles · 24 pares por plan · 0,40 m / 300 s · horizonte 600 h','solar + onda larga · 24 pares/plan · 0,40 m / 300 s · 336 h');
replace(8,'Text 3','Confirmación fina 0,20 m: ', 'Catálogo fino 0,20 m · 14 días: ');
replace(8,'Text 3','46,02 °C · 19,17 K · 0/24 excedencias',`${fmt(d.fina.Tmax)} °C · ${fmt(d.fina.Delta)} K · 0/24 excedencias`);
replace(8,'Text 7','ΔTmax 19,17 K',`ΔTmax ${fmt(d.fina.Delta)} K`);
replace(8,'Text 8','20 K · margen ≈ 0,83 K',`20 K · margen ≈ ${fmt(20-d.fina.Delta)} K`);
replace(8,'s8_cond','Cambia suministro, clima o frío ','Cambia clima, exposición o frío ');
replace(8,'s8_lim','agua 18 °C y transferencia equivalente idealizadas','Uv sin calibrar y propiedades radiativas supuestas');
replace(9,'Text 5','Viento y clima histórico','Viento, clima y radiación');
replace(11,'Text 0','Viento y clima histórico','Viento, clima y radiación');
replace(11,'Text 7','descarga 17-11-2026, UTC','aire/viento 17-11 y radiación 18-11-2026, UTC');
replace(11,'Text 7','Se usan 0–600 h; sin faltantes','Ventana común 0–336 h; sin faltantes');
replace(12,'Text 0','Balance continuo y condiciones de borde','Balance exterior con solar y onda larga');
replace(12,'Text 7','Una cara cubierta deja de llevar Robin y pasa a conducir\nFuente volumétrica ≠ intercambio superficial\nNormal saliente n',"q'' positivo hacia el hormigón\nTs: exterior de protección · Ti: centro de celda\nT⁴ en kelvin · α = 0,6 · ε = 0,9");
replace(13,'Text 11','calendario nominal por edad local','edades locales: la última manta se retira después de 14 días');
replace(15,'Text 5','c: circuitos abiertos · U = 5 W/(m³ K) equivalente · tope conjunto térmico','i: celdas de ramales abiertos · Uv = 5 W/(m³ K), equivalente');
replace(15,'Text 30','U no calibrado; 15 kW no acreditados','sin pared de tubo ni agua axial resueltas');
replace(17,'Text 7','24 pares de la candidata · temporal aparte: 3 pares, ≤ 0,0038 K',`24 pares con radiación · temporal: 3 pares, ≤ ${fmt(d.resumen.max_cambio_temporal_Delta,4)} K`);
replace(18,'Text 4','fila real · plan 60 · 0,40 m / 300 s · 600 h','fila real con radiación · plan 60 · 0,40 m / 300 s · 336 h');
replace(19,'Text 4','24 pares por plan · 600 h · la fila fina confirma solo la candidata','24 pares por plan a 336 h · la fila fina confirma solo la candidata');
replace(21,'Text 6','Auditoría: 5 matrices, 4.700 transiciones','Auditoría: 5 matrices, 129 piezas con radiación');
replace(21,'Text 12','Suelo sin inercia · sin radiación','Suelo sin inercia · α/ε supuestas');
replace(21,'Text 12','Agua 18 °C y U sin calibrar','Agua 18 °C y Uv sin calibrar');
replace(21,'Text 12','Exposición y clima incompletos','Sin sombras ni pared de tubo resueltas');
replace(21,'Text 12','Tensiones y fisuración','Tensiones y fisuración\nRetiros posteriores: ΔT > 20 K observado');
const exported=await PresentationFile.exportPptx(p);await fs.mkdir(dir,{recursive:true});
await fs.writeFile(path.join(dir,'borrador_actualizado_artifact.pptx'),exported.data);
await fs.writeFile(path.join(dir,'ediciones.json'),JSON.stringify(edits,null,2));
console.log('Artifact Tool actualizó',edits.length,'objetos de texto');
}catch(e){console.error(e.message);process.exitCode=1;}
