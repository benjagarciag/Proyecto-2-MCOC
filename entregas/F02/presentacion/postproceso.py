"""Postproceso del PPTX base: animaciones por clic, transiciones, ecuaciones OMML
y ajustes de gráficos (huecos, líneas discontinuas, marcadores).

Uso: python postproceso.py base.pptx salida.pptx
Lee recursos/animaciones.json escrito por construir_pptx.js.
"""
from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

AQUI = Path(__file__).resolve().parent
CFG = json.loads((AQUI / "recursos/animaciones.json").read_text(encoding="utf-8"))

NS_MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"
NS_A14 = "http://schemas.microsoft.com/office/drawing/2010/main"
NS_M = "http://schemas.openxmlformats.org/officeDocument/2006/math"

# ======================================================== TeX mínimo -> OMML
SIMBOLOS = {
    "rho": "ρ", "partial": "∂", "nabla": "∇", "cdot": "·", "Delta": "Δ", "Omega": "Ω", "cup": "∪",
    "geq": "≥", "leq": "≤", "approx": "≈", "{": "{", "}": "}", "%": "%", "quad": " ", "qquad": "  ",
    " ": " ", ",": " ", "max": "max", "min": "min",
}


class Tex:
    def __init__(self, src: str, sz: int, color: str):
        self.s, self.i, self.sz, self.color = src, 0, sz, color

    def run(self, texto: str, recto: bool) -> str:
        mr = '<m:rPr><m:sty m:val="p"/></m:rPr>' if recto else ""
        ar = (f'<a:rPr lang="es-CL" sz="{self.sz}" i="{0 if recto else 1}"><a:solidFill><a:srgbClr val="{self.color}"/></a:solidFill>'
              '<a:latin typeface="Cambria Math" panose="02040503050406030204" pitchFamily="18" charset="0"/>'
              '<a:cs typeface="Cambria Math"/></a:rPr>')
        esp = ' xml:space="preserve"' if texto != texto.strip() or " " in texto else ""
        return f"<m:r>{mr}{ar}<m:t{esp}>{escape(texto)}</m:t></m:r>"

    def peek(self):
        return self.s[self.i] if self.i < len(self.s) else None

    def comando(self) -> str:
        self.i += 1  # '\'
        c = self.peek()
        if c is not None and not c.isalpha():
            self.i += 1
            return c
        j = self.i
        while self.i < len(self.s) and self.s[self.i].isalpha():
            self.i += 1
        return self.s[j:self.i]

    def grupo(self) -> list[str]:
        """Lee {..} o un solo átomo."""
        while self.peek() == " ":
            self.i += 1
        if self.peek() == "{":
            self.i += 1
            atomos = self.secuencia("}")
            self.i += 1
            return atomos
        return [self.atomo()]

    def atomo(self, recto_forzado: bool = False) -> str:
        c = self.peek()
        if c == "\\":
            cmd = self.comando()
            if cmd == "frac":
                num, den = "".join(self.grupo()), "".join(self.grupo())
                return f"<m:f><m:num>{num}</m:num><m:den>{den}</m:den></m:f>"
            if cmd == "mathrm":
                self.i += 1  # {
                j = self.s.index("}", self.i)
                txt, self.i = self.s[self.i:j], j + 1
                return self.run(txt, True)
            if cmd == "dot":
                e = "".join(self.grupo())
                return f'<m:acc><m:accPr><m:chr m:val="̇"/></m:accPr><m:e>{e}</m:e></m:acc>'
            if cmd == "sum":
                sub = sup = ""
                while self.peek() in ("_", "^"):
                    k = self.s[self.i]; self.i += 1
                    g = "".join(self.grupo())
                    sub, sup = (g, sup) if k == "_" else (sub, g)
                cuerpo = "".join(self.secuencia(None, cortar=True))
                hide = ('<m:subHide m:val="1"/>' if not sub else "") + ('<m:supHide m:val="1"/>' if not sup else "")
                return (f'<m:nary><m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/>{hide}</m:naryPr>'
                        f"<m:sub>{sub}</m:sub><m:sup>{sup}</m:sup><m:e>{cuerpo}</m:e></m:nary>")
            if cmd == "left":
                abre = self.s[self.i]; self.i += 1
                cierra = {"(": ")", "[": "]"}[abre]
                dentro = "".join(self.secuencia("\\right"))
                self.i += len("\\right") + 1
                return (f'<m:d><m:dPr><m:begChr m:val="{abre}"/><m:endChr m:val="{cierra}"/></m:dPr>'
                        f"<m:e>{dentro}</m:e></m:d>")
            if cmd in SIMBOLOS:
                return self.run(SIMBOLOS[cmd], cmd not in ("rho", "Omega"))
            raise ValueError(f"comando no soportado: \\{cmd}")
        if c == "{":
            return "".join(self.grupo())
        if c.isalpha():
            j = self.i
            while self.i < len(self.s) and self.s[self.i].isalpha():
                self.i += 1
            palabra = self.s[j:self.i]
            return self.run(palabra, len(palabra) > 2)  # palabras rectas; letras e índices (ij) itálicos
        if c.isdigit():
            j = self.i
            while self.i < len(self.s) and self.s[self.i].isdigit():
                self.i += 1
            return self.run(self.s[j:self.i], True)
        self.i += 1
        mapa = {"-": "−", "*": "·"}
        return self.run(mapa.get(c, c), True)

    def secuencia(self, fin: str | None, cortar: bool = False) -> list[str]:
        atomos: list[str] = []
        prof = 0
        while self.i < len(self.s):
            if fin and self.s.startswith(fin, self.i):
                break
            c = self.peek()
            if cortar:
                prof += {"(": 1, ")": -1}.get(c, 0)
            if cortar and atomos and prof == 0 and (c in "+-=," or self.s.startswith("\\right", self.i) or self.s.startswith("\\quad", self.i)
                                                    or self.s.startswith("\\qquad", self.i)):
                break
            if cortar and c == "}":
                break
            if c == " ":
                self.i += 1
                continue
            if c in "_^":
                base = atomos.pop() if atomos else ""
                sub = sup = None
                while self.peek() in ("_", "^"):
                    k = self.s[self.i]; self.i += 1
                    g = "".join(self.grupo())
                    if k == "_":
                        sub = g
                    else:
                        sup = g
                if sub is not None and sup is not None:
                    atomos.append(f"<m:sSubSup><m:e>{base}</m:e><m:sub>{sub}</m:sub><m:sup>{sup}</m:sup></m:sSubSup>")
                elif sub is not None:
                    atomos.append(f"<m:sSub><m:e>{base}</m:e><m:sub>{sub}</m:sub></m:sSub>")
                else:
                    atomos.append(f"<m:sSup><m:e>{base}</m:e><m:sup>{sup}</m:sup></m:sSup>")
                continue
            # agrupar palabras para subíndices tipo T_{max,\Omega}: cada átomo es un elemento
            antes = self.i
            a = self.atomo()
            # una palabra de letras sueltas italic genera varias corridas; si sigue _ o ^ solo la última es base
            if self.peek() in ("_", "^") and a.count("<m:r>") > 1 and "<m:f>" not in a and self.s[antes].isalpha():
                partes = re.findall(r"<m:r>.*?</m:r>", a)
                atomos.extend(partes)
            else:
                atomos.append(a)
        return atomos


def omml(tex: str, sz_pt: int, color: str, align: str) -> str:
    cuerpo = "".join(Tex(tex, sz_pt * 100, color).secuencia(None))
    jc = {"left": "left", "center": "center"}.get(align, "left")
    return (f'<m:oMathPara xmlns:m="{NS_M}"><m:oMathParaPr><m:jc m:val="{jc}"/></m:oMathParaPr>'
            f"<m:oMath>{cuerpo}</m:oMath></m:oMathPara>")


def insertar_ecuaciones(xml: str) -> str:
    for nombre, eq in CFG["eq"].items():
        m = re.search(r'<p:sp>(?:(?!</p:sp>).)*?<p:cNvPr id="\d+" name="' + re.escape(nombre) + r'".*?</p:sp>', xml, re.S)
        if not m:
            continue
        sp = m.group(0)
        mat = omml(eq["tex"], int(eq["size"]), eq["color"], eq["align"])
        choice = re.sub(r"(<p:txBody>.*?<a:lstStyle/>).*(</p:txBody>)",
                        lambda g: g.group(1) + f'<a:p><a:pPr algn="{"ctr" if eq["align"] == "center" else "l"}"/>'
                        f"<a14:m>{mat}</a14:m><a:endParaRPr lang=\"es-CL\" sz=\"{int(eq['size']) * 100}\"/></a:p>" + g.group(2),
                        sp, flags=re.S)
        alt = (f'<mc:AlternateContent xmlns:mc="{NS_MC}"><mc:Choice xmlns:a14="{NS_A14}" Requires="a14">{choice}</mc:Choice>'
               f"<mc:Fallback>{sp}</mc:Fallback></mc:AlternateContent>")
        xml = xml.replace(sp, alt, 1)
    return xml


# ============================================================== animaciones
class Ids:
    def __init__(self):
        self.n = 2

    def __call__(self):
        self.n += 1
        return self.n


def efecto(fx: str, spid: str, dur: int, ids: Ids) -> tuple[str, int, int]:
    """Devuelve (comportamientos, presetID, subtipo)."""
    tgt = f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
    vis = (f'<p:set><p:cBhvr><p:cTn id="{ids()}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
           f'{tgt}<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
           '<p:to><p:strVal val="visible"/></p:to></p:set>')
    if fx == "fade":
        return vis + f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{ids()}" dur="{dur}"/>{tgt}</p:cBhvr></p:animEffect>', 10, 0
    if fx == "wipeL":
        return vis + f'<p:animEffect transition="in" filter="wipe(left)"><p:cBhvr><p:cTn id="{ids()}" dur="{dur}"/>{tgt}</p:cBhvr></p:animEffect>', 22, 8
    if fx == "wipeU":
        return vis + f'<p:animEffect transition="in" filter="wipe(down)"><p:cBhvr><p:cTn id="{ids()}" dur="{dur}"/>{tgt}</p:cBhvr></p:animEffect>', 22, 4
    if fx == "zoomIn":
        def esc(attr):
            return (f'<p:anim calcmode="lin" valueType="num"><p:cBhvr><p:cTn id="{ids()}" dur="{dur}" fill="hold"/>{tgt}'
                    f'<p:attrNameLst><p:attrName>{attr}</p:attrName></p:attrNameLst></p:cBhvr><p:tavLst>'
                    f'<p:tav tm="0"><p:val><p:fltVal val="0"/></p:val></p:tav>'
                    f'<p:tav tm="100000"><p:val><p:strVal val="#{attr}"/></p:val></p:tav></p:tavLst></p:anim>')
        return (vis + esc("ppt_w") + esc("ppt_h")
                + f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{ids()}" dur="{dur}"/>{tgt}</p:cBhvr></p:animEffect>'), 53, 16
    raise ValueError(fx)


def timing(xml: str, grupos: list[list[dict]]) -> str:
    ids_por_nombre = dict((n, i) for i, n in re.findall(r'<p:cNvPr id="(\d+)" name="([^"]*)"', xml))
    tipo = {}
    for i, n in re.findall(r'<p:cNvPr id="(\d+)" name="([^"]*)"', xml):
        pass
    for m in re.finditer(r'<p:(sp|pic|graphicFrame)>\s*<p:nv\w+>\s*<p:cNvPr id="(\d+)"', xml):
        tipo.setdefault(m.group(2), m.group(1))
    ids = Ids()
    clics_xml, bld = [], {}
    for grupo in grupos:
        items = []
        for k, it in enumerate(grupo):
            spid = ids_por_nombre.get(it["n"])
            if spid is None:
                raise KeyError(f"objeto sin nombre en diapositiva: {it['n']}")
            ctn = ids()
            beh, preset, sub = efecto(it["fx"], spid, int(it.get("t", 400)), ids)
            nodo = "clickEffect" if k == 0 else "withEffect"
            items.append(f'<p:par><p:cTn id="{ctn}" presetID="{preset}" presetClass="entr" presetSubtype="{sub}" fill="hold" grpId="0" nodeType="{nodo}">'
                         f'<p:stCondLst><p:cond delay="{int(it.get("d", 0))}"/></p:stCondLst><p:childTnLst>{beh}</p:childTnLst></p:cTn></p:par>')
            bld[spid] = tipo.get(spid, "sp")
        a, b = ids(), ids()
        clics_xml.append(f'<p:par><p:cTn id="{a}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst><p:childTnLst>'
                         f'<p:par><p:cTn id="{b}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
                         + "".join(items) + "</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>")
    bld_xml = ""
    for spid, t in bld.items():
        if t == "graphicFrame":
            bld_xml += f'<p:bldGraphic spid="{spid}" grpId="0"><p:bldAsOne/></p:bldGraphic>'
        elif t == "sp":
            bld_xml += f'<p:bldP spid="{spid}" grpId="0" animBg="1"/>'
    return ('<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
            '<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
            + "".join(clics_xml)
            + '</p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
            '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
            "</p:childTnLst></p:cTn></p:par></p:tnLst>"
            + (f"<p:bldLst>{bld_xml}</p:bldLst>" if bld_xml else "") + "</p:timing>")


# ================================================================= gráficos
DISCONTINUAS = ("22A", "límite", "14 días", "meta")
CON_MARCA = ("evento", "planes")


def ajustar_grafico(xml: str) -> str:
    xml = re.sub(r'<c:pt idx="\d+"><c:v></c:v></c:pt>', "", xml)
    xml = xml.replace('<c:dispBlanksAs val="span"/>', '<c:dispBlanksAs val="gap"/>')

    def serie(m):
        s = m.group(0)
        nombre = re.search(r"<c:tx>.*?<c:v>(.*?)</c:v>", s, re.S).group(1)
        if any(k in nombre for k in DISCONTINUAS):
            s = s.replace('<a:prstDash val="solid"/>', '<a:prstDash val="dash"/>', 1)
        if any(k in nombre for k in CON_MARCA):
            s = re.sub(r"(<c:spPr>)<a:solidFill>.*?</a:solidFill><a:ln .*?</a:ln>", r"\1<a:ln><a:noFill/></a:ln>", s, count=1, flags=re.S)
            s = re.sub(r'<c:symbol val="\w+"/><c:size val="\d+"/>', '<c:symbol val="circle"/><c:size val="11"/>', s, count=1)
        else:
            s = re.sub(r'<c:symbol val="\w+"/>', '<c:symbol val="none"/>', s, count=1)
        return s

    return re.sub(r"<c:ser>.*?</c:ser>", serie, xml, flags=re.S)


# ================================================================ principal
def main(base: str, salida: str):
    zin = zipfile.ZipFile(base)
    zout = zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED)
    for item in zin.infolist():
        if item.filename.endswith("/"):
            continue  # entradas de carpeta: molestan a servicios en la nube
        data = zin.read(item.filename)
        m = re.fullmatch(r"ppt/slides/slide(\d+)\.xml", item.filename)
        if m:
            n = m.group(1)
            xml = data.decode("utf-8")
            grupos = CFG["anim"].get(n)
            transicion = '<p:transition spd="med"><p:fade/></p:transition>'
            extra = transicion + (timing(xml, grupos) if grupos else "")
            xml = insertar_ecuaciones(xml)
            xml = xml.replace("</p:clrMapOvr>", "</p:clrMapOvr>" + extra, 1)
            data = xml.encode("utf-8")
        elif re.fullmatch(r"ppt/charts/chart\d+\.xml", item.filename):
            data = ajustar_grafico(data.decode("utf-8")).encode("utf-8")
        zout.writestr(item, data)
    zout.close()
    print("PPTX final:", salida)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
