import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,PresentationFile} from 'file:///C:/Users/benja/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
try{
 const root=process.cwd(),work=path.join(root,'.venv/cache/pre_entrega_f02');
 const input=process.argv[2]||path.join(work,'F02_Grupo6_radiacion_actualizada.pptx');
 const label=process.argv[3]||'fuente';
 const p=await PresentationFile.importPptx(new FileBlob(new Uint8Array(await fs.readFile(input)),'application/vnd.openxmlformats-officedocument.presentationml.presentation'));
 const inspeccion=await p.inspect({kind:'slide,textbox,chart,table,layout',maxChars:500000});
 await fs.writeFile(path.join(work,`inspeccion_${label}.json`),JSON.stringify(inspeccion,null,2));
 const dir=path.join(work,label);await fs.mkdir(dir,{recursive:true});
 for(let i=0;i<p.slides.items.length;i++){
  const png=await p.export({slide:p.slides.items[i],format:'png',scale:label==='fuente'?1:2});
  await fs.writeFile(path.join(dir,`slide${i+1}.png`),png.data||new Uint8Array(await png.arrayBuffer()));
 }
 console.log('Importadas y renderizadas',p.slides.items.length,'láminas:',label);
}catch(e){console.error(e.stack);process.exitCode=1;}
