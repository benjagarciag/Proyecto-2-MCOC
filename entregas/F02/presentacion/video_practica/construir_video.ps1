# Construye el video de práctica desde una copia ya temporizada por temporizar_xml.py.
# Copia temporizada: animaciones originales a tiempos del guion y voz de Luis/Matías
# como sonido de transición (suena al reproducir la copia; el video la recibe aparte).
# Subtítulos, hablante y marcas de clic se agregan en una franja bajo la lámina (componer_video.py).
param([string]$plan, [string]$pptxOrigen, [string]$pptxSalida, [string]$mp4)
$ErrorActionPreference = "Stop"
$DATOS = Get-Content -Raw -Encoding UTF8 $plan | ConvertFrom-Json
function RGB($r, $g, $b) { return $r + 256 * $g + 65536 * $b }
$TRANS = 0.5

Copy-Item $pptxOrigen $pptxSalida -Force
$app = New-Object -ComObject PowerPoint.Application
try {
  $pr = $app.Presentations.Open($pptxSalida, $false, $false, $false)
  while ($pr.Slides.Count -gt 8) { $pr.Slides.Item($pr.Slides.Count).Delete() }
  $W = $pr.PageSetup.SlideWidth; $H = $pr.PageSetup.SlideHeight

  for ($i = 1; $i -le 8; $i++) {
    $s = $pr.Slides.Item($i); $p = $DATOS[$i - 1]; $seq = $s.TimeLine.MainSequence
    $ben = ($p.quien -eq "Benjamín")
    # --- la temporización ya viene en el XML (temporizar_xml.py): no deben quedar clics
    $clic = 0; for ($e = 1; $e -le $seq.Count; $e++) { if ($seq.Item($e).Timing.TriggerType -eq 1) { $clic++ } }
    if ($clic -ne 0) { throw "S$i conserva $clic efectos por clic: ejecutar antes temporizar_xml.py" }
    $fin = [double]$p.clics[$p.clics.Count - 1] - $TRANS + 3
    # --- transición, voz y avance automático
    $tr = $s.SlideShowTransition
    $tr.Duration = $TRANS
    if ($p.audio) { $tr.SoundEffect.ImportFromFile($p.audio) }
    $tr.AdvanceOnTime = -1; $tr.AdvanceTime = [Math]::Max([double]$p.total - $TRANS, $fin + 0.5)
    "S$i $($p.quien): efectos $($seq.Count), lámina $([Math]::Round([double]$p.total,1)) s"
  }

  # --- portada explicativa
  $c = $pr.Slides.Add(1, 12)
  $c.FollowMasterBackground = 0; $c.Background.Fill.ForeColor.RGB = RGB 19 32 42
  $t1 = $c.Shapes.AddTextbox(1, 60, 120, $W - 120, 60); $t1.TextFrame.TextRange.Text = "Video de práctica · Defensa F02 · Grupo 6"
  $t1.TextFrame.TextRange.Font.Size = 32; $t1.TextFrame.TextRange.Font.Bold = -1; $t1.TextFrame.TextRange.Font.Color.RGB = RGB 255 255 255
  $t2 = $c.Shapes.AddTextbox(1, 60, 200, $W - 120, 200)
  $t2.TextFrame.TextRange.Text = "S1–S3: tu turno, Benjamín. Sin voz: di el texto amarillo de la franja inferior, a ritmo lento.`rS4–S5: Luis (voz sintética chilena). S6–S8: Matías (voz sintética mexicana).`rLa marca naranja «▶ CLIC n» aparece en el momento exacto de avanzar cada animación.`rTiempos estimados a ritmo lento; no reemplaza el ensayo del grupo."
  $t2.TextFrame.TextRange.Font.Size = 20; $t2.TextFrame.TextRange.Font.Color.RGB = RGB 220 225 228
  $t2.TextFrame.TextRange.ParagraphFormat.SpaceAfter = 10
  $c.SlideShowTransition.AdvanceOnTime = -1; $c.SlideShowTransition.AdvanceTime = 9

  $pr.Save()
  $pr.CreateVideo($mp4, $true, 5, 720, 30, 90)
  do { Start-Sleep -Seconds 5; $st = $pr.CreateVideoStatus } while ($st -eq 1 -or $st -eq 2)
  "estado video: $st (3 = listo)"
  $pr.Close()
} finally { $app.Quit() }
