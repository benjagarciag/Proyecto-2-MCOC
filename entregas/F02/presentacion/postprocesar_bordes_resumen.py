"""Reintegra autoría Artifact de B03; conserva el resto del paquete original."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json
import postprocesar_pre_entrega as P
H=P.H;NS=P.NS
A=Path('entregas/F02/presentacion');W=Path('.venv/cache/bordes_resumen_f02')
d=json.loads((W/'contenido.json').read_text(encoding='utf8'))
with ZipFile(W/'source.pptx') as z:files={n:z.read(n) for n in z.namelist()}
with ZipFile(W/'artifact.pptx') as z:draft={n:z.read(n) for n in z.namelist()}
slides={i:H.xml(files[f'ppt/slides/slide{i}.xml']) for i in [9,12]}
for i,name in [(12,'Text 0'),(12,'Text 7'),(9,'Text 7')]:
    authored=H.shapes(H.xml(draft[f'ppt/slides/slide{i}.xml']),name)[0].find('p:txBody',NS)
    for sp in H.shapes(slides[i],name):
        body=sp.find('p:txBody',NS)
        for par in body.findall('a:p',NS):body.remove(par)
        for par in authored.findall('a:p',NS):body.append(P.deepcopy(par))
t=slides[12];tree=t.find('p:cSld/p:spTree',NS)
for el in list(tree):
    if el.xpath('.//p:cNvPr[starts-with(@name,"eq_b03_")]',namespaces=NS):tree.remove(el)
for sp in t.findall('.//p:sp',NS):
    value=''.join(sp.xpath('.//a:t/text()',namespaces=NS))
    if 'SUPUESTO DEL MODELO' in value:sp.getparent().remove(sp)
P.native_table(t,d['filas'],x=.8,y=1.7,w=11.7,h=3.9,widths=[2.3,9.4],size=22)
for tr in t.findall('.//a:tbl/a:tr',NS)[1:]:
    for tc in tr.findall('a:tc',NS):
        for pp in tc.findall('.//a:pPr',NS):pp.set('algn','l')
P.text(t,'Text 7',size=16,x=.8,y=6.1,w=11.7,h=.45)
P.text(slides[9],'Text 7',size=16)
for i,t in slides.items():files[f'ppt/slides/slide{i}.xml']=H.out(t)
notes=H.xml(files['ppt/notesSlides/notesSlide12.xml']);body=notes.xpath('.//p:sp[p:nvSpPr/p:nvPr/p:ph/@type="body"]',namespaces=NS)[0]
H.reset_text(body,'B03 · Condiciones de borde\n\n'+'\n\n'.join(' · '.join(r) for r in d['filas'])+'\n\n'+d['pie']+'''\n\nPARA RESPONDER
Robin: intercambio con aire y resistencia al terreno. En aire se resuelve un balance no lineal: convección, solar absorbida y onda larga; madera y mantas son resistencias en serie, sin inercia propia. Arriba hay mantas; en laterales madera y mantas, sin relleno. No se prescribe la temperatura de cara del hormigón.
Neumann es flujo prescrito. No llamamos Neumann al flujo calculado por Robin ni adiabática a una manta con resistencia finita.
Dirichlet prescribe temperatura en una frontera. Nuestro reservorio externo de suelo tiene15°C; la cara de hormigón se acopla por resistencia0,50/1,20m²K/W más media celda. El agua uniforme18°C es referencia del sumidero equivalente, no una pared de tubo discretizada.
Calor interno: hidratación positiva y frío negativo, ambos enW/m³. No son condiciones de borde. Colocación a12°C es condición inicial.
Interfaces: temperatura y flujo continuos, contacto perfecto; la cara cubierta deja de ser exterior. Retiros72/240/504h de edad local, sujetos a monitoreo; después sombra90% (se conserva10%solar), con h y onda larga conservados.

FUENTES
entregas/F02/cierre_revision_final/CONFIGURACION_FINAL_REVISADA.json; casos/sensibilidad_h/radiacion_borde.py; proteccion_postdesmolde.py. Revisión documental19/11/2026, sin nuevas simulaciones.''')
files['ppt/notesSlides/notesSlide12.xml']=H.out(notes)
with ZipFile(W/'candidate.pptx','w',ZIP_DEFLATED) as z:
    for n,b in files.items():z.writestr(n,b)
with ZipFile(W/'source.pptx') as z:changed=[n for n in files if files[n]!=z.read(n)]
assert set(changed)=={'ppt/slides/slide9.xml','ppt/slides/slide12.xml','ppt/notesSlides/notesSlide12.xml'},changed
print('Solo cambian B03, su nota y la etiqueta del índice.')
s=(A/'finalizar_pre_entrega.mjs').read_text(encoding='utf8').replace('cache/pre_entrega_f02','cache/bordes_resumen_f02').replace('F02_Grupo6_Pre_entrega.pptx','F02_Grupo6_Bordes_resumen.pptx').replace("const original=path.join(work,'F02_Grupo6_radiacion_actualizada.pptx');","const original=path.join(work,'source.pptx');").replace('validacion_pre_entrega.json','validacion_bordes.json')
(A/'finalizar_bordes_resumen.mjs').write_text(s,encoding='utf8')
