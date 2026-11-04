/* Opcional: node desarrollo/tests/test_e07_termico_web.cjs. Sin paquetes npm. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(process.argv[2]||path.resolve(__dirname,'../..'));
const source=fs.existsSync(path.join(root,'Visualizadores/e07_termico.js'))?path.join(root,'Visualizadores'):root;
const {solveVoxelHeat}=require(path.join(source,'e07_termico.js'));
const html=fs.readFileSync(path.join(source,'E07.html'),'utf8');
const DATA=JSON.parse(html.match(/<script id="e07-data" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const script=html.match(/<script>\s*([\s\S]*?)<\/script>/)[1];new vm.Script(script);
const core=script.split('// BEGIN_CORE:')[1].split('\n').slice(1).join('\n').split('// END_CORE')[0];
const context=vm.createContext({DATA});vm.runInContext(core+';globalThis.api={decode,statistics,activeIds,playbackTime};',context);
const {decode,statistics,activeIds,playbackTime}=context.api;
const near=(a,b,tol=1e-6)=>assert(Math.abs(a-b)<=tol,`${a} != ${b} (tol ${tol})`);
const bc=type=>Array.from({length:6},()=>({type,value:type==='N'?0:10,h:10}));
const defaults={k:2,rho:2400,cp:900,q:0,duration:1,horizon:3,dtCap:900,sourceMode:'pulse',sourceId:0,bc:bc('N'),observe:[.5,.5,.5]};
const small=(ids=[1],forma=[1,1,1],vertidas=[{id:1,inicio:0,temperatura:20}])=>({g:{ids:Uint8Array.from(ids),forma,h:1,origen:[0,0,0]},vertidas});
function run(data=small(),p={}){const r=solveVoxelHeat({...data,p:{...defaults,...p}});const scale=Math.max(1,Math.abs(r.energyIn),r.energySource,Math.abs(r.energyBoundary));assert(Math.abs(r.balance)/scale<1e-11,'Balance de energía');assert(r.history.every(h=>h.rate===null||Math.abs(h.rate-h.cond-h.border-h.internal)<1e-12));return r;}
let r=run();near(r.peak.value,20);near(r.trough.value,20);near(r.fields[r.fields.length-1],20);console.log('OK aislado: temperatura uniforme constante.');
r=run(small(),{q:600});near(r.history.at(-1).mean,21,1e-10);near(r.energySource,600*3600,1e-5);console.log('OK calor interno: aumento q·t/(ρcp), corte exacto al terminar el pulso.');
r=run(small(),{horizon:1,bc:Array.from({length:6},()=>({type:'N',value:100,h:0}))});near(r.history.at(-1).mean,21,1e-10);console.log('OK Neumann: flujo positivo entrante calienta.');
r=run(small(),{horizon:1,bc:Array.from({length:6},()=>({type:'N',value:-100,h:0}))});near(r.history.at(-1).mean,19,1e-10);console.log('OK Neumann: flujo negativo enfría.');
for(const type of ['D','R']){r=run(small(),{horizon:1,bc:bc(type)});const H=type==='D'?4:1/(.25+.1),exact=10+10*Math.exp(-6*H*3600/(2400*900));near(r.history.at(-1).mean,exact,.0001);assert(r.history.at(-1).mean<20);if(type==='D')near(r.trough.value,10);console.log(`OK ${type}: solución exponencial de una celda y reconstrucción de borde.`);}
r=run(small(),{bc:Array.from({length:6},()=>({type:'R',value:-20,h:0}))});near(r.history.at(-1).mean,20);console.log('OK Robin h=0 equivale a aislamiento.');
const pair=small([1,2],[1,1,2],[{id:1,inicio:0,temperatura:10},{id:2,inicio:0,temperatura:30}]);r=run(pair,{horizon:1});near(r.history.at(-1).mean,20,1e-10);const expected=20-10*Math.exp(-4*3600/(2400*900));near(r.fields[r.fields.length-2],expected,.00001);console.log('OK difusión entre dos celdas: conservación y decaimiento analítico de su diferencia.');
const separated=small([1,0,2],[1,1,3],pair.vertidas);r=run(separated);near(r.fields[r.fields.length-2],10);near(r.fields[r.fields.length-1],30);console.log('OK máscara: una celda vacía no conduce.');
const sequence=small([1,2],[1,1,2],[{id:1,inicio:0,temperatura:20},{id:2,inicio:.1,temperatura:30}]);r=run(sequence,{horizon:.2,dtCap:900});const event=r.times.indexOf(.1);assert(event>=0);assert(Number.isNaN(r.fields[1]));near(r.fields[event*2+1],30);near(r.energyIn,50*2400*900);assert(r.history.at(-1).mean>24.9999);console.log('OK activación: NaN antes de colocar, T nueva propia, T previa persistente y energía sensible incluida.');
assert.throws(()=>run(separated,{observe:[1.5,.5,.5]}),/vacío/);
assert.throws(()=>run(small(),{dtCap:1,horizon:336}),/Demasiados/);
for(const g of DATA.grillas){g.ids=decode(g);const s=statistics(g,g.ids);assert.equal(s.occupied,g.ocupados);near(s.areas[0],g.exteriores);near(s.areas[1],g.internas);near(s.areas[2],g.interfaces);
 for(const e of g.eventos){const st=statistics(g,activeIds(g,e.t,true));assert.equal(st.occupied,e.ocupados);near(st.areas[0],e.exterior);near(st.areas[2],e.interfaces);}
 console.log(`OK geometría h=${g.h}: áreas y activaciones coinciden con Python.`);}
const g=DATA.grillas[1],p={...defaults,q:500,duration:12,horizon:336,bc:Array.from({length:6},()=>({type:'R',value:10,h:5})),observe:[0,0,1.5]};
r=run({g,vertidas:DATA.vertidas},p);assert(r.steps>1000);assert(r.peak.value>19);assert(r.trough.value>=10-1e-8);assert.equal(r.history.at(-1).t,336);
console.log(`OK fundación real 0,5 m, 14 días: Tmax=${r.peak.value.toFixed(6)} °C; Tmin=${r.trough.value.toFixed(6)} °C; residuo=${r.balance.toExponential(3)} J; ${r.steps} pasos.`);
const fine=run({g:DATA.grillas[2],vertidas:DATA.vertidas},{...p,horizon:48});assert.equal(fine.history.at(-1).t,48);console.log('OK grilla 0,25 m: ensayo de 48 h estable, con balance.');
near(playbackTime(24,6/1.8+1),48);near(playbackTime(30,17),336);console.log('OK animación: acelera ×10 a las 30 h y termina a las 336 h.');
