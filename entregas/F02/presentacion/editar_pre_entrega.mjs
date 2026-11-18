// Autoría sobre el PPTX existente mediante Artifact Tool. El postproceso
// reintegra los párrafos al paquete fuente para preservar animaciones.
import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,PresentationFile} from 'file:///C:/Users/benja/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
try{
 const root=process.cwd(),w=path.join(root,'.venv/cache/pre_entrega_f02');
 const input=path.join(w,'F02_Grupo6_radiacion_actualizada.pptx');
 const p=await PresentationFile.importPptx(new FileBlob(new Uint8Array(await fs.readFile(input)),'application/vnd.openxmlformats-officedocument.presentationml.presentation'));
 const {records}=await p.inspect({kind:'textbox',maxChars:500000});const edits=[];
 function set(slide,name,value){const r=records.find(x=>x.slideIndex===slide-1&&x.name===name);if(!r)throw Error(`${slide}/${name}`);p.resolve(r.id).text.replace(r.text,value);edits.push({slide,name});}
 set(1,'s1_res','0 / 24\nexcedencias a 14 y 28 días con radiación');
 set(3,'s3_sup','PROTECCIÓN ADOPTADA\nÚltima manta: 504 h de edad local\nDespués: sombra solar 90 % (τ = 0,10)');
 set(3,'Text 13','Secuencia esquemática · capas activadas al inicio · vertical ×1,6\nt₀: 19/11/2026 10:00 UTC−03:00');
 set(4,'s4_chk','✓ Balance: residuo ≤ 0,00025 J    ✓ Seno 1D: error ≤ 0,00258 K');
 set(5,'Text 0','Temperaturas y protección hasta los 28 días');
 set(5,'Text 1','M4_SS × ERA5-2024 · manta 504 h + sombra 90 % · 0,40 m / 300 s');
 set(5,'s5_fino','RESULTADO CALCULADO\n24 pares finos hasta 672 h: ΔTmax 15,72 K\nSombra posterior al retiro local de 504 h');
 set(6,'s6_cat','catálogo de 14 y 28 días');
 set(6,'s6_climaU','aire [°C] · historia completa 0–672 h');
 set(7,'s7_tablaT','Manta 504 h + sombra 90 % · 24 pares/plan\n0,40 m / 300 s · 336 y 672 h · >60 fuera de recursos');
 set(7,'s7_gl2','No existe una opción más rápida admisible');
 set(7,'s7_gD2','D < 10,61 h exigiría superar 60 m³/h');
 set(7,'s7_gl3','Una vertida continua = propuesta de 11 capas');
 set(7,'s7_gD3','t₀: 19/11/2026 10:00 UTC−03:00');
 set(8,'Text 2','60 m³/h · 12 °C · 9 circuitos · manta 504 h + sombra 90 %');
 set(8,'Text 3','Catálogo fino 0,20 m · 14 y 28 días: \n47,03 °C · 15,72 K · 0/24 excedencias');
 set(8,'s8_lim','LIMITACIÓN  Uv y sombra idealizados; sin validación en obra');
 set(8,'Text 34','Preguntas · consulta B01–B15');
 set(9,'Text 9','B04   Protecciones y retiro\nBenjamín');
 set(11,'Text 7','ERA5 vía Open-Meteo · descargas 17/18-11-2026 UTC\nSitio solicitado −37,277929 / −72,368271\nCelda devuelta −37,25 / −72,25\nVentana 0–672 h; sin faltantes\nHistórico ≠ pronóstico de obra 2026');
 set(13,'Text 0','Protecciones y retiro condicionado');
 set(13,'Text 10','2.ª manta 504 h');
 set(13,'Text 11','Madera 18 mm / k 0,158 · dos mantas 40 mm / k 0,042\nTras retirar la última: sombra solar 90 %; h y onda larga conservados\nEdades locales · cronología esquemática · cubierta hasta 672 h');
 set(14,'Text 4','Q por edad, común a todas las capas\nProbetas M1–M4; campañas SS / 22A\nDosificaciones no confirmadas; 22A menor confianza\nQ [W/m³] → acumulado por trapecios de 600 s\nAcumulado lineal; energía integrada por paso\nCola nula tras 240,33 h SS / 163 h 22A: supuesto\nSin cinética dependiente de temperatura');
 set(16,'Text 8','117,1 min');set(16,'Text 9','capa mayor a 55 m³/h');
 set(17,'Text 7','24 pares · 672 h · máximo |Δespacial| 0,882 K\nTiempo: 2 pares, cambio ≤ 0,0014 K');
 set(18,'Text 4','Final y contraste sombra sola · 0,40 m / 300 s · 672 h · no sumar planes');
 set(18,'Text 10','Ejemplos aritméticos, no suma de las filas');
 set(19,'Text 4','24 pares por fila hasta 672 h; también cumplen a 336 h · fina completa solo propuesta');
 set(20,'Text 25','+ ambiente, caudal y agua entrada/retorno · verificar sombra · adquisición 1 min, archivo ≤ 5 min');
 set(21,'Text 6','Conservación: residuo ≤ 0,00025 J\nSeno 1D: error 0,002571 K; 24 tests\nAuditoría: 3 matrices, 72 piezas, 2.045 transiciones');
 set(21,'Text 9','Espacio: 24 pares hasta 672 h, ≤ 0,882 K\nTiempo: 2 pares, ≤ 0,0014 K\nPesos reponderados: 0 %');
 set(21,'Text 12','Fuente por edad; cola nula supuesta\nSuelo sin inercia; α/ε supuestas\nAgua 18 °C y Uv sin calibrar\nCubierta real y efecto sobre h / IR\nRetiro de sombra / apagado definitivo\nTensiones y fisuración');
 const draft=await PresentationFile.exportPptx(p);
 await fs.writeFile(path.join(w,'artifact_editado.pptx'),draft.data);
 await fs.writeFile(path.join(w,'ediciones.json'),JSON.stringify(edits,null,2));
 console.log('Artifact Tool editó',edits.length,'objetos, conservando estructura fuente');
}catch(e){console.error(e.stack);process.exitCode=1;}
