"""Reintegra autoría Artifact al paquete original sin perder animaciones.

Datos exclusivamente calculados: cierre_f02 y proteccion_postdesmolde.
Ejecutar desde la raíz con el Python documental (lxml/openpyxl).
"""
from copy import deepcopy
from io import BytesIO
import json,math,posixpath,re
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
import postprocesar_radiacion as H

R=Path.cwd(); A=R/'entregas/F02/presentacion'; W=R/'.venv/cache/pre_entrega_f02'
NS=H.NS; q=H.q; xml=H.xml; out=H.out
F=lambda x,n=2:f'{x:.{n}f}'.replace('.',',')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))

def geometry(el,x=None,y=None,w=None,h=None):
    tr=el.find('p:spPr/a:xfrm',NS)
    if tr is None:tr=el.find('p:xfrm',NS)
    assert tr is not None
    for key,value in dict(x=x,y=y,w=w,h=h).items():
        if value is not None:tr.find('a:off' if key in ('x','y') else 'a:ext',NS).set({'w':'cx','h':'cy'}.get(key,key),str(round(value*914400)))

def text(slide,name,value=None,size=None,**coords):
    matches=H.shapes(slide,name);assert matches,name
    for sp in matches:
        if value is not None:H.reset_text(sp,value)
        if size:H.fontsize(sp,size)
        if coords:geometry(sp,**coords)
    return matches[0]

def native_table(slide,rows,x=None,y=None,w=None,h=None,widths=None,size=14):
    graphic=slide.xpath('.//p:graphicFrame[a:graphic/a:graphicData/a:tbl]',namespaces=NS)[0]
    tab=graphic.find('.//a:tbl',NS); old=tab.findall('a:tr',NS)
    head,body=deepcopy(old[0]),deepcopy(old[1]);cols=len(rows[0])
    grid=tab.find('a:tblGrid',NS)
    original_widths=[int(c.get('w'))/914400 for c in grid]
    original_height=sum(int(tr.get('h')) for tr in old)/914400
    grid.clear()
    total=w or sum(original_widths)
    widths=widths or (original_widths if len(original_widths)==cols and w is None else [total/cols]*cols)
    for width in widths:E.SubElement(grid,q('a:gridCol'),w=str(round(width*914400)))
    for tr in old:tab.remove(tr)
    for ri,row in enumerate(rows):
        tr=deepcopy(head if ri==0 else body); cells=tr.findall('a:tc',NS);template=deepcopy(cells[0])
        for cell in cells:tr.remove(cell)
        for j,val in enumerate(row):
            tc=deepcopy(cells[min(j,len(cells)-1)] if j<len(cells) else template)
            H.reset_text(tc,str(val));H.fontsize(tc,size);tr.append(tc)
        tr.set('h',str(round((h or original_height)/len(rows)*914400)));tab.append(tr)
    geometry(graphic,x=x,y=y,w=w,h=h)
    return graphic

def new_text(slide,name,value,x,y,w,h,size=14):
    sp=deepcopy(H.shapes(slide,'Text 0')[0]); tree=slide.find('p:cSld/p:spTree',NS)
    ids=[int(e.get('id')) for e in slide.findall('.//p:cNvPr',NS)]
    nv=sp.find('p:nvSpPr/p:cNvPr',NS);nv.set('id',str(max(ids)+1));nv.set('name',name)
    for hl in sp.findall('.//a:hlinkClick',NS):hl.getparent().remove(hl)
    H.reset_text(sp,value);H.fontsize(sp,size);geometry(sp,x=x,y=y,w=w,h=h);tree.append(sp)
    return sp

def clear_pictures(slide):
    for pic in slide.findall('.//p:pic',NS):pic.getparent().remove(pic)

def image(files,slide,i,path):
    pics=slide.findall('.//p:pic',NS);assert len(pics)==1,(i,len(pics))
    rid=pics[0].find('.//a:blip',NS).get(q('r:embed'))
    rels=xml(files[f'ppt/slides/_rels/slide{i}.xml.rels'])
    target=next(e.get('Target') for e in rels if e.get('Id')==rid)
    files[posixpath.normpath(posixpath.join('ppt/slides',target))]=Path(path).read_bytes()
    return pics[0]

def bar(files,num,cats,vals):
    chart=f'ppt/charts/chart{num}.xml';t=xml(files[chart]);ser=t.find('.//c:ser',NS)
    cat=ser.find('c:cat',NS);cat.clear();ref=E.SubElement(cat,q('c:strRef'));E.SubElement(ref,q('c:f')).text=f'Sheet1!$A$2:$A${len(vals)+1}'
    H.cached(E.SubElement(ref,q('c:strCache')),cats,'str')
    ref=ser.find('c:val/c:numRef',NS);ref.find('c:f',NS).text=f'Sheet1!$B$2:$B${len(vals)+1}'
    H.cached(ref.find('c:numCache',NS),vals)
    name=ser.find('c:tx/c:strRef/c:strCache/c:pt/c:v',NS).text
    rels=xml(files[f'ppt/charts/_rels/chart{num}.xml.rels']);target=next(e.get('Target') for e in rels if e.get('Type').endswith('/package'))
    p=posixpath.normpath(posixpath.join('ppt/charts',target));files[p]=H.sheet_bytes(files[p],[['Escenario',name]]+list(zip(cats,vals)))
    files[chart]=out(t)

def clone_slide(files,slides,source,dest):
    slides[dest]=deepcopy(slides[source]); relp=f'ppt/slides/_rels/slide{dest}.xml.rels'
    rels=xml(files[f'ppt/slides/_rels/slide{source}.xml.rels'])
    for rel in rels:
        if rel.get('Type').endswith('/notesSlide'):rel.set('Target',f'../notesSlides/notesSlide{dest}.xml')
    files[relp]=out(rels)
    files[f'ppt/notesSlides/notesSlide{dest}.xml']=files[f'ppt/notesSlides/notesSlide{source}.xml']
    nr=xml(files[f'ppt/notesSlides/_rels/notesSlide{source}.xml.rels'])
    for rel in nr:
        if rel.get('Type').endswith('/slide'):rel.set('Target',f'../slides/slide{dest}.xml')
    files[f'ppt/notesSlides/_rels/notesSlide{dest}.xml.rels']=out(nr)
    pres=xml(files['ppt/presentation.xml']);rels=xml(files['ppt/_rels/presentation.xml.rels'])
    rid='rId'+str(max(int(e.get('Id')[3:]) for e in rels)+1)
    E.SubElement(rels,'{http://schemas.openxmlformats.org/package/2006/relationships}Relationship',Id=rid,Type=NS['r']+'/slide',Target=f'slides/slide{dest}.xml')
    ids=pres.find('p:sldIdLst',NS);el=E.SubElement(ids,q('p:sldId'),id=str(max(int(e.get('id')) for e in ids)+1));el.set(q('r:id'),rid)
    files['ppt/presentation.xml']=out(pres);files['ppt/_rels/presentation.xml.rels']=out(rels)
    ct=xml(files['[Content_Types].xml'])
    for folder,kind in [('slides','slide'),('notesSlides','notesSlide')]:
        E.SubElement(ct,'{http://schemas.openxmlformats.org/package/2006/content-types}Override',PartName=f'/ppt/{folder}/{kind}{dest}.xml',ContentType=f'application/vnd.openxmlformats-officedocument.presentationml.{kind}+xml')
    files['[Content_Types].xml']=out(ct)
    text(slides[dest],'Text 1',f'B{dest-9:02d}')
    for sp in slides[dest].xpath('.//p:sp[p:nvSpPr/p:nvPr/p:ph/@type="sldNum"]',namespaces=NS):H.reset_text(sp,str(dest))

def main():
    with ZipFile(W/'F02_Grupo6_radiacion_actualizada.pptx') as z:files={n:z.read(n) for n in z.namelist() if not n.endswith('/')}
    with ZipFile(W/'artifact_editado.pptx') as z:authored={n:z.read(n) for n in z.namelist()}
    slides={i:xml(files[f'ppt/slides/slide{i}.xml']) for i in range(1,22)}
    for ed in read(W/'ediciones.json'):
        new=H.shapes(xml(authored[f"ppt/slides/slide{ed['slide']}.xml"]),ed['name'])[0].find('p:txBody',NS)
        for sp in H.shapes(slides[ed['slide']],ed['name']):
            body=sp.find('p:txBody',NS)
            for p in body.findall('a:p',NS):body.remove(p)
            for p in new.findall('a:p',NS):body.append(deepcopy(p))
    d=read(R/'entregas/F02/cierre_revision_final/DATOS_CIERRE.json');summary=d['resumen'];plans=summary['matrices']
    sp=text(slides[1],'s1_res',x=8.35,y=4.6,w=4.4,h=1.15)
    for p,size in zip(sp.findall('p:txBody/a:p',NS),[48,18]):H.fontsize(p,size)
    text(slides[1],'s1_lim',size=13,y=6.05,w=4.4,h=.6)
    text(slides[9],'Text 9',size=16)
    native_table(slides[4],[['Espacio','Tiempo'],['0,40 → 0,20 m','300 → 150 s'],['24 escenarios','2 casos decisivos'],['Cambio ΔT\n≤ 0,882 K','Cambio ΔT\n≤ 0,0014 K'],['misma clasificación','misma clasificación']],size=15)
    text(slides[3],'s3_sup',size=18,x=.8,y=1.9,w=7.1,h=1.1)
    text(slides[3],'Text 13',size=11,x=1,y=6.45,w=7.1,h=.5)
    text(slides[4],'s4_chk',size=16,x=1,y=5.6,w=11.8,h=.8)
    text(slides[5],'s5_pico',x=1.9,w=2.1);text(slides[5],'s5_14d',x=4.35,w=.9,size=10)
    text(slides[5],'s5_fino',size=12,x=8.85,y=5.6,w=4,h=.9)
    text(slides[6],'s6_climaU',size=10,h=.45)
    native_table(slides[7],[['Ritmo [m³/h]','D [h]','P_T','P_Δ','P_f','Cumple'],['60','10,61','0 %','0 %','0 %','Sí'],['55','11,58','0 %','0 %','0 %','Sí'],['> 60','< 10,61*','—','—','—','No adm.*']],h=1.8,size=13)
    for row in [2,3]:
        for j in range(11):
            for sp in H.shapes(slides[7],f's7_g{row}_{j}'):
                pr=sp.find('p:spPr',NS)
                for f in list(pr):
                    if E.QName(f).localname in ('solidFill','gradFill','pattFill','ln'):pr.remove(f)
                E.SubElement(pr,q('a:noFill'));line=E.SubElement(pr,q('a:ln'));E.SubElement(line,q('a:noFill'))
    for n in ['s7_gx0','s7_gx5','s7_gx10','s7_gx15']:text(slides[7],n,y=5.42)
    for name,y in [('s7_gl2',5.85),('s7_gD2',6.13),('s7_gl3',6.42),('s7_gD3',6.7)]:
        sp=text(slides[7],name,size=12,x=1.45,y=y,w=6.2,h=.3)
        for pp in sp.findall('.//a:pPr',NS):pp.set('algn','l')
    text(slides[7],'s7_tablaT',size=11,y=3.12,h=.6)
    text(slides[8],'Text 2',size=18,w=11.7,h=.6);text(slides[8],'Text 3',size=16,w=8,h=.7);text(slides[8],'s8_lim',size=14)
    text(slides[11],'Text 7',size=13,h=1.05)
    image(files,slides[11],11,R/'entregas/F02/cierre_revision_final/07_CLIMA_672H.png')
    H.post.SIMBOLOS.update(tau='τ',prime='′')
    H.equation(slides[12],'eq_b03_2',r"q''=h(T_a-T_s)+\alpha\tau I+\epsilon\sigma(T_{rad,K}^{4}-T_{s,K}^{4})",19,'1B74AA')
    text(slides[12],'Text 7','τ = 1 con protección; tras la última manta, τ = 0,10 para la radiación solar.\nSombra ideal: convección y onda larga conservan su ley; temperaturas radiativas en K.\nRetiro de la última manta a 504 h de edad local, condicionado a monitoreo.',size=15,x=.6,y=5.2,w=11.9,h=1.1)
    alternatives=[['Medida','Manta [h]','Sol restante','ΔT [K]','P_f','Cumple'],['Solo retiro tardío','504','100 %','33,01','100 %','No'],['Solo sombra 90 %','360','10 %','23,48','20,83 %','No'],['Manta + sombra','504','10 %','16,53','0 %','Sí']]
    # La tabla sustituye el raster antiguo que todavía mostraba retiro a360h.
    clear_pictures(slides[13]);template=deepcopy(slides[19].xpath('.//p:graphicFrame[a:graphic/a:graphicData/a:tbl]',namespaces=NS)[0]);slides[13].find('p:cSld/p:spTree',NS).append(template)
    native_table(slides[13],alternatives,x=.6,y=1.45,w=12.1,h=2.15,widths=[3.5,1.6,2,1.6,1.6,1.8],size=14)
    text(slides[13],'Text 11',size=14,x=.6,y=4.25,w=12,h=1)
    text(slides[14],'Text 4',size=14,y=3.45,h=2.85);text(slides[14],'Text 5',y=6.55,h=.3)
    teal=H.shapes(slides[16],'Shape 4')[0];gray=H.shapes(slides[16],'Shape 7')[0]
    width=int(teal.find('p:spPr/a:xfrm/a:ext',NS).get('cx'))/914400;geometry(gray,w=width*60/55)
    text(slides[16],'Text 8',x=4.5,w=1.3,size=20)
    H.equation(slides[17],'eq_b08_2',r'T_i^{n+1}=T_i^n+\frac{\Delta t}{C_i}P_i+\frac{V_i}{C_i}\Delta E_h',22,'1B74AA')
    sp=new_text(slides[17],'def_P','Pᵢ: conducción + bordes − frío [W]; ΔEₕ: calor volumétrico [J/m³]',.6,3.04,6.3,.35,11)
    for pp in sp.findall('.//a:pPr',NS):pp.set('algn','l')
    text(slides[17],'Text 7',size=12,h=.7)
    native_table(slides[18],[['Plan / curva','Clima','Peso','Tmax [°C]','ΔT [K]','I_T','I_Δ','I_F'],['Final / M4_SS','2024','1/24','46,66','16,53','0','0','0'],['Sombra / M4_SS','2024','1/24','46,66','23,48','0','1','1']],h=1.35,size=12)
    text(slides[18],'Text 4','Dos filas reales de planes distintos · 672 h · no se suman entre planes',size=12,y=2.75,h=.3)
    native_table(slides[19],[['Plan','Malla','D [h]','Tmax28d [°C]','ΔT28d [K]','Margen [K]','P_f']]+[[f"{p['q']} m³/h",F(p['h'])+' m',F(p['D_h']),F(p['Tmax']),F(p['Delta']),F(20-p['Delta']),'0 %'] for p in plans],h=1.65,size=13)
    image(files,slides[19],19,R/'entregas/F02/cierre_revision_final/04_CORTES_COMPARABLES_672H.png')
    # La imagen2×2 ocupa su proporción científica original; sin estirar el campo.
    pic=slides[19].findall('.//p:pic',NS)[0];geometry(pic,x=3.0,y=3.4,w=7.0,h=3.5)
    text(slides[19],'Text 4',size=11,y=3.03,h=.3)
    text(slides[20],'Text 25',size=12)
    # Historias nativas con punto exacto del máximo antes del salto horario.
    run=read(R/'resultados/cierre_f02/q60/malla_0.4_paso300/M4_SS_ERA5-2024.json');hist=run['historia'];event=run['corrida']['DeltaTmax'];peak=run['corrida']['Tmax']
    sample=hist[::12]+[hist[-1]]
    sample.append(dict(tiempo_h=event['tiempo_h'],Tmax_C=event['Tmax_C'],Tmin_S25_C=event['Tmin_S25_C'],DeltaT_K=event['valor']))
    sample.sort(key=lambda r:(r['tiempo_h'],0 if r.get('DeltaT_K')==event['valor'] else 1));xs=[r['tiempo_h'] for r in sample]
    H.scatter(files,1,[('Tmax hormigón',xs,[r['Tmax_C'] for r in sample]),('Tmin S25',xs,[r['Tmin_S25_C'] for r in sample]),('14 días',[336,336],[0,50])],672)
    H.scatter(files,2,[('ΔT',xs,[r['DeltaT_K'] for r in sample]),('límite20K',[0,672],[20,20]),('14 días',[336,336],[0,25]),('evento267h',[267],[event['valor']])],672)
    for num in [1,2]:
        t=xml(files[f'ppt/charts/chart{num}.xml'])
        for ax in t.findall('.//c:valAx',NS):
            if ax.find('c:axPos',NS).get('val')=='b':
                unit=ax.find('c:majorUnit',NS)
                if unit is not None:unit.set('val','96')
        files[f'ppt/charts/chart{num}.xml']=out(t)
    for num,year in [(4,2023),(5,2024),(6,2025)]:
        rr=read(R/f'resultados/cierre_f02/q60/malla_0.4_paso300/M4_SS_ERA5-{year}.json');h=rr['historia'][::12]+[rr['historia'][-1]]
        H.scatter(files,num,[(f'ERA5-{year}',[x['tiempo_h'] for x in h],[x['aire_C'] for x in h])],672)
    H.scatter(files,7,[('planes',[p['D_h'] for p in plans[:2]],[0,0]),('meta5%',[10,12],[5,5])],12)
    for num in [3,4,5,6]:
        t=xml(files[f'ppt/charts/chart{num}.xml'])
        for tx in t.findall('.//a:defRPr',NS):tx.set('sz','900')
        files[f'ppt/charts/chart{num}.xml']=out(t)
    for num in [4,5,6]:
        t=xml(files[f'ppt/charts/chart{num}.xml'])
        for ax in t.findall('.//c:valAx',NS):
            if ax.find('c:axPos',NS).get('val')=='b':ax.find('c:scaling/c:max',NS).set('val','720')
        layout=t.find('.//c:plotArea/c:layout',NS)
        if layout is None:layout=E.SubElement(t.find('.//c:plotArea',NS),q('c:layout'))
        layout.clear();manual=E.SubElement(layout,q('c:manualLayout'))
        for tag,val in [('layoutTarget','inner'),('xMode','factor'),('yMode','factor'),('wMode','factor'),('hMode','factor'),('x','.10'),('y','.08'),('w','.80'),('h','.70')]:E.SubElement(manual,q('c:'+tag),val=val)
        files[f'ppt/charts/chart{num}.xml']=out(t)
    changes=sorted(summary['cambios_espaciales'],key=lambda r:(r['curva'],r['clima']))
    bar(files,9,[r['curva'].replace('_',' ')+' '+r['clima'][-2:] for r in changes],[round(r['Delta'],10) for r in changes])
    t=xml(files['ppt/charts/chart9.xml'])
    for ax in t.findall('.//c:valAx',NS):
        ax.find('c:scaling/c:min',NS).set('val','-1');ax.find('c:scaling/c:max',NS).set('val','.4')
    files['ppt/charts/chart9.xml']=out(t)
    bar(files,8,['M1 SS','M2 SS','M3 SS','M4 SS','M1 22A','M2 22A','M3 22A','M4 22A'],[88.148355,95.715228,94.149018,100.166118,61.212021,82.446225,73.288830,73.628343])
    # Tres respaldos adicionales, conservando el diseño nativo del archivo recibido.
    clone_slide(files,slides,19,22);clear_pictures(slides[22]);text(slides[22],'Text 0','Cronograma físico de las once capas')
    layers=read(R/'resultados/diseno_circuitos_colocacion/esquema.json')['capas']
    native_table(slides[22],[['Capa','Cotas z [m]','V [m³]','Inicio [h]','Duración [h]','Fin [h]']]+[[str(c['id']),F(c['z_inferior_m'],1)+'–'+F(c['z_superior_m'],1),F(c['volumen_m3']),F(c['inicio_h'],3),F(c['duracion_h'],3),F(c['fin_h'],3)] for c in layers],x=.8,y=1.35,w=11.7,h=4.65,size=13)
    text(slides[22],'Text 4','t₀ = 19/11/2026 10:00 UTC−03:00 · término físico ≈ 20:36:47.\nActivación instantánea al inicio de cada capa; D incluye toda su duración física.\nUna operación continua; capas de avance ≠ esperas de endurecimiento ni objetos IFC.',size=14,x=.8,y=6.15,w=11.7,h=.8)
    clone_slide(files,slides,12,23);text(slides[23],'Text 0','Dominio activo, S25 y fuente por edad')
    H.equation(slides[23],'eq_b03_1',r'T_{25}=T_i+\frac{q^{\prime\prime}}{k}(d-0{,}025)',24,'166C65')
    H.equation(slides[23],'eq_b03_2',r'\Delta E_h=E_h(a+\Delta t)-E_h(a)',24,'1B74AA')
    H.equation(slides[23],'eq_b03_3',r'Q_j=\frac{E_{j+1}-E_j}{a_{j+1}-a_j}',24,'6E5A3A')
    native_table(slides[23],[['Parte','Tratamiento'],['Ωc(t)','solo hormigón colocado'],['S25(t)','25 mm bajo caras exteriores'],['Capa nueva','tapa cara previa; nace cara nueva'],['Interfaz','conducción, contacto perfecto'],['Fuente','Q(a) recibida en W/m³']],size=13)
    text(slides[23],'Text 7','d = centro a cara; q″ positivo hacia dentro. Reconstrucción lineal normal; ΔT usa el mismo instante.\nEₕ: integral trapezoidal cada 600 s; interpolación lineal. Misma curva completa por realización.\nEdad reiniciada por capa; cola nula tras el ensayo es hipótesis, no fin físico de la hidratación.',size=14,x=.6,y=5.3,w=12,h=1.1)
    clone_slide(files,slides,19,24);clear_pictures(slides[24]);text(slides[24],'Text 0','Por qué hacen falta manta y sombra')
    native_table(slides[24],alternatives,x=.6,y=1.4,w=12.1,h=2.15,widths=[3.5,1.6,2,1.6,1.6,1.8],size=14)
    text(slides[24],'Text 4','La manta frena el enfriamiento brusco de la superficie mientras el interior conserva calor.\nLa sombra reduce el aporte solar posterior: se conserva el 10 %, no se desprecia.\nSolo sombra: a 428 h, 30,29 − 6,82 = 23,48 K (M4_SS / 2024).\nLa combinación ensayada cumple; retirar la sombra o cambiar el frío exige recalcular.\nSin validación de instalación real, cinética de hidratación ni riesgo real ≤ 5 %.',size=20,x=.8,y=4.05,w=11.7,h=2.35)
    for color in H.shapes(slides[24],'Text 4')[0].findall('.//a:srgbClr',NS):color.set('val','202B33')
    # Índice: enlaces internos nuevos; los12 existentes permanecen intactos.
    relp='ppt/slides/_rels/slide9.xml.rels';rels=xml(files[relp])
    for dest,x,label in [(22,.6,'B13 · Cronograma'),(23,4.8,'B14 · S25 y fuente'),(24,9,'B15 · Manta + sombra')]:
        rid='rId'+str(max(int(r.get('Id')[3:]) for r in rels)+1)
        E.SubElement(rels,'{http://schemas.openxmlformats.org/package/2006/relationships}Relationship',Id=rid,Type=NS['r']+'/slide',Target=f'slide{dest}.xml')
        sp=new_text(slides[9],f'enlace_{dest}',label,x,6.9,3.8,.3,14)
        for rp in sp.findall('.//a:rPr',NS):E.SubElement(rp,q('a:hlinkClick'),{q('r:id'):rid,'action':'ppaction://hlinksldjump'})
    files[relp]=out(rels)
    # Cachés idénticas a las celdas XML serializadas (no solo aproximaciones float).
    for num in range(1,10):
        cp=f'ppt/charts/chart{num}.xml';t=xml(files[cp]);rels=xml(files[f'ppt/charts/_rels/chart{num}.xml.rels']);target=next(r.get('Target') for r in rels if r.get('Type').endswith('/package'));bp=posixpath.normpath(posixpath.join('ppt/charts',target))
        with ZipFile(BytesIO(files[bp])) as book:
            s=xml(book.read('xl/worksheets/sheet1.xml'));sn={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};cells={c.get('r'):c for c in s.findall('.//s:sheetData/s:row/s:c',sn)}
            for ref in t.xpath('.//c:numRef|.//c:strRef',namespaces=NS):
                form=ref.find('c:f',NS).text;m=re.fullmatch(r"'?Sheet1'?!(\$?[A-Z]+)\$?(\d+)(?::(\$?[A-Z]+)\$?(\d+))?",form);assert m,form
                col=m[1].replace('$','');assert col==(m[3] or m[1]).replace('$','');values=[]
                for n in range(int(m[2]),int(m[4] or m[2])+1):
                    c=cells[f'{col}{n}'];v=''.join(c.xpath('.//s:t/text()',namespaces=sn)) if c.get('t')=='inlineStr' else c.find('s:v',sn).text;values.append(v)
                cache=ref.find('c:numCache',NS)
                if cache is None:cache=ref.find('c:strCache',NS)
                H.cached(cache,values)
        files[cp]=out(t)
    script=read(A/'recursos/contenido_pre_entrega.json')
    for i in range(1,25):
        note=xml(files[f'ppt/notesSlides/notesSlide{i}.xml']);body=note.xpath('.//p:sp[p:nvSpPr/p:nvPr/p:ph/@type="body"]',namespaces=NS)[0]
        if i<=8:content=f"S{i} · {script['responsables'][i-1]} · {script['tiempos'][i-1]}\n\nDIÁLOGO\n{script['habla'][f'S{i}']}"
        else:content=f"Respaldo B{i-9:02d} (índice si B00). Fuera del recorrido principal.\n"+'\n'.join(''.join(s.xpath('.//a:t/text()',namespaces=NS)) for s in slides[i].findall('.//p:sp',NS))
        content+='\n\nFUENTES Y ALCANCE\nGUION_ORAL_F02.md; CIERRE_PUNTOS_RESTANTES.md; cierre_revision_final/RESULTADOS_CIERRE.md; CONFIGURACION_FINAL_REVISADA.json; METRICAS_144_FILAS.csv.\nTres matrices completas: 60 y55 a0,40m;60 a0,20m;300s,24pares cada una hasta672h, también336h. 72piezas,2045transiciones auditadas. Espacio24pares≤0,882K;tiempo2casos≤0,0014K.\nManta504h de edad local y sombra solar90% posterior; agua18°C, Uv5 y15kW equivalentes idealizados. La cola cero de la fuente no demuestra fin de hidratación. Pf0 únicamente bajo catálogo discreto y pesos declarados; sin validación de riesgo real, tuberías, sombra ni fisuración. SHA de la preentrega: consultar git log de este archivo.'
        H.reset_text(body,content);files[f'ppt/notesSlides/notesSlide{i}.xml']=out(note);files[f'ppt/slides/slide{i}.xml']=out(slides[i])
    # Eliminar únicamente declaraciones huérfanas heredadas del paquete fuente.
    types=xml(files['[Content_Types].xml'])
    for item in list(types):
        if E.QName(item).localname=='Override' and item.get('PartName','').lstrip('/') not in files:types.remove(item)
    files['[Content_Types].xml']=out(types)
    with ZipFile(W/'candidate.pptx','w',ZIP_DEFLATED) as z:
        for name,data in files.items():z.writestr(name,data)
    print('Candidato:24diapositivas,8principales;animaciones originales conservadas.')

if __name__=='__main__':main()
