"""Añade B16 sin reserializar ninguna de las24diapositivas del usuario."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from copy import deepcopy
from hashlib import sha256
import json
from lxml import etree as E
import postprocesar_pre_entrega as P
H=P.H;NS=P.NS;A=Path('entregas/F02/presentacion');W=Path('.venv/cache/f02_final_ecuaciones')
with ZipFile(W/'source.pptx') as z:original={n:z.read(n) for n in z.namelist()}
files=dict(original);slides={23:H.xml(files['ppt/slides/slide23.xml'])}
P.clone_slide(files,slides,23,25);t=slides[25];tree=t.find('p:cSld/p:spTree',NS)
for el in list(tree):
    if E.QName(el).localname in ('nvGrpSpPr','grpSpPr'):continue
    names=el.xpath('.//p:cNvPr/@name',namespaces=NS)
    if not any(n in ['Shape 0','Text 0','Text 1','Text 3'] or n.startswith('Slide Number') for n in names):tree.remove(el)
with ZipFile(W/'artifact.pptx') as z:auth=H.xml(z.read('ppt/slides/slide23.xml'))
sp=H.shapes(t,'Text 0')[0];body=sp.find('p:txBody',NS)
for par in body.findall('a:p',NS):body.remove(par)
for par in H.shapes(auth,'Text 0')[0].findall('p:txBody/a:p',NS):body.append(deepcopy(par))
P.text(t,'Text 0',size=28)

def label(name,value,x,y,w):
    sp=P.new_text(t,name,value,x,y,w,.35,16)
    for pp in sp.findall('.//a:pPr',NS):pp.set('algn','l')
    for co in sp.findall('.//a:srgbClr',NS):co.set('val','166C65')
    return sp

H.post.SIMBOLOS.update(tau='τ',epsilon='ε',sigma='σ',alpha='α',chi='χ',sum='∑',ell='ℓ')
def eq(name,tex,x,y,w,h,points=22,color='202B33'):
    sp=P.new_text(t,name,'',x,y,w,h,points);tree.remove(sp)
    alt=E.SubElement(tree,H.q('mc:AlternateContent'))
    choice=E.SubElement(alt,H.q('mc:Choice'),Requires='a14',nsmap={'a14':NS['a14']})
    choice.append(sp);fallback=E.SubElement(alt,H.q('mc:Fallback'));fallback.append(deepcopy(sp))
    H.equation(t,name,tex,points,color)
    for shape in H.shapes(t,name):
        for pp in shape.findall('.//a:pPr',NS):pp.set('algn','l')

label('titulo_balance','1 · Balance dentro del hormigón',.6,1.35,6.5)
eq('modelo_continuo',r'\rho c_p\frac{\partial T}{\partial t}=\nabla\cdot(k\nabla T)+Q(a)-q_{frío}',.6,1.78,6.5,.8,24)
label('titulo_exterior','2 · Aire: convección + solar + onda larga',.6,2.95,6.6)
eq('modelo_exterior',r"q''=h(T_a-T_s)+\alpha\tau I+\epsilon\sigma(T_{rad,K}^4-T_{s,K}^4)",.6,3.4,6.6,.7,17,'1B74AA')
eq('modelo_resistencia',r"q''=\frac{T_s-T_i}{R},\quad R=\frac{d}{k_c}+\sum_\ell\frac{e_\ell}{k_\ell}",.6,4.25,6.6,.75,21,'1B74AA')
label('titulo_suelo','3 · Base: resistencia hacia el suelo',.6,5.35,6.5)
eq('modelo_suelo',r"q''_{suelo}=\frac{15-T_i}{d/k_c+0{,}50/1{,}20}",.6,5.8,6.5,.8,22)
label('titulo_discreto','4 · Avance temporal por celda',7.5,1.35,5.2)
eq('modelo_discreto',r'T_i^{n+1}=T_i^n+\frac{\Delta t}{C_i}P_i+\frac{V_i}{C_i}\Delta E_h',7.5,1.85,5.2,.8,21)
sp=P.new_text(t,'def_discreto','Cᵢ = ρcₚVᵢ · Pᵢ = conducción + bordes − frío [W]',7.5,2.65,5.2,.45,12)
label('titulo_frio','5 · Refrigeración equivalente',7.5,3.35,5.2)
eq('modelo_frio',r'P_{frío}=\min(\sum_{i}\chi_{i} U_{v} V_{i}\max(T_i-18,0),15\ \mathrm{kW})',7.5,3.85,5.2,.9,16,'1B74AA')
label('titulo_fuente','6 · Hidratación y convección',7.5,5.05,5.2)
eq('modelo_fuente',r'\Delta E_h=E_h(a+\Delta t)-E_h(a)',7.5,5.5,5.2,.6,21)
eq('modelo_viento',r'h=5{,}7+3{,}8v_{10}(2/10)^{0{,}14}',7.5,6.15,5.2,.45,20)
P.new_text(t,'convencion','q″ positivo hacia el hormigón · Tₛ: exterior de la protección · T⁴ en kelvin · τ = 0,10 con sombra',.6,6.95,12,.25,11)
note=H.xml(files['ppt/notesSlides/notesSlide25.xml']);body=note.xpath('.//p:sp[p:nvSpPr/p:nvPr/p:ph/@type="body"]',namespaces=NS)[0]
H.reset_text(body,'''B16 · Ecuaciones del modelo (respaldo para preguntas).
1. Balance local enW/m³: almacenamiento = conducción + hidratación − refrigeración.
2. Flujo positivo hacia el hormigón. Ts es exterior de protección;Ti centro; d=Δx/2. R combina media celda y las protecciones vigentes. La temperatura radiativa efectiva cumple Trad,K⁴=Fcielo Tcielo,K⁴+(1−Fcielo)Ta,K⁴. Alpha0,6,epsilon0,9; tau1antes y0,10después del retiro local de última manta504h. Solar actúa en exterior de la protección; solo flujo neto entra al hormigón.
3. Reservorio de suelo15°C conL0,50m/k1,20, sin inercia; no se fija temperatura de la cara del hormigón.
4. Euler explícito: Ci=rho cp Vi. Pi=sumjGij(Tj−Ti)+sumfAfqf''−Pfrio,i. Gij=kA/Δx para material uniforme. Paso≤300s y restricción de estabilidad local. ΔEh enJ/m³ se integra exactamente desde el acumulado por edad. Se separa conducción/bordes/frío enPi de la hidratación enΔEh.
5. chi indica habilitación de celdas de ramales abiertos. Uv5W/(m³K), agua18°C uniforme y tope15000Wglobal. Frío se distribuye proporcionalmente entre celdas habilitadas cuando actúa el tope. Apertura con cobertura y mínima19°C; cierre≤18°C, mantiene estado en banda. No se resuelve pared ni agua axial.
6. Eh integral trapezoidal deQrecibida, interpolación acumulada lineal; edad reiniciada por capa. hW/(m²K), viento10ma2m con exponente0,14. hno incluye LWotra vez.
Condición inicial12°Cpor capa; contacto perfecto entre capas; retiros72/240/504hlocales. Métricas y probabilidades enB09/B10; reconstrucciónS25enB14. Fuentes: CONFIGURACION_FINAL_REVISADA.json, radiacion_borde.py, control_circuitos.py, cierre_f02.py. Sin nuevas simulaciones ni cambios de datos.
Las24diapositivas anteriores se conservaron exactamente como las guardó el usuario.''')
files['ppt/notesSlides/notesSlide25.xml']=H.out(note);files['ppt/slides/slide25.xml']=H.out(t)
for n in original:
    if n not in ['ppt/presentation.xml','ppt/_rels/presentation.xml.rels','[Content_Types].xml']:assert files[n]==original[n],n
with ZipFile(W/'candidate.pptx','w',ZIP_DEFLATED) as z:
    for n,b in files.items():z.writestr(n,b)
report={'source_sha256':sha256((W/'source.pptx').read_bytes()).hexdigest(),'diapositivas_originales_identicas':list(range(1,25)),'respaldo_nuevo':25,'partes_originales_modificadas':['ppt/presentation.xml','ppt/_rels/presentation.xml.rels','[Content_Types].xml'],'nota':'Se añade B16 al final; índice original sin cambios para conservar toda edición del usuario.'}
(W/'conservacion.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('25diapositivas; originales1–24 byte por byte idénticas.')
