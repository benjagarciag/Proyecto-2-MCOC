> Actualización19/11: se eliminó el PPT temporizado para dejar un único PowerPoint final por solicitud del usuario. El MP4 se conserva como práctica histórica. Las referencias siguientes describen su generación anterior.

# Video de práctica F02

- `F02_video_practica.mp4` (≈5:52, 1280×870): las ocho láminas principales de
  `F02_Grupo6_Pre_entrega.pptx` con sus animaciones reales, avanzando solas al ritmo del
  guion vigente (`../../GUION_ORAL_F02.md`). Franja inferior: quién habla, texto y «▶ CLIC n».
  - S1–S3, Benjamín: sin voz, texto en amarillo (≈110 palabras/min) para practicar encima.
  - S4–S5, Luis: voz neuronal es-CL-LorenzoNeural. S6–S8, Matías: es-MX-JorgeNeural.
    Son voces sintéticas de Microsoft (servicio en línea edge-tts), no las de los compañeros.
- `F02_practica_temporizada.pptx`: misma copia temporizada; en modo presentación avanza
  sola y reproduce las voces como sonido de transición. No reemplaza al PPTX de defensa.

El 19/11 se corrigieron ids de figura duplicados en `F02_Grupo6_Pre_entrega.pptx`
(S4 tabla↔flecha, S7 tabla↔primer bloque del cronograma, y figuras animadas con el
mismo id que el número de página en S2/S3/S6/S7). Ahora S1–S8 tienen 2-3-3-3-3-3-3-2
clics, como el guion, y cada animación actúa sobre su figura.

## Regenerar

1. `preparar_audio.py <trabajo>`: lee el guion, genera voces (edge-tts + ffmpeg) y `plan.json`.
2. `temporizar_xml.py <trabajo>\plan.json ..\F02_Grupo6_Pre_entrega.pptx <trabajo>\temporizado_xml.pptx`
   (convierte los clics en tiempos absolutos en el XML; no se usa COM para esto porque
   cambiar disparadores por COM separa los efectos «con el anterior» de su grupo).
3. `construir_video.ps1 -plan <trabajo>\plan.json -pptxOrigen <trabajo>\temporizado_xml.pptx -pptxSalida F02_practica_temporizada.pptx -mp4 <trabajo>\video_mudo.mp4`
   (PowerPoint vía COM: deja S1–S8, portada, transiciones con voz y exporta video mudo).
4. `componer_video.py <trabajo>\plan.json <trabajo>\video_mudo.mp4 F02_video_practica.mp4`
   (detecta el inicio de cada lámina, agrega franja y voces).

Tiempos a ritmo lento estimados; no es un ensayo cronometrado del grupo.
