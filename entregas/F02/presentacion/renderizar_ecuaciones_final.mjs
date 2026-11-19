import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {FileBlob,PresentationFile} from 'file:///C:/Users/benja/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
process.env.RUNTIME_NODE_MODULES='C:/Users/benja/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const SKILL='C:/Users/benja/.codex/plugins/cache/openai-primary-runtime/presentations/26.1117.11355/skills/presentations';
const PYTHON='C:/Users/benja/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
try {
const root=process.cwd(),work=path.join(root,'.venv/cache/f02_final_ecuaciones'),output=path.join(work,'candidate.pptx');
const pres=await PresentationFile.importPptx(new FileBlob(new Uint8Array(await fs.readFile(output)),'application/vnd.openxmlformats-officedocument.presentationml.presentation'));
const dir=path.join(work,'render_final');await fs.mkdir(dir,{recursive:true});
for(const i of [8,22,24]){const png=await pres.export({slide:pres.slides.items[i],format:'png',scale:2});await fs.writeFile(path.join(dir,`slide${i+1}.png`),png.data||new Uint8Array(await png.arrayBuffer()));}
console.log('Renderizadas las láminas de comprobación.');
}catch(e){console.error(e.message);process.exitCode=1;}
