"""PDF estático de las láminas renderizadas, con navegación interna preservada."""
from pathlib import Path
from zipfile import ZipFile
import re,sys
import xml.etree.ElementTree as E
from reportlab.pdfgen import canvas
from pypdf import PdfReader

R=Path.cwd()
PPTX=Path(sys.argv[1]) if len(sys.argv)>1 else R/'entregas/F02/presentacion/F02_Grupo6_radiacion.pptx'
PNG=Path(sys.argv[2]) if len(sys.argv)>2 else R/'.venv/cache/f02_radiacion_presentacion/artifact_actualizado'
PDF=Path(sys.argv[3]) if len(sys.argv)>3 else R/'entregas/F02/presentacion/F02_Grupo6_radiacion.pdf'
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}


def main():
    with ZipFile(PPTX) as z:
        root=E.fromstring(z.read('ppt/presentation.xml'));size=root.find('p:sldSz',ns)
        W,H=int(size.get('cx'))/12700,int(size.get('cy'))/12700
        count=len(root.findall('p:sldIdLst/p:sldId',ns));c=canvas.Canvas(str(PDF),pagesize=(W,H),pageCompression=1)
        c.setTitle('F02 Grupo6: modelo con radiación, horizontes14y28d')
        c.setAuthor('Benjamín García, Luis Noriega y Matías Stierling')
        for i in range(1,count+1):
            c.bookmarkPage(f'p{i}');c.drawImage(str(PNG/f'slide{i}.png'),0,0,width=W,height=H)
            slide=E.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
            rels={r.get('Id'):r for r in E.fromstring(z.read(f'ppt/slides/_rels/slide{i}.xml.rels'))}
            for sp in slide.findall('.//p:sp',ns):
                xfrm=sp.find('p:spPr/a:xfrm',ns)
                if xfrm is None:continue
                off=xfrm.find('a:off',ns);ext=xfrm.find('a:ext',ns)
                x,y,w,h=[int(el.get(key))/12700 for el,key in [(off,'x'),(off,'y'),(ext,'cx'),(ext,'cy')]]
                rect=(x,H-y-h,x+w,H-y)
                for link in sp.findall('.//a:hlinkClick',ns):
                    rel=rels.get(link.get('{'+ns['r']+'}id'))
                    if rel is None:continue
                    target=rel.get('Target');m=re.search(r'slide(\d+)\.xml$',target)
                    if m:c.linkRect('',f'p{m[1]}',rect,relative=0,thickness=0)
                    elif target.startswith('https://'):c.linkURL(target,rect,relative=0,thickness=0)
            c.showPage()
        c.save()
    reader=PdfReader(PDF);assert len(reader.pages)==24
    assert len(reader.pages[8].get('/Annots',[]))>=15
    print('PDF24 páginas y navegación de consulta:',PDF)


if __name__=='__main__':main()
