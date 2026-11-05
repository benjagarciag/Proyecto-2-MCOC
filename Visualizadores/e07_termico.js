/* Balance cartesiano explícito sobre la máscara IFC. Fuente directa o hidratación exponencial por edad; integral exacta por paso.
 * Convenciones idénticas a mcplan.bordes_termicos.coeficientes_cara:
 * G=kA/d, Dirichlet H=2kA/d; Robin H=A/(d/(2k)+1/h);
 * Neumann positivo entrante. P_cara=B-H*T. Interfaces: contacto perfecto.
 * Solo se ejecuta al pulsar Calcular, en un Worker; no modifica archivos.
 */
function solveVoxelHeat(input, onProgress = () => {}) {
  const {g, vertidas, p} = input;
  const finite = (n,v) => {if(!Number.isFinite(v))throw Error(n+' debe ser finito.');};
  for(const k of ['k','rho','cp','q','duration','horizon','dtCap'])finite(k,p[k]);
  if(p.k<=0||p.rho<=0||p.cp<=0||p.q<0||p.duration<=0||p.horizon<=0||p.horizon>336||p.dtCap<=0)
    throw Error('k, ρ, cₚ, duración y Δt deben ser positivos; fuente ≥ 0 y horizonte entre 0 y 336 h.');
  if(!['pulse','constant','hydration'].includes(p.sourceMode))throw Error('Modo de fuente inválido.');
  if(p.sourceMode==='hydration'&&(!Number.isFinite(p.tau)||p.tau<=0))throw Error('τ debe ser positivo y finito.');
  if(!Number.isInteger(p.sourceId)||p.sourceId<0||p.sourceId>5)throw Error('ID de fuente inválido.');
  if(!Array.isArray(p.bc)||p.bc.length!==6)throw Error('Se requieren seis condiciones de borde.');
  const [nz,ny,nx]=g.forma;
  if(![nx,ny,nz].every(n=>Number.isInteger(n)&&n>0)||g.ids.length!==nx*ny*nz||!(g.h>0))throw Error('Grilla inválida.');
  const N=g.ids.reduce((s,v)=>s+(v>0),0),V=g.h**3,A=g.h**2,C=p.rho*p.cp*V,G=p.k*g.h;
  if(!N)throw Error('La grilla no contiene hormigón.');
  if(Math.ceil(p.horizon*3600/p.dtCap)>20000)throw Error('Demasiados pasos para la vista interactiva. Aumenta Δt tope o reduce el horizonte.');
  const map=new Int32Array(g.ids.length).fill(-1),indices=new Int32Array(N),ids=new Uint8Array(N);
  const starts=new Float64Array(N),initials=new Float64Array(N),neighbors=new Int32Array(N*6).fill(-1);
  let cursor=0;
  for(let flat=0;flat<g.ids.length;flat++)if(g.ids[flat]){const v=vertidas.find(v=>v.id===g.ids[flat]);if(!v)throw Error('ID sin propiedades IFC.');
    finite('Inicio',v.inicio);finite('T colocación',v.temperatura);if(v.inicio<0)throw Error('Inicio negativo.');
    map[flat]=cursor;indices[cursor]=flat;ids[cursor]=g.ids[flat];starts[cursor]=v.inicio*3600;initials[cursor]=v.temperatura;cursor++;}
  for(let i=0;i<N;i++){const flat=indices[i],x=flat%nx,y=Math.floor(flat/nx)%ny,z=Math.floor(flat/(nx*ny));
    const f=[x>0?flat-1:-1,x<nx-1?flat+1:-1,y>0?flat-nx:-1,y<ny-1?flat+nx:-1,z>0?flat-nx*ny:-1,z<nz-1?flat+nx*ny:-1];
    for(let d=0;d<6;d++)if(f[d]>=0)neighbors[i*6+d]=map[f[d]];}
  const H=new Float64Array(6),B=new Float64Array(6);
  for(let d=0;d<6;d++){const bc=p.bc[d];finite('Valor de borde',bc.value);
    if(bc.type==='D'){H[d]=2*G;B[d]=H[d]*bc.value;}
    else if(bc.type==='N'){H[d]=0;B[d]=bc.value*A;}
    else if(bc.type==='R'){finite('β Robin',bc.h);if(bc.h<0)throw Error('β Robin no puede ser negativo.');H[d]=bc.h?A/(g.h/(2*p.k)+1/bc.h):0;B[d]=H[d]*bc.value;}
    else throw Error('Borde desconocido.');}
  let observation=-1;
  if(p.observe){const xyz=p.observe.map((v,d)=>Math.floor((v-g.origen[d])/g.h));
    if(xyz.length!==3||!xyz.every(Number.isFinite)||xyz.some((v,d)=>v<0||v>=[nx,ny,nz][d]))throw Error('El punto observado está fuera de la grilla.');
    observation=map[(xyz[2]*ny+xyz[1])*nx+xyz[0]];if(observation<0)throw Error('El punto observado cae en un voxel vacío. Elige un centro del hormigón en el corte.');}
  let T=new Float64Array(N).fill(NaN),next=new Float64Array(N).fill(NaN);
  const active=new Uint8Array(N),extH=new Float64Array(N),extB=new Float64Array(N);
  const end=p.horizon*3600;
  const snapshotTimes=[...new Set([0,end,...Array.from({length:129},(_,i)=>end*i/128),...vertidas.map(v=>v.inicio*3600).filter(t=>t>=0&&t<=end)])].sort((a,b)=>a-b);
  const events=[...new Set([end,...vertidas.flatMap(v=>[v.inicio*3600,...(p.sourceMode==='pulse'?[(v.inicio+p.duration)*3600]:[])]).filter(t=>t>=0&&t<=end)])].sort((a,b)=>a-b);
  const fields=new Float32Array(snapshotTimes.length*N).fill(NaN),history=[];
  let t=0,steps=0,snapshot=0,event=0,dtLimit=Infinity,dtMin=Infinity,dtMax=0,energyIn=0,energySource=0,energyBoundary=0;
  let peak={value:-Infinity,t:0},trough={value:Infinity,t:0},peakField=null,troughField=null,lastProgress=-1;
  const vertidaPeaks=vertidas.map(v=>({id:v.id,value:null,t:null}));
  const peakById=new Map(vertidaPeaks.map(v=>[v.id,v]));
  const sourceAt=(i,time)=>p.q&&(p.sourceId===0||ids[i]===p.sourceId)&&time>=starts[i]&&(p.sourceMode!=='pulse'||time<starts[i]+p.duration*3600)?p.q*V*(p.sourceMode==='hydration'?Math.exp(-(time-starts[i])/(p.tau*3600)):1):0;
  function activate(){let added=false;for(let i=0;i<N;i++)if(!active[i]&&starts[i]<=t+1e-7){active[i]=1;T[i]=initials[i];energyIn+=C*T[i];added=true;}return added;}
  function operator(){let maxDiagonal=0;for(let i=0;i<N;i++)if(active[i]){let h=0,b=0,diag=0;for(let d=0;d<6;d++){const j=neighbors[i*6+d];if(j>=0&&active[j])diag+=G;else{h+=H[d];b+=B[d];diag+=H[d];}}extH[i]=h;extB[i]=b;maxDiagonal=Math.max(maxDiagonal,diag);}dtLimit=maxDiagonal?C/maxDiagonal:Infinity;}
  function record(){const maxima=new Map();let min=Infinity,max=-Infinity,sum=0,count=0,energy=0,ps=0,pb=0,obsCond=null,obsBorder=null,obsSource=null;
    for(let i=0;i<N;i++)if(active[i]){const ti=T[i];if(!Number.isFinite(ti))throw Error('Temperatura no finita; revisa parámetros y estabilidad.');min=Math.min(min,ti);max=Math.max(max,ti);sum+=ti;count++;energy+=C*ti;ps+=sourceAt(i,t);pb+=extB[i]-extH[i]*ti;let cellMax=ti;
      for(let d=0;d<6;d++){const j=neighbors[i*6+d];if(j<0||!active[j]){const bc=p.bc[d];const face=bc.type==='D'?bc.value:ti+(B[d]-H[d]*ti)*g.h/(2*p.k*A);min=Math.min(min,face);max=Math.max(max,face);cellMax=Math.max(cellMax,face);}}
      maxima.set(ids[i],Math.max(maxima.get(ids[i])??-Infinity,cellMax));
      if(i===observation){let cond=0;for(let d=0;d<6;d++){const j=neighbors[i*6+d];if(j>=0&&active[j])cond+=G*(T[j]-ti);}obsCond=cond/C*3600;obsBorder=(extB[i]-extH[i]*ti)/C*3600;obsSource=sourceAt(i,t)/C*3600;}}
    for(const [id,value] of maxima){const p=peakById.get(id);if(p.value===null||value>p.value){p.value=value;p.t=t/3600;}}
    if(count){if(max>peak.value){peak={value:max,t:t/3600};peakField=new Float32Array(T);}if(min<trough.value){trough={value:min,t:t/3600};troughField=new Float32Array(T);}}
    history.push({t:t/3600,min:count?min:null,max:count?max:null,mean:count?sum/count:null,energy,source:ps,boundary:pb,
      obsT:observation>=0&&active[observation]?T[observation]:null,cond:obsCond,border:obsBorder,internal:obsSource,
      rate:obsCond===null?null:obsCond+obsBorder+obsSource});
  }
  activate();operator();record();
  fields.set(T,snapshot++*N);
  while(t<end-1e-7){
    while(event<events.length&&events[event]<=t+1e-7)event++;
    const target=Math.min(end,events[event]??end,snapshotTimes[snapshot]??end);
    const dt=Math.min(p.dtCap,.8*dtLimit,target-t);
    if(!(dt>0))throw Error('Paso temporal no representable.');
    if(++steps>20000)throw Error('Se superó el límite de 20.000 pasos interactivos. Ajusta la malla o el horizonte.');
    dtMin=Math.min(dtMin,dt);dtMax=Math.max(dtMax,dt);
    let qStep=0,bStep=0;
    for(let i=0;i<N;i++)if(active[i]){const ti=T[i];let conduction=0;
      for(let d=0;d<6;d++){const j=neighbors[i*6+d];if(j>=0&&active[j])conduction+=G*(T[j]-ti);}
      const boundary=extB[i]-extH[i]*ti,source=sourceAt(i,t)*(p.sourceMode==='hydration'?-Math.expm1(-dt/(p.tau*3600))/(dt/(p.tau*3600)):1);
      next[i]=ti+dt*(conduction+boundary+source)/C;qStep+=source;bStep+=boundary;
    }else next[i]=NaN;
    [T,next]=[next,T];energySource+=qStep*dt;energyBoundary+=bStep*dt;t+=dt;
    if(Math.abs(t-target)<1e-7)t=target;
    if(activate())operator();record();
    if(snapshot<snapshotTimes.length&&Math.abs(t-snapshotTimes[snapshot])<1e-7)fields.set(T,snapshot++*N);
    const progress=Math.floor(t/end*100);if(progress!==lastProgress){lastProgress=progress;onProgress(progress);}
  }
  if(!peakField||!troughField)throw Error('No hay hormigón colocado dentro del horizonte elegido.');
  const last=history[history.length-1],balance=last.energy-energyIn-energySource-energyBoundary;
  return {indices,fields,times:snapshotTimes.map(t=>t/3600),history,peak,trough,vertidaPeaks,peakField,troughField,p,steps,dtMin,dtMax,dtLimit:dtLimit===Infinity?null:dtLimit,
    energyIn,energySource,energyBoundary,balance,observation,N,h:g.h,
    scale:[trough.value,peak.value]};
}
if(typeof module!=='undefined'&&module.exports)module.exports={solveVoxelHeat};
