"""Lee snapshots congelados, documenta metadatos y grafica; no descarga ni simula."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[2]
cfg = json.loads((REPO/'casos/incertidumbre/parametros.json').read_text(encoding='utf-8'))
manifest = json.loads((REPO/'datos/clima/radiacion/manifiesto.json').read_text(encoding='utf-8'))
variables = ['temperature_2m','wind_speed_10m','shortwave_radiation','direct_radiation',
             'diffuse_radiation','direct_normal_irradiance','dew_point_2m','cloud_cover']
registros, series, archivos = [], [], {}
for c in cfg['historias']:
    m = manifest[c['id']]
    po = REPO / m['snapshot_original']
    pr = REPO / m['snapshot'].replace('\\', '/')
    for p, esperado in [(po,m['original_sha256']),(pr,m['sha256'])]:
        actual = hashlib.sha256(p.read_bytes()).hexdigest()
        assert actual == esperado
        archivos[str(p.relative_to(REPO)).replace('\\','/')] = actual
    d0 = json.loads(po.read_text(encoding='utf-8'))
    d = json.loads(pr.read_text(encoding='utf-8'))
    hr, original = d['respuesta']['hourly'], d0['respuesta']['hourly']
    marcas = np.asarray(hr['time'])
    assert len(marcas) == 696 and (np.diff(marcas) == 3600).all()
    assert list(marcas) == original['time']
    for v in variables:
        assert np.isfinite(np.array(hr[v],float)).all(), v
    for v in variables[:3]:
        np.testing.assert_array_equal(hr[v], original[v])
    inicio = int(datetime.fromisoformat(c['inicio']).timestamp())
    i = hr['time'].index(inicio)
    assert i+674 <= len(marcas)
    s = dict(clima=c['id'], horas=np.arange(673,dtype=float))
    for v in ['temperature_2m','wind_speed_10m','dew_point_2m','cloud_cover']:
        s[v] = np.array(hr[v][i:i+673],float)
    for v in ['shortwave_radiation','diffuse_radiation','direct_normal_irradiance','direct_radiation']:
        s[v] = np.array(hr[v][i+1:i+674],float)
    s['h_c'] = 5.7+3.8*s['wind_speed_10m']*(2/10)**.14
    np.testing.assert_allclose(s['direct_radiation']+s['diffuse_radiation'],s['shortwave_radiation'],atol=.2)
    series.append(s)
    registros.append(dict(clima=c['id'],muestras_archivo=len(marcas),muestras_aire_evaluacion=673,
        inicio_historico=c['inicio'],inicio_utc=datetime.fromtimestamp(inicio,timezone.utc).isoformat(),
        fin_utc=datetime.fromtimestamp(inicio+672*3600,timezone.utc).isoformat(),
        descarga_original_utc=d0['metadata']['descargado_utc'],
        descarga_radiacion_utc=d['metadata']['descargado_utc'],
        primera_marca_archivo_utc=datetime.fromtimestamp(int(marcas[0]),timezone.utc).isoformat(),
        ultima_marca_archivo_utc=datetime.fromtimestamp(int(marcas[-1]),timezone.utc).isoformat(),
        coordenadas_solicitadas=d['metadata']['coordenadas_solicitadas'],
        coordenadas_respuesta={k:d['respuesta'][k] for k in ['latitude','longitude','elevation']},
        faltantes=0,max_diferencia_comunes=0.,original=str(po.relative_to(REPO)),radiacion=str(pr.relative_to(REPO))))

# Comprobar que los archivos climáticos son los mismos citados por las corridas finales.
corridas = [p for p in (REPO/'resultados/cierre_f02').glob('q*/malla*/M*.json')
            if p.name.startswith(('M1_', 'M2_', 'M3_', 'M4_'))]
assert len(corridas) == 72
for p in corridas:
    d = json.loads(p.read_text(encoding='utf-8')); prov = d['procedencia']
    nombre = d['corrida']['clima']; m = manifest[nombre]
    assert prov['clima']['sha256'] == m['sha256']
    assert prov['referencia']['modelo_viento']['clima_sha256'][nombre] == m['original_sha256']

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
colores = ['#0072B2','#D55E00','#009E73']
grupos = [
 ('clima_ambiente', [('temperature_2m','Temperatura del aire','Temperatura [°C]'),
                     ('wind_speed_10m','Viento a 10 m','Velocidad [m/s]'),
                     ('dew_point_2m','Punto de rocío','Temperatura [°C]'),
                     ('cloud_cover','Nubosidad total','Cobertura [%]')]),
 ('clima_radiacion_conveccion',[('shortwave_radiation','Radiación global horizontal (GHI)','Irradiancia [W/m²]'),
                              ('direct_normal_irradiance','Radiación directa normal (DNI)','Irradiancia [W/m²]'),
                              ('diffuse_radiation','Radiación difusa (DHI)','Irradiancia [W/m²]'),
                              ('h_c','Convección calculada','h_c [W/(m² K)]')])]
for nombre, paneles in grupos:
    fig, axs = plt.subplots(2,2,figsize=(8.5,5.8),sharex=True,layout='constrained')
    for ax,(v,titulo,unidad) in zip(axs.flat,paneles):
        for s,color in zip(series,colores):
            if v in ['shortwave_radiation','direct_normal_irradiance','diffuse_radiation','h_c']:
                ax.step(s['horas'],s[v],where='post',lw=.8,color=color,label=s['clima'])
            else:
                ax.plot(s['horas'],s[v],lw=.8,color=color,label=s['clima'])
        ax.axvline(336,color='#555555',ls=':',lw=.8)
        ax.set(title=titulo,ylabel=unidad,xlim=(0,672),xticks=[0,168,336,504,672])
        ax.grid(alpha=.18)
        ax.spines[['top','right']].set_visible(False)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x,p:f'{x:g}'.replace('.',',')))
    for ax in axs[1,:]: ax.set_xlabel('Horas desde el inicio de construcción')
    axs[0,0].legend(ncol=3,fontsize=7,frameon=False)
    fig.savefig(BASE/'Imagenes'/f'{nombre}.png',dpi=220,facecolor='white')
    plt.close(fig)

salida = BASE/'datos';salida.mkdir(exist_ok=True)
for rel in ['casos/incertidumbre/parametros.json','datos/clima/radiacion/manifiesto.json',
            'entregas/F02/cierre_revision_final/CONFIGURACION_FINAL_REVISADA.json',
            'datos/hidratacion/source_terms.txt','datos/hidratacion/manifiesto.json',
            'desarrollo/fundacion/fundacion.ifc']:
    archivos[rel] = hashlib.sha256((REPO/rel).read_bytes()).hexdigest()
for p in sorted((REPO/'datos/clima/forecasts').glob('*.json')):
    archivos[str(p.relative_to(REPO)).replace('\\','/')] = hashlib.sha256(p.read_bytes()).hexdigest()
(salida/'clima_trazabilidad.json').write_text(json.dumps(dict(registros=registros,sha256=archivos,
    corridas_climaticas_contrastadas=len(corridas),alcance='Lectura, contraste de procedencia y figuras; sin nuevas descargas ni solver.'),
    ensure_ascii=False,indent=2),encoding='utf-8')
with (salida/'clima_series_utilizadas.csv').open('w',newline='',encoding='utf-8') as f:
    nombres=['clima','hora_relativa','temperature_2m','wind_speed_10m','dew_point_2m','cloud_cover',
             'shortwave_radiation','direct_normal_irradiance','diffuse_radiation','h_c']
    w = csv.DictWriter(f,fieldnames=nombres);w.writeheader()
    for s in series:
        for j in range(673):
            w.writerow(dict(clima=s['clima'],hora_relativa=j,**{v:float(s[v][j]) for v in nombres[2:]}))
print('Verificados seis snapshots, ausencia de faltantes y procedencia climática de',len(corridas),'corridas.')
for r in registros:print(r['clima'],r['descarga_original_utc'],r['descarga_radiacion_utc'])
