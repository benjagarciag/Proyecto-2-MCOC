"""Prepara audios y tiempos del video de práctica a partir de GUION_ORAL_F02.md.

Luis y Matías: voces neuronales (edge-tts, servicio en línea de Microsoft).
Benjamín: sin voz; duración estimada a 110 palabras/min para que practique.
Uso: python preparar_audio.py <carpeta_trabajo>   (requiere edge-tts y ffmpeg)
"""
import asyncio, json, re, subprocess, sys, wave
from pathlib import Path

import edge_tts

AQUI = Path(__file__).resolve().parent
GUION = AQUI.parents[1] / "GUION_ORAL_F02.md"
TRAB = Path(sys.argv[1]); TRAB.mkdir(parents=True, exist_ok=True)
VOCES = {"Luis": "es-CL-LorenzoNeural", "Matías": "es-MX-JorgeNeural"}
RITMO = "-12%"          # algo más lento que la voz por defecto
PPM_BENJAMIN = 110
PAUSA = 0.7             # s de silencio entre frases (momento del clic)
LEAD = 0.25             # el clic ocurre un poco antes de la frase siguiente
INICIO = 0.6            # silencio al entrar en la lámina


def leer_guion():
    g = GUION.read_text(encoding="utf-8")
    laminas = []
    for m in re.finditer(r"## (S\d) — (\w+): (.*?) \(.*?\)\n.*?<!-- habla:\1 -->\n(.*?)<!-- fin:\1 -->", g, re.S):
        k, quien, tit, cuerpo = m.groups()
        segs, actual = [], []
        for linea in cuerpo.splitlines():
            if linea.startswith(">") and "CLIC" in linea:
                segs.append(" ".join(actual).strip()); actual = []
            elif linea.strip():
                actual.append(linea.strip())
        segs.append(" ".join(actual).strip())
        laminas.append({"id": k, "quien": quien, "titulo": tit, "segmentos": segs})
    assert len(laminas) == 8, len(laminas)
    return laminas


def para_voz(texto):
    # lectura natural de cifras y símbolos
    t = texto.replace("P_f", "P sub f").replace("S25", "S veinticinco").replace("m³/h", "metros cúbicos por hora")
    t = re.sub(r"(\d),(\d)", r"\1 coma \2", t)
    return t


def duracion(wav):
    with wave.open(str(wav)) as w:
        return w.getnframes() / w.getframerate()


async def tts(texto, voz, destino):
    mp3 = destino.with_suffix(".mp3")
    await edge_tts.Communicate(para_voz(texto), voz, rate=RITMO).save(str(mp3))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3), "-ar", "44100", "-ac", "1", str(destino)], check=True)


def silencio(seg, destino):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                    "-t", f"{seg:.3f}", str(destino)], check=True)


async def main():
    plan = []
    for lam in leer_guion():
        k, quien = lam["id"], lam["quien"]
        t, clics, partes, subt = INICIO, [], [], []
        for i, texto in enumerate(lam["segmentos"]):
            if i > 0:
                clics.append(max(t - LEAD, 0.2))
            if not texto:
                continue
            if quien in VOCES:
                wav = TRAB / f"{k}_{i}.wav"
                await tts(texto, VOCES[quien], wav)
                d = duracion(wav); partes.append(wav)
            else:
                d = len(texto.split()) / PPM_BENJAMIN * 60
            subt.append({"desde": t, "hasta": t + d, "texto": texto, "tras_clic": i})
            t += d + PAUSA
        total = t + 0.6
        audio = None
        if partes:  # pista de la lámina: silencios + frases en sus tiempos exactos
            lista, cursor = [], 0.0
            for s, wav in zip([s for s in subt], partes):
                if s["desde"] > cursor:
                    sil = TRAB / f"{k}_sil{len(lista)}.wav"; silencio(s["desde"] - cursor, sil); lista.append(sil)
                lista.append(wav); cursor = s["hasta"]
            sil = TRAB / f"{k}_fin.wav"; silencio(total - cursor, sil); lista.append(sil)
            txt = TRAB / f"{k}_lista.txt"
            txt.write_text("".join(f"file '{p.as_posix()}'\n" for p in lista), encoding="utf-8")
            audio = TRAB / f"{k}.wav"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(txt),
                            "-ar", "44100", "-ac", "1", str(audio)], check=True)
            total = duracion(audio)
        plan.append({"id": k, "quien": quien, "titulo": lam["titulo"], "clics": clics,
                     "subtitulos": subt, "total": total, "audio": str(audio) if audio else None})
        print(k, quien, f"{total:.1f} s", "clics", [round(c, 1) for c in clics])
    (TRAB / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    print("total", round(sum(p["total"] for p in plan), 1), "s")

asyncio.run(main())
