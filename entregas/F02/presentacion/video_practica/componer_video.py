"""Compone el video final de práctica a partir del video mudo exportado por PowerPoint.

- Detecta el inicio real de cada lámina (cambio de imagen cerca del tiempo previsto).
- Agrega una franja bajo la lámina con: quién habla, el texto del guion y «▶ CLIC n».
- Coloca las voces de Luis y Matías en sus tiempos (PowerPoint no exporta sonidos de transición).
Uso: python componer_video.py <plan.json> <video_mudo.mp4> <video_final.mp4>
"""
import json, os, subprocess, sys
from pathlib import Path
import numpy as np

plan_p, mudo, final = sys.argv[1:4]
plan = json.load(open(plan_p, encoding="utf-8"))
INTRO, FPS = 9.0, 20
RETRASO_VOZ = 0.3     # la voz empieza un poco después del inicio del fundido
ANIM = 0.5            # las animaciones se ven ~0,5 s después del tiempo de clic del plan
FRANJA = 150          # alto de la franja inferior (px), video 1280×720 → 1280×870

crudo = subprocess.run(["ffmpeg", "-v", "error", "-i", mudo, "-vf", f"fps={FPS},scale=64:36,format=gray",
                        "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
f = np.frombuffer(crudo, np.uint8).reshape(-1, 36, 64).astype(float)
dif = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
duracion = len(f) / FPS

inicios, previsto = [], INTRO
for lam in plan:
    a, b = int((previsto - 1.0) * FPS), int((previsto + 1.5) * FPS)
    v = np.where(dif[a:b] > 1.5)[0]
    real = (a + v[0] + 1) / FPS if len(v) else previsto
    inicios.append(real); previsto = real + lam["total"]
    print(lam["id"], "inicio", round(real, 2))

# ---------------------------------------------------------------- subtítulos ASS
def ts(t):
    t = max(t, 0); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

ass = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1280", f"PlayResY: {720 + FRANJA}", "WrapStyle: 0", "",
       "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: Ben,Segoe UI,27,&H005CD6FF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,40,40,762,1",
       "Style: Voz,Segoe UI,27,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,40,40,762,1",
       "Style: Quien,Segoe UI Semibold,22,&H00A8B36A,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,1,0,1,0,0,7,40,40,730,1",
       "Style: Clic,Segoe UI Semibold,24,&H00FFFFFF,&H000000FF,&H00286EE6,&H00286EE6,1,0,0,0,100,100,0,0,3,6,0,9,40,40,728,1",
       "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
ass.append(f"Dialogue: 0,{ts(0)},{ts(INTRO)},Quien,,0,0,0,,INTRODUCCIÓN")
for k, (lam, t0) in enumerate(zip(plan, inicios)):
    t1 = inicios[k + 1] if k + 1 < len(inicios) else duracion
    ben = lam["quien"] == "Benjamín"
    etiqueta = "TU TURNO · BENJAMÍN (sin voz: dilo tú)" if ben else f"HABLA {lam['quien'].upper()}"
    ass.append(f"Dialogue: 0,{ts(t0)},{ts(t1)},Quien,,0,0,0,,{lam['id']} · {etiqueta}")
    subs = lam["subtitulos"]
    for j, s in enumerate(subs):
        fin_s = t0 + RETRASO_VOZ + (subs[j + 1]["desde"] if j + 1 < len(subs) else lam["total"])
        texto = s["texto"].replace("\n", " ")
        ass.append(f"Dialogue: 0,{ts(t0 + RETRASO_VOZ + s['desde'] - 0.15)},{ts(min(fin_s - 0.05, t1))},{'Ben' if ben else 'Voz'},,0,0,0,,{texto}")
    for n, c in enumerate(lam["clics"], 1):
        ini = t0 + c + ANIM - 0.3
        ass.append(f"Dialogue: 1,{ts(ini)},{ts(ini + 2.2)},Clic,,0,0,0,,▶ CLIC {n}")

trabajo = Path(final).resolve().parent
sub = trabajo / "_subtitulos.ass"
sub.write_text("\n".join(ass) + "\n", encoding="utf-8-sig")

# ---------------------------------------------------------------- audio + video
entradas, filtros, n = ["-i", mudo], [], 0
for lam, t in zip(plan, inicios):
    if lam["audio"]:
        n += 1; entradas += ["-i", lam["audio"]]
        ms = int((t + RETRASO_VOZ) * 1000)
        filtros.append(f"[{n}:a]adelay={ms}|{ms}[a{n}]")
filtros.append("".join(f"[a{k}]" for k in range(1, n + 1)) + f"amix=inputs={n}:normalize=0[a]")
filtros.append(f"[0:v]pad=1280:{720 + FRANJA}:0:0:color=0x0E171E,subtitles=_subtitulos.ass[v]")
cwd = os.getcwd(); os.chdir(trabajo)
try:
    subprocess.run(["ffmpeg", "-y", "-v", "error", *entradas, "-filter_complex", ";".join(filtros),
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
                    str(Path(final).resolve())], check=True)
finally:
    os.chdir(cwd); sub.unlink(missing_ok=True)
print("listo:", final)
