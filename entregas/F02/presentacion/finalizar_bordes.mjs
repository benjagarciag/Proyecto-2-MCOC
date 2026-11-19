import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {FileBlob,PresentationFile} from 'file:///C:/Users/benja/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
process.env.RUNTIME_NODE_MODULES='C:/Users/benja/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const SKILL='C:/Users/benja/.codex/plugins/cache/openai-primary-runtime/presentations/26.1117.11355/skills/presentations';
const PYTHON='C:/Users/benja/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
try {
const {finalizePresentation}=await import(`file:///${SKILL}/container_tools/artifact_tool_utils.mjs`);
const root=process.cwd(),work=path.join(root,'.venv/cache/bordes_f02');
const output=path.join(root,'entregas/F02/presentacion/F02_Grupo6_Condiciones_borde.pptx');
const original=path.join(work,'source.pptx');
await finalizePresentation({workspaceDir:root,candidatePath:path.join(work,'candidate.pptx'),finalPath:output,
 explicitTotalSlideCount:24,requiredNativeTableOwnerSlides:[4,7,10,12,13,14,17,18,19,20,22,23,24],
 requiredNativeChartOwnerSlides:[5,6,7,14,17],requiredEmbeddedWorkbookChartOwnerSlides:[5,6,7,14,17],
 pythonExecutable:PYTHON,integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',
 ...[4,7,10,12,13,14,17,18,19,20,22,23,24].flatMap(n=>['--require-native-table-slide',String(n)])],
 fontPolicy:{basis:'reference',families:['Segoe UI','Segoe UI Semibold','Cambria Math','Arial'],referencePath:original,
 referenceSha256:createHash('sha256').update(await fs.readFile(original)).digest('hex')},
 verifyArtifactToolImport:true,receiptPath:path.join(work,'validacion_bordes.json')});
console.log('PowerPoint final:',output);
const pres=await PresentationFile.importPptx(new FileBlob(new Uint8Array(await fs.readFile(output)),'application/vnd.openxmlformats-officedocument.presentationml.presentation'));
const finalPdf=output.replace(/\.pptx$/,'.pdf');
try {
 const pdf=await pres.export({format:'pdf'});
 await fs.writeFile(finalPdf,pdf.data||new Uint8Array(await pdf.arrayBuffer()));
}catch(e){
 console.log('PDF nativo no disponible:',e.message.split('\n')[0]);
 const pngDir=path.join(work,'artifact_actualizado');await fs.mkdir(pngDir,{recursive:true});
 for(let i=0;i<pres.slides.items.length;i++){
  const png=await pres.export({slide:pres.slides.items[i],format:'png',scale:2});
  await fs.writeFile(path.join(pngDir,`slide${i+1}.png`),png.data||new Uint8Array(await png.arrayBuffer()));
 }
 const result=spawnSync(PYTHON,['-X','utf8',path.join(root,'entregas/F02/presentacion/exportar_pdf_pre_entrega.py'),output,pngDir,finalPdf],{encoding:'utf8'});
 if(result.status!==0)throw Error(result.stderr||result.error||'Falló exportación estática');
 console.log(result.stdout.trim());
}
console.log('PDF final:',finalPdf);
}catch(e){console.error(e.message);process.exitCode=1;}
