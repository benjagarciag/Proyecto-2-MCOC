"""Conserva animaciones y geometría del original, incorpora textos Artifact y evidencia actual.

Ejecutar con Python del runtime documental (lxml/openpyxl disponibles).
"""
from copy import deepcopy
from io import BytesIO
import importlib.util,json,math,posixpath,re
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
from openpyxl import load_workbook

R=Path.cwd();A=R/'entregas/F02/presentacion';B=R/'.venv/cache/f02_radiacion_presentacion'
D=json.loads((A/'recursos/contenido_radiacion.json').read_text(encoding='utf-8'))
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','c':'http://schemas.openxmlformats.org/drawingml/2006/chart','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships','m':'http://schemas.openxmlformats.org/officeDocument/2006/math','a14':'http://schemas.microsoft.com/office/drawing/2010/main','mc':'http://schemas.openxmlformats.org/markup-compatibility/2006'}
q=lambda tag:'{'+NS[tag.split(':')[0]]+'}'+tag.split(':')[1]
def xml(data):return E.fromstring(data)
def out(t):return E.tostring(t,encoding='UTF-8',xml_declaration=True,standalone=True)
def fmt(x,d=2):return f'{x:.{d}f}'.replace('.',',')
def shapes(t,name):return t.xpath('.//p:sp[p:nvSpPr/p:cNvPr/@name=$name]',namespaces=NS,name=name)
def txt(t):return ''.join(t.xpath('.//a:t/text()',namespaces=NS))
def reset_text(t,text):
    body=t.find('a:txBody',NS) if E.QName(t).localname=='tc' else t.find('p:txBody',NS)
    assert body is not None
    old=body.find('a:p',NS);par=deepcopy(old) if old is not None else E.Element(q('a:p'))
    style=deepcopy(par.find('.//a:rPr',NS)) if par.find('.//a:rPr',NS) is not None else E.Element(q('a:rPr'),sz='1600')
    for child in list(par):
        if E.QName(child).localname!='pPr':par.remove(child)
    for child in list(body):
        if E.QName(child).localname=='p':body.remove(child)
    for i,line in enumerate(text.split('\n')):
        p=deepcopy(par);r=E.SubElement(p,q('a:r'));r.append(deepcopy(style));E.SubElement(r,q('a:t')).text=line;body.append(p)
def fontsize(t,points):
    for r in t.findall('.//a:rPr',NS)+t.findall('.//a:defRPr',NS)+t.findall('.//a:endParaRPr',NS):r.set('sz',str(round(points*100)))
def frame(t,**kw):
    x=t.find('p:spPr/a:xfrm',NS);assert x is not None
    for k,v in kw.items():
        el=x.find('a:off' if k in ['x','y'] else 'a:ext',NS)
        el.set({'w':'cx','h':'cy'}.get(k,k),str(round(v*914400)))
def table(t,index,rows):
    tab=t.findall('.//a:tbl',NS)[index];trs=tab.findall('a:tr',NS);assert len(trs)==len(rows)
    for tr,vals in zip(trs,rows):
        cells=tr.findall('a:tc',NS);assert len(cells)==len(vals)
        for tc,value in zip(cells,vals):reset_text(tc,str(value))
def replace_image(files,t,name,file):
    pic=t.xpath('.//p:pic[p:nvPicPr/p:cNvPr/@name=$name]',namespaces=NS,name=name)[0]
    rel=pic.find('.//a:blip',NS).get(q('r:embed'))
    return rel,Path(file).read_bytes()

spec=importlib.util.spec_from_file_location('post_original',A/'postproceso.py')
post=importlib.util.module_from_spec(spec);spec.loader.exec_module(post)
post.SIMBOLOS.update(alpha='α',epsilon='ε',sigma='σ',chi='χ')
def equation(t,name,tex,points,color='202B33'):
    for sp in shapes(t,name):
        body=sp.find('p:txBody',NS)
        for child in list(body):
            if E.QName(child).localname=='p':body.remove(child)
        par=E.SubElement(body,q('a:p'))
        if sp.getparent().tag==q('mc:Choice'):
            wrapper=E.SubElement(par,q('a14:m'))
            om=post.omml(tex,points,color,'left')
            namespace=f'<root xmlns:a="{NS["a"]}">'+om+'</root>'
            wrapper.append(E.fromstring(namespace.encode())[0])
        else:
            run=E.SubElement(par,q('a:r'));E.SubElement(run,q('a:rPr'),sz=str(points*100));E.SubElement(run,q('a:t')).text=tex.replace('\\','')


def cached(parent,values,kind='num'):
    for child in list(parent):
        if E.QName(child).localname in ['ptCount','pt','lvl']:parent.remove(child)
    E.SubElement(parent,q('c:ptCount'),val=str(len(values)))
    for i,v in enumerate(values):
        if v is None:continue
        pt=E.SubElement(parent,q('c:pt'),idx=str(i));E.SubElement(pt,q('c:v')).text=str(v)


def sheet_bytes(data,rows):
    wb=load_workbook(BytesIO(data));ws=wb['Sheet1'];ws.delete_rows(1,ws.max_row)
    for row in rows:ws.append(row)
    b=BytesIO();wb.save(b);return b.getvalue()


def scatter(files,number,series,xmax=None):
    chart=f'ppt/charts/chart{number}.xml';t=xml(files[chart]);sers=t.findall('.//c:ser',NS);assert len(sers)==len(series)
    series=[(name,[round(float(v),10) for v in x],[round(float(v),10) for v in y]) for name,x,y in series]
    xx=[];yy=[[] for _ in series]
    for j,(name,x,y) in enumerate(series):
        assert len(x)==len(y)
        xx.extend(x)
        for k in range(len(series)):yy[k].extend(y if k==j else [None]*len(x))
    offset=0
    for j,(s,(name,x,y)) in enumerate(zip(sers,series)):
        namecache=s.find('c:tx/c:strRef/c:strCache',NS);cached(namecache,[name],'str')
        for key,column,values in [('xVal','A',x),('yVal',chr(66+j),y)]:
            ref=s.find(f'c:{key}/c:numRef',NS);ref.find('c:f',NS).text=f'Sheet1!${column}${offset+2}:${column}${offset+len(x)+1}'
            cached(ref.find('c:numCache',NS),values)
        offset+=len(x)
    if xmax is not None:
        for axis in t.findall('.//c:valAx',NS):
            if axis.find('c:axPos',NS).get('val')=='b':axis.find('c:scaling/c:max',NS).set('val',str(xmax))
    rels=xml(files[f'ppt/charts/_rels/chart{number}.xml.rels'])
    target=next(r.get('Target') for r in rels if r.get('Type').endswith('/package'))
    file=posixpath.normpath(posixpath.join('ppt/charts',target))
    rows=[['Horas']+[s[0] for s in series]]+[[x]+[y[i] for y in yy] for i,x in enumerate(xx)]
    files[file]=sheet_bytes(files[file],rows);files[chart]=out(t)


def main():
    with ZipFile(A/'F02_Grupo6_presentacion.pptx') as z:files={n:z.read(n) for n in z.namelist() if not n.endswith('/')}
    with ZipFile(B/'borrador_actualizado_artifact.pptx') as z:authored={n:z.read(n) for n in z.namelist()}
    ediciones=json.loads((B/'ediciones.json').read_text())
    slides={i:xml(files[f'ppt/slides/slide{i}.xml']) for i in range(1,22)}
    for ed in ediciones:
        draft=xml(authored[f"ppt/slides/slide{ed['slide']}.xml"])
        nuevas=shapes(draft,ed['name']);assert nuevas,ed
        body=nuevas[0].find('p:txBody',NS)
        for sp in shapes(slides[ed['slide']],ed['name']):
            old=sp.find('p:txBody',NS);assert old is not None
            for child in list(old):
                if E.QName(child).localname=='p':old.remove(child)
            for par in body.findall('a:p',NS):old.append(deepcopy(par))
    # Cambios puntuales de geometría para que el nuevo contenido encaje.
    for sp in shapes(slides[3],'s3_hl5'):fontsize(sp,12);frame(sp,h=.65)
    for sp in shapes(slides[3],'s3_sup'):fontsize(sp,11);frame(sp,h=.5)
    for sp in shapes(slides[5],'s5_pico'):frame(sp,x=3.25,w=2.0)
    for sp in shapes(slides[5],'s5_14d'):frame(sp,x=7.8,w=.8);fontsize(sp,11)
    for sp in shapes(slides[6],'s6_climaU'):fontsize(sp,10);frame(sp,h=.45)
    for sp in shapes(slides[8],'Text 3'):frame(sp,w=8.0);fontsize(sp,16)
    for sp in shapes(slides[8],'s8_lim'):fontsize(sp,14)
    for sp in shapes(slides[13],'Text 11'):frame(sp,w=10.7);fontsize(sp,13)
    # La barra debe representar la nueva fracción de20K, no solo cambiar el rótulo.
    for sp in slides[8].findall('.//p:sp',NS):
        fill=sp.find('p:spPr/a:solidFill/a:srgbClr',NS)
        if fill is not None and fill.get('val')=='743E99':frame(sp,w=6.4*D['fina']['Delta']/20)
    esp=D['resumen']['max_cambio_espacial_Delta'];temp=D['resumen']['max_cambio_temporal_Delta']
    table(slides[4],0,[['Espacio','Tiempo'],['0,40 → 0,20 m','300 → 150 s'],['24 escenarios','3 casos decisivos'],[f'Cambio ΔT\n≤ {fmt(esp,3)} K',f'Cambio ΔT\n≤ {fmt(temp,4)} K'],['misma clasificación','misma clasificación']])
    for tc in slides[4].findall('.//a:tbl/a:tr',NS)[3].findall('a:tc',NS):fontsize(tc,15)
    plans=[p for p in D['resumen']['planes'] if p['h']==.4]
    equation(slides[7],'eq_s7',r'D\geq\frac{V}{Q}=\frac{636{,}775\ \mathrm{m}^3}{60\ \mathrm{m}^3/\mathrm{h}}=10{,}61\ \mathrm{h}',22,'166C65')
    table(slides[7],0,[['Ritmo [m³/h]','D [h]','P_T','P_Δ','P_f','Cumple']]+[[p['q'],fmt(p['D_h']),fmt(100*p['riesgo']['P_T'])+' %',fmt(100*p['riesgo']['P_delta'])+' %',fmt(100*p['riesgo']['P_union'])+' %','Sí' if p['riesgo']['P_union']<=.05 else 'No'] for p in plans])
    table(slides[12],0,[['Borde','Condición'],['Inicial','12 °C al colocar cada capa'],['Entre capas','contacto perfecto'],['Base','reservorio15 °C, sin inercia'],['Laterales','expuestos, sin relleno'],['Radiación','solar + onda larga explícitas']])
    equation(slides[12],'eq_b03_2',r"q''=h(T_a-T_s)+\alpha I+\epsilon\sigma(T_{rad,K}^{4}-T_{s,K}^{4})",19,'1B74AA')
    equation(slides[12],'eq_b03_3',r"q''=\frac{T_s-T_i}{d/k+R_{capas}}",23,'6E5A3A')
    for sp in shapes(slides[12],'eq_b03_2'):frame(sp,x=.6,y=2.65,w=7.6,h=1.0)
    for sp in shapes(slides[12],'eq_b03_3'):frame(sp,x=.6,y=3.95,w=7.0,h=1.0)
    for sp in shapes(slides[12],'Text 7'):frame(sp,x=.6,y=5.2,w=11.9,h=1.0);fontsize(sp,16)
    equation(slides[15],'eq_b06_1',r'P_{frío}=\min(\sum_i \chi_i U_v V_i\max(T_i-18,0),15\ \mathrm{kW})',23,'1B74AA')
    equation(slides[17],'eq_b08_3',r'\Delta t\leq 0{,}8\frac{C_i}{\sum G_{ef}},\quad\Delta t\leq300\ \mathrm{s}',22,'166C65')
    row=D['datos']['evento'];peak=D['datos']['pico']
    table(slides[18],0,[['Curva','Clima','Peso','Tmax [°C]','ΔTmax [K]','I_T','I_Δ','I_F'],['M4_SS','ERA5-2024','1/24',fmt(peak['valor']),fmt(row['valor']),'0','0','0']])
    table(slides[19],0,[['Plan','Malla','D [h]','Tmax14d [°C]','ΔT14d [K]','MargenΔ [K]','P_f']]+[[str(p['q'])+' m³/h'+(' fina' if p['h']==.2 else ''),fmt(p['h'])+' m',fmt(p['D_h']),fmt(p['Tmax']),fmt(p['Delta']),fmt(20-p['Delta']),fmt(100*p['riesgo']['P_union'])+' %'] for p in D['resumen']['planes']])
    # Imágenes científicas sustituidas, conservando marco y relación de aspecto.
    images=[(5,'s5_corte',R/'entregas/F02/evidencia_f02_radiacion/05_corte_evento_267h.png')]
    for i,name,file in images:
        rel,binary=replace_image(files,slides[i],name,file)
        rels=xml(files[f'ppt/slides/_rels/slide{i}.xml.rels'])
        target=next(e.get('Target') for e in rels if e.get('Id')==rel)
        files[posixpath.normpath(posixpath.join('ppt/slides',target))]=binary
    # B10: único gráfico de corte de esta diapositiva, nuevo instante común336h.
    for i,file in [(19,R/'entregas/F02/evidencia_f02_radiacion/06_cortes_comunes_336h.png'),(11,R/'entregas/F02/evidencia_f02_radiacion/07_clima_radiacion.png')]:
        pics=slides[i].findall('.//p:pic',NS);assert len(pics)==1
        rid=pics[0].find('.//a:blip',NS).get(q('r:embed'))
        rels=xml(files[f'ppt/slides/_rels/slide{i}.xml.rels']);target=next(e.get('Target') for e in rels if e.get('Id')==rid)
        files[posixpath.normpath(posixpath.join('ppt/slides',target))]=file.read_bytes()
    # Normalizar referencias de las fuentes/climas originales sin cambiar sus valores.
    # Cada serie referencia solo sus filas válidas, sin cachés dispersas compartidas.
    for number in [3,4,5,6]:
        original_chart=xml(files[f'ppt/charts/chart{number}.xml']);series=[]
        for s in original_chart.findall('.//c:ser',NS):
            name=s.find('c:tx/c:strRef/c:strCache/c:pt/c:v',NS).text
            puntos=[]
            xvals={int(pt.get('idx')):float(pt.find('c:v',NS).text) for pt in s.findall('c:xVal/c:numRef/c:numCache/c:pt',NS)}
            for pt in s.findall('c:yVal/c:numRef/c:numCache/c:pt',NS):
                v=pt.find('c:v',NS).text
                if v not in [None,'']:puntos.append((xvals[int(pt.get('idx'))],float(v)))
            series.append((name,[x for x,y in puntos],[y for x,y in puntos]))
        scatter(files,number,series)
    # Historias nativas editables y libro embebido con los mismos valores.
    h=D['datos']['historia'];sample=h[::12]
    if sample[-1]['tiempo_h']!=336:sample.append(h[-1])
    # El máximo de una cara puede ser el límite izquierdo del cambio horario.
    # Se incorpora la medición exacta del evento, antes del registro posterior.
    sample.append(dict(tiempo_h=row['tiempo_h'],Tmax_C=row['Tmax_C'],Tmin_S25_C=row['Tmin_S25_C'],DeltaT_K=row['valor']))
    sample.sort(key=lambda r:(r['tiempo_h'],0 if r.get('DeltaT_K')==row['valor'] else 1))
    x=[r['tiempo_h'] for r in sample]
    scatter(files,1,[('Tmax hormigón',x,[r['Tmax_C'] for r in sample]),('Tmin S25',x,[r['Tmin_S25_C'] for r in sample]),('14 días',[336,336],[0,50])],336)
    scatter(files,2,[('ΔT',x,[r['DeltaT_K'] for r in sample]),('límite20K',[0,336],[20,20]),('14 días',[336,336],[0,25]),('evento267h',[267],[row['valor']])],336)
    scatter(files,7,[('planes',[p['D_h'] for p in plans],[100*p['riesgo']['P_union'] for p in plans]),('meta5%',[10,15],[5,5])])
    chart='ppt/charts/chart9.xml';t=xml(files[chart]);ser=t.find('.//c:ser',NS)
    changes=sorted(D['resumen']['cambios_espaciales'],key=lambda r:(r['curva'],r['clima']))
    cats=[r['curva'].replace('_',' ')+' '+r['clima'][-2:] for r in changes];vals=[round(r['Delta'],10) for r in changes]
    cat=ser.find('c:cat',NS);cat.clear();ref=E.SubElement(cat,q('c:strRef'));E.SubElement(ref,q('c:f')).text='Sheet1!$A$2:$A$25';ca=E.SubElement(ref,q('c:strCache'));cached(ca,cats,'str')
    cached(ser.find('c:val/c:numRef/c:numCache',NS),vals)
    for ax in t.findall('.//c:valAx',NS):
        sc=ax.find('c:scaling',NS)
        sc.find('c:min',NS).set('val',str(math.floor((min(vals)-.1)*5)/5));sc.find('c:max',NS).set('val',str(max(.2,math.ceil((max(vals)+.1)*5)/5)))
    nombre=ser.find('c:tx/c:strRef/c:strCache/c:pt/c:v',NS).text
    files[chart]=out(t);file='ppt/embeddings/Microsoft_Excel_Worksheet9.xlsx';files[file]=sheet_bytes(files[file],[['Escenario',nombre]]+list(zip(cats,vals)))
    chart='ppt/charts/chart8.xml';t=xml(files[chart]);ser=t.find('.//c:ser',NS)
    cat=ser.find('c:cat',NS)
    cats=cat.xpath('.//c:lvl[1]/c:pt/c:v/text()',namespaces=NS)
    vals=[float(v) for v in ser.xpath('c:val/c:numRef/c:numCache/c:pt/c:v/text()',namespaces=NS)]
    assert len(cats)==len(vals)==8
    cat.clear();ref=E.SubElement(cat,q('c:strRef'));E.SubElement(ref,q('c:f')).text='Sheet1!$A$2:$A$9';cached(E.SubElement(ref,q('c:strCache')),cats,'str')
    nombre=ser.find('c:tx/c:strRef/c:strCache/c:pt/c:v',NS).text
    files[chart]=out(t);file='ppt/embeddings/Microsoft_Excel_Worksheet8.xlsx';files[file]=sheet_bytes(files[file],[['Fuente',nombre]]+list(zip(cats,vals)))
    # Refrescar cada caché desde el literal XML REAL serializado en el libro.
    # Evita diferencias de representación binaria/decimal de openpyxl.
    for number in range(1,10):
        chart=f'ppt/charts/chart{number}.xml';t=xml(files[chart])
        rels=xml(files[f'ppt/charts/_rels/chart{number}.xml.rels'])
        target=next(r.get('Target') for r in rels if r.get('Type').endswith('/package'))
        file=posixpath.normpath(posixpath.join('ppt/charts',target))
        with ZipFile(BytesIO(files[file])) as book:
            sheet=xml(book.read('xl/worksheets/sheet1.xml'))
            sn={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            cells={cell.get('r'):cell for cell in sheet.findall('.//s:sheetData/s:row/s:c',sn)}
            for ref in t.xpath('.//c:numRef|.//c:strRef',namespaces=NS):
                formula=ref.find('c:f',NS).text
                match=re.fullmatch(r"'?Sheet1'?!(\$?[A-Z]+)\$?(\d+)(?::(\$?[A-Z]+)\$?(\d+))?",formula)
                assert match,formula
                col=match[1].replace('$','');lastcol=(match[3] or match[1]).replace('$','');assert col==lastcol
                start=int(match[2]);end=int(match[4] or match[2]);values=[]
                for rownum in range(start,end+1):
                    cell=cells[f'{col}{rownum}']
                    if cell.get('t')=='inlineStr':value=''.join(cell.xpath('.//s:t/text()',namespaces=sn))
                    else:value=cell.find('s:v',sn).text
                    values.append(value)
                cache=ref.find('c:numCache',NS)
                if cache is None:cache=ref.find('c:strCache',NS)
                cached(cache,values)
        files[chart]=out(t)
    # Notas completas: el diálogo coincide con el Markdown actualizado.
    for i in range(1,22):
        note=xml(files[f'ppt/notesSlides/notesSlide{i}.xml'])
        body=note.xpath('.//p:sp[p:nvSpPr/p:nvPr/p:ph/@type="body"]',namespaces=NS)[0]
        if i<=8:
            content=f"S{i} · {D['responsables'][i-1]} · {D['tiempos'][i-1]}\n\nDIÁLOGO\n{D['habla'][f'S{i}']}\n\nFUENTES\nCOMPARACION_CIRCUITOS_FINAL.md; ECUACIONES_MODELO_VIGENTE.md; INTERCAMBIO_TUBERIAS.md; evidencia_f02_radiacion/.\n\nALCANCE\nSolar+LW activas. Métricas0–336h. Uv y agua idealizados; caudal no determina transferencia. Seguimiento posterior excedeΔ20K, con picos pendientes."
        elif i==9:content='Índice de consultaB01–B12. Fuera del recorrido de siete minutos. Enlaces conservados.'
        else:
            content=f"Consulta B{i-9:02d}. Fuente: BRIEF_DIAPOSITIVAS_F02.md y GUION_ORAL_F02.md actualizados con radiación.\n\nEVIDENCIA\nCinco matrices completas,129piezas a336h y auditoría aprobada. α0,6/ε0,9 supuestas. Refrigeración equivalente Uv5/agua18/tope15kW, sin pared ni agua axial resueltas.\n\nCLAVES\nEl seguimiento posterior600–672h conserva excedencias. Malla fina completa solo candidata60. Seis contrastes finos de otras tasas son selectivos. El IFC conserva cinco objetos y el plan externo once capas. No hay riesgo real≤5% ni ausencia de grietas demostrados."
        reset_text(body,content);files[f'ppt/notesSlides/notesSlide{i}.xml']=out(note)
        files[f'ppt/slides/slide{i}.xml']=out(slides[i])
    # El original contiene tipos de20 masters que ya no existen en el paquete.
    # Se retiran solo esas declaraciones huérfanas; los masters usados se conservan.
    types=xml(files['[Content_Types].xml'])
    for item in list(types):
        if E.QName(item).localname=='Override' and item.get('PartName','').lstrip('/') not in files:
            types.remove(item)
    files['[Content_Types].xml']=out(types)
    candidate=B/'candidate.pptx'
    with ZipFile(candidate,'w',ZIP_DEFLATED) as z:
        for name,data in files.items():z.writestr(name,data)
    print('Candidato actualizado conservando animaciones:',candidate)


if __name__=='__main__':main()
