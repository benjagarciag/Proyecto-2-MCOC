"""Convierte los clics de S1–S8 en animaciones automáticas a tiempos absolutos (XML).

Cada grupo de clic pasa a ser un bloque «después del anterior» dentro de una sola
secuencia que empieza al entrar en la lámina, con inicio en el tiempo del guion.
Los efectos «con el anterior» quedan dentro de su propio bloque (como los guarda PowerPoint).
Uso: python temporizar_xml.py <plan.json> <entrada.pptx> <salida.pptx>
"""
import json, re, sys, zipfile

plan_p, ent, sal = sys.argv[1:4]
plan = json.load(open(plan_p, encoding="utf-8"))
TRANS = 0.5  # las animaciones arrancan tras la transición de 0,5 s

INDEF = '<p:cond delay="indefinite"/>'


def retemporizar(xml, clics):
    i, j = xml.index("<p:timing>"), xml.index("</p:timing>") + len("</p:timing>")
    t = xml[i:j]
    a = t.index('nodeType="mainSeq">') ; a = t.index("<p:childTnLst>", a) + len("<p:childTnLst>")
    b = t.index("</p:childTnLst></p:cTn><p:prevCondLst>")
    cuerpo = t[a:b]
    # partir en pars de clic de primer nivel
    pars, prof, ini = [], 0, None
    for m in re.finditer(r"<p:par>|</p:par>", cuerpo):
        if m.group() == "<p:par>":
            if prof == 0: ini = m.start()
            prof += 1
        else:
            prof -= 1
            if prof == 0: pars.append(cuerpo[ini:m.end()])
    assert len(pars) == len(clics), (len(pars), len(clics))
    internos = []
    for k, par in enumerate(pars):
        assert INDEF in par
        # par interno = lo que está dentro del childTnLst del par de clic
        x = par.index("<p:childTnLst>") + len("<p:childTnLst>")
        y = par.rindex("</p:childTnLst>")
        dentro = par[x:y]
        assert dentro.count('<p:cond delay="0"/></p:stCondLst><p:childTnLst>') >= 1
        ms = int(max(0.0, clics[k] - TRANS) * 1000)
        dentro = dentro.replace('<p:stCondLst><p:cond delay="0"/></p:stCondLst>', f'<p:stCondLst><p:cond delay="{ms}"/></p:stCondLst>', 1)
        dentro = dentro.replace('nodeType="clickEffect"', 'nodeType="afterEffect"', 1)
        internos.append(dentro)
    nuevo = ('<p:par><p:cTn id="999990" fill="hold"><p:stCondLst><p:cond delay="indefinite"/>'
             '<p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>'
             + "".join(internos) + "</p:childTnLst></p:cTn></p:par>")
    t = t[:a] + nuevo + t[b:]
    return xml[:i] + t + xml[j:]


zin = zipfile.ZipFile(ent); zout = zipfile.ZipFile(sal, "w", zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    d = zin.read(it.filename)
    m = re.fullmatch(r"ppt/slides/slide(\d+)\.xml", it.filename)
    if m and 1 <= int(m.group(1)) <= 8:
        d = retemporizar(d.decode("utf-8"), plan[int(m.group(1)) - 1]["clics"]).encode("utf-8")
    zout.writestr(it, d)
zout.close()
print("ok", sal)
