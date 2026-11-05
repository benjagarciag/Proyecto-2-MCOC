/* node desarrollo/tests/test_e08_termico_web.cjs [directorio Visualizadores] */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=process.argv[2]||path.resolve(__dirname,'../../Visualizadores');
const {solveVoxelHeat}=require(path.resolve(source,'e07_termico.js'));
const p={k:2,rho:2400,cp:900,q:900,tau:30,duration:12,horizon:72,dtCap:3600,sourceMode:'hydration',sourceId:0,bc:Array.from({length:6},()=>({type:'N',value:0,h:0})),observe:null};
const input={g:{ids:[1,0,2],forma:[1,1,3],h:1,origen:[0,0,0]},vertidas:[{id:1,inicio:0,temperatura:19},{id:2,inicio:6.37,temperatura:18}]};
const near=(a,b,tol=1e-7)=>assert(Math.abs(a-b)<tol,`${a} != ${b}`);
const heat=age=>age<0?0:900*30*3600*(-Math.expm1(-age/30));
for(const dtCap of [3600,137]){
 const r=solveVoxelHeat({...input,p:{...p,dtCap}}),capacity=p.rho*p.cp;
 near(r.fields.at(-2),19+heat(72)/capacity,4e-6);
 near(r.fields.at(-1),18+heat(72-6.37)/capacity,4e-6);
 near(r.energySource,heat(72)+heat(72-6.37),1e-5);
 near(r.balance,0,1e-5);
 const event=r.times.indexOf(6.37);assert(event>=0);assert(Number.isNaN(r.fields[1]));near(r.fields[event*2+1],18);
 near(r.history.find(x=>x.t===6.37).source,900*(1+Math.exp(-6.37/30)),1e-8);
}
console.log('OK hidratación: solución adiabática independiente, energía exacta con dos pasos temporales y edades separadas.');
const moved=solveVoxelHeat({...input,vertidas:[input.vertidas[0],{id:2,inicio:24,temperatura:25}],p});
near(moved.fields.at(-1),25+heat(48)/(p.rho*p.cp),4e-6);
console.log('OK entradas: cambiar inicio y temperatura cambia activación y resultado sin editar el solver.');
const selected=solveVoxelHeat({...input,p:{...p,sourceId:2}});near(selected.fields.at(-2),19);near(selected.energySource,heat(72-6.37),1e-5);
assert.throws(()=>solveVoxelHeat({...input,p:{...p,tau:0}}),/τ/);
assert.throws(()=>solveVoxelHeat({...input,p:{...p,tau:NaN}}),/τ/);
console.log('OK selección de fuente y rechazo de tau inválido.');
const html=fs.readFileSync(path.resolve(source,'E07.html'),'utf8'),script=html.match(/<script>\s*([\s\S]*?)<\/script>/)[1];new vm.Script(script);
const data=JSON.parse(html.match(/<script id="e07-data" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const foundation=data.grillas[1];foundation.ids=foundation.rle.flatMap(([id,count])=>Array(count).fill(id));
const integrated=solveVoxelHeat({g:foundation,vertidas:data.vertidas,p:{...p,horizon:336,dtCap:900,bc:Array.from({length:6},()=>({type:'R',value:10,h:5}))}});
const expectedEnergy=data.vertidas.reduce((sum,v)=>sum+foundation.filas.find(f=>f.vertida_id===v.id).numero_voxeles*foundation.h**3*heat(336-v.inicio),0);
assert(Math.abs(integrated.energySource-expectedEnergy)/expectedEnergy<1e-12);
assert(Math.abs(integrated.balance)/expectedEnergy<1e-11);assert(Number.isFinite(integrated.peak.value));assert.equal(integrated.history.at(-1).t,336);
console.log(`OK IFC→grid→activación→hidratación→conducción/bordes: 14 días, Tmax=${integrated.peak.value.toFixed(6)} °C; residuo=${integrated.balance.toExponential(3)} J.`);
// Isolated controller test: no browser, no simulations of the foundation, no writes.
const nodes=new Map();const el=id=>{if(!nodes.has(id))nodes.set(id,{textContent:'',innerHTML:'',value:'',disabled:false,cloneNode(){return {...this,checkValidity(){const n=Number(this.value);return this.value!==''&&Number.isFinite(n)&&(!this.min||n>=this.min)&&(!this.max||n<=this.max);}}}});return nodes.get(id);};
const ctx=vm.createContext({DATA:data,Set,Number,Array,Error,Math,$:el,document:{querySelectorAll:()=>[]},stopPlay(){},invalidateThermal(){ctx.invalidations++;},update(){},renderEvents(){},invalidations:0,state:{hidden:new Set(),selected:0}});
const functions=['renderSequenceInputs','applySequence','validateScenario','visibleId'];
for(const name of functions){const start=script.indexOf('function '+name+'('),end=script.indexOf('\nfunction ',start+1);vm.runInContext(script.slice(start,end<0?undefined:end),ctx);}
// renderSequenceInputs uses dot; replace it for this pure controller check.
ctx.renderSequenceInputs=()=>{};
ctx.values=data.vertidas.map(({id,inicio,temperatura})=>({id,inicio,temperatura}));
ctx.values[1].inicio=24;ctx.values[1].temperatura=25;vm.runInContext('applySequence(values)',ctx);
assert.equal(data.vertidas[1].inicio,24);assert.equal(data.vertidas[1].temperatura,25);assert.equal(ctx.invalidations,1);
ctx.values[0].inicio=-1;assert.throws(()=>vm.runInContext('applySequence(values)',ctx),/Revisa/);assert.equal(ctx.invalidations,1);
const before=JSON.stringify(data);vm.runInContext('state.hidden.add(2)',ctx);assert.equal(vm.runInContext('visibleId(2)',ctx),false);assert.equal(vm.runInContext('visibleId(1)',ctx),true);assert.equal(JSON.stringify(data),before);
for(const id of ['k','rho','cp','q','tau','duration','horizon','dtCap']){const inputId={k:'thermalK',rho:'thermalRho',cp:'thermalCp',q:'thermalQ',tau:'thermalTau',duration:'thermalDuration',horizon:'thermalHorizon',dtCap:'thermalDt'}[id];el(inputId).min=id==='q'?'0':'0.01';}
ctx.scenario={version:1,sha256_ifc:data.sha256_ifc,h:.5,p:{...p,observe:[0,0,1.5]}};assert.equal(vm.runInContext('validateScenario(scenario)',ctx),1);
ctx.scenario.p.horizon=NaN;assert.throws(()=>vm.runInContext('validateScenario(scenario)',ctx),/Parámetro/);
console.log('OK HTML: sintaxis, secuencia aplicada, invalidación, rechazo de entradas, visibilidad independiente y validación JSON.');
