import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,PresentationFile} from 'file:///C:/Users/benja/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const w=path.join(process.cwd(),'.venv/cache/bordes_f02'),a=path.join(process.cwd(),'entregas/F02/presentacion');
const d=JSON.parse(await fs.readFile(path.join(w,'contenido.json'),'utf8'));
const p=await PresentationFile.importPptx(new FileBlob(new Uint8Array(await fs.readFile(path.join(a,'F02_Grupo6_Pre_entrega.pptx'))),'application/vnd.openxmlformats-officedocument.presentationml.presentation'));
const {records}=await p.inspect({kind:'textbox,layout',maxChars:500000});await fs.writeFile(path.join(w,'layout_antes.json'),JSON.stringify(records));
for(const [slide,name,value] of [[12,'Text 0',d.titulo],[12,'Text 7',d.pie],[9,'Text 7',d.indice]]){const r=records.find(x=>x.slideIndex===slide-1&&x.name===name);if(!r)throw Error(name);p.resolve(r.id).text.replace(r.text,value);}
const result=await PresentationFile.exportPptx(p);await fs.writeFile(path.join(w,'artifact.pptx'),result.data||new Uint8Array(await result.arrayBuffer()));
console.log('Autoría Artifact terminada');
