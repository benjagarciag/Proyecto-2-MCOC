import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,PresentationFile} from 'file:///C:/Users/benja/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const w=path.join(process.cwd(),'.venv/cache/f02_final_ecuaciones'),a=path.join(process.cwd(),'entregas/F02/presentacion');

const p=await PresentationFile.importPptx(new FileBlob(new Uint8Array(await fs.readFile(path.join(w,'source.pptx'))),'application/vnd.openxmlformats-officedocument.presentationml.presentation'));
for(const i of [8,22]){const png=await p.export({slide:p.slides.items[i],format:'png',scale:1});await fs.writeFile(path.join(w,`fuente_${i+1}.png`),png.data||new Uint8Array(await png.arrayBuffer()));}
const {records}=await p.inspect({kind:'textbox,layout',maxChars:500000});await fs.writeFile(path.join(w,'layout_antes.json'),JSON.stringify(records));
for(const [name,value] of [['Text 0','Ecuaciones del modelo'],['Text 7','Flujo positivo hacia el hormigón · Ts: exterior de la protección · temperaturas radiativas en kelvin.']]){const r=records.find(x=>x.slideIndex===22&&x.name===name);if(!r)throw Error(name);p.resolve(r.id).text.replace(r.text,value);}
const result=await PresentationFile.exportPptx(p);await fs.writeFile(path.join(w,'artifact.pptx'),result.data||new Uint8Array(await result.arrayBuffer()));
console.log('Autoría Artifact terminada');
