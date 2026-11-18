"""Desarrolla F02 §§1–3.3 desde evidencia existente, sin solver ni cambios al PPT."""
from pathlib import Path
from datetime import datetime, timedelta
from hashlib import sha256
import csv
import json
import os

RAIZ = Path(__file__).resolve().parents[2]
os.environ.setdefault('MPLCONFIGDIR', str(RAIZ/'.venv/cache/matplotlib'))
DESTINO = RAIZ/'entregas/F02/revision_puntos_1_3'


def leer(p):
    return json.loads(p.read_text(encoding='utf-8'))


def tabla(nombre, filas):
    with (DESTINO/nombre).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)


def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    esquema_p = RAIZ/'resultados/diseno_circuitos_colocacion/esquema.json'
    esquema = leer(esquema_p)
    config_p = RAIZ/'.venv/cache/f02_sensibilidad_h/casos/incertidumbre/parametros.json'
    config = leer(config_p)
    t0 = datetime.fromisoformat(config['inicio'])
    assert t0.isoformat() == '2026-11-19T10:00:00-03:00'
    capas = []
    for q in [60, 55, 50, 45]:
        anterior = 0
        for c in esquema['capas']:
            inicio, fin = c['inicio_h']*60/q, c['fin_h']*60/q
            assert abs(inicio-anterior) < 1e-9
            assert abs((fin-inicio)*q-c['volumen_m3']) < 1e-8
            capas.append(dict(plan_m3_h=q, capa=c['id'], z_inferior_m=c['z_inferior_m'],
                z_superior_m=c['z_superior_m'], volumen_m3=c['volumen_m3'],
                inicio_h=inicio, duracion_h=fin-inicio, fin_h=fin, espera_previa_h=0,
                inicio_local=(t0+timedelta(hours=inicio)).isoformat(),
                fin_local=(t0+timedelta(hours=fin)).isoformat(),
                activacion_solver_h=inicio, temperatura_C=12))
            anterior = fin
        assert abs(anterior-esquema['duracion_total_h']*60/q) < 1e-9
    tabla('CRONOGRAMA_44_CAPAS.csv', capas)
    entradas = [esquema_p, config_p]
    filas, historias = [], {}
    for p in sorted((RAIZ/'resultados/sensibilidad_radiacion/ambas/malla_0.4_paso300').glob('M*.json')):
        if p.name == 'matriz.json':
            continue
        d = leer(p)
        r, h = d['corrida'], d['historia']
        assert r['horizonte_h'] == 672
        assert abs(h[-1]['tiempo_h']-672) < 1e-8
        base = r['base_336h']
        fallos = [x for x in h if x['DeltaT_K'] > 20 or x['Tmax_C'] > 70]
        fallo600 = any(x['tiempo_h'] <= 600 for x in fallos)
        assert fallo600 and r['excede_20'] and not r['excede_70']
        filas.append(dict(curva=r['curva'], clima=r['clima'], peso=r['peso'],
            Tmax_336_C=base['Tmax']['valor'], Delta_336_K=base['DeltaTmax']['valor'],
            I_T_336=int(base['excede_70']), I_Delta_336=int(base['excede_20']),
            I_F_336=int(base['excede_70'] or base['excede_20']),
            Tmax_672_C=r['Tmax']['valor'], Delta_672_K=r['DeltaTmax']['valor'],
            t_pico_Delta_h=r['DeltaTmax']['tiempo_h'],
            I_T_672=int(r['excede_70']), I_Delta_672=int(r['excede_20']),
            I_F_672=int(r['excede_70'] or r['excede_20']),
            excedencia_muestreada_antes_600=fallo600,
            primera_excedencia_registrada_h=fallos[0]['tiempo_h'],
            alerta_cola=bool(r['pico_no_resuelto']),
            archivo=str(p.relative_to(RAIZ))))
        historias[(r['curva'], r['clima'])] = h
        entradas.append(p)
    assert len(filas) == 24 and abs(sum(r['peso'] for r in filas)-1) < 1e-12
    assert not any(r['I_F_336'] for r in filas)
    tabla('METRICAS_24_PARES_336_672.csv', filas)
    resumen = dict(t0=t0.isoformat(), zona='America/Santiago; UTC−03:00 en el inicio adoptado',
        cronograma_filas=len(capas), pares=len(filas), horizonte_comun_h=672,
        Tmax_336_C=max(r['Tmax_336_C'] for r in filas),
        Delta_336_K=max(r['Delta_336_K'] for r in filas),
        Tmax_672_C=max(r['Tmax_672_C'] for r in filas),
        Delta_672_K=max(r['Delta_672_K'] for r in filas),
        P_T_336=sum(r['peso']*r['I_T_336'] for r in filas),
        P_Delta_336=sum(r['peso']*r['I_Delta_336'] for r in filas),
        P_union_336=sum(r['peso']*r['I_F_336'] for r in filas),
        P_T_672=sum(r['peso']*r['I_T_672'] for r in filas),
        P_Delta_672=sum(r['peso']*r['I_Delta_672'] for r in filas),
        P_union_672=sum(r['peso']*r['I_F_672'] for r in filas),
        alertas_cola=sum(r['alerta_cola'] for r in filas),
        todos_exceden_antes_600=all(r['excedencia_muestreada_antes_600'] for r in filas),
        estado='Cumple catálogo336h; incumple catálogo672h. Máximos definitivos no acreditados.',
        nota600='Solo prueba de excedencia en muestras guardadas; no máximos exactos a600h.',
        entradas=[dict(ruta=str(p.relative_to(RAIZ)),sha256=sha256(p.read_bytes()).hexdigest()) for p in entradas])
    (DESTINO/'RESUMEN.json').write_text(json.dumps(resumen,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 1, figsize=(11,7), sharex=True, layout='constrained')
    for clave,color in [(('M4_SS','ERA5-2024'),'#743e99'),(('M1_22A','ERA5-2024'),'#b54830')]:
        h=historias[clave]
        x=[r['tiempo_h'] for r in h]
        etiqueta=' × '.join(clave)
        ax[0].plot(x,[r['Tmax_C'] for r in h],color=color,label=etiqueta+' Tmax')
        ax[0].plot(x,[r['Tmin_S25_C'] for r in h],color=color,ls='--',alpha=.7,label=etiqueta+' Tmin,S25')
        ax[1].plot(x,[r['DeltaT_K'] for r in h],color=color,label=etiqueta)
    for a in ax:
        a.axvline(336,color='black',ls=':',label='14 días' if a is ax[1] else None)
        a.axvspan(360,360+esquema['capas'][-1]['inicio_h'],color='#d2a12a',alpha=.2,
            label='Retiros nominales última manta' if a is ax[1] else None)
        a.grid(alpha=.2)
        a.legend(fontsize=8,loc='upper left')
    ax[0].set(ylabel='Temperatura [°C]',title='Mismo plan con radiación: ventana obligatoria y seguimiento extendido')
    ax[1].axhline(20,color='black',ls='--')
    ax[1].set(xlabel='Tiempo desde t₀ [h]',ylabel='ΔT simultáneo [K]',xlim=(0,672))
    fig.savefig(DESTINO/'HORIZONTES_336_672.png',dpi=170)
    plt.close(fig)
    paquete=[]
    actuales=[RAIZ/'entregas/F02/MODELO_VIGENTE.json',
        RAIZ/'entregas/F02/CONFIGURACION_BENJAMIN.json',
        RAIZ/'entregas/F02/GUION_ORAL_F02.md',
        RAIZ/'entregas/F02/BRIEF_DIAPOSITIVAS_F02.md',
        RAIZ/'entregas/F02/presentacion/F02_Grupo6_radiacion_actualizada.pptx',
        RAIZ/'entregas/F02/presentacion/F02_Grupo6_radiacion_actualizada.pdf']
    actuales+=list((RAIZ/'resultados/familia_radiacion_336h').rglob('*.json'))
    actuales+=entradas
    for p in sorted(set(actuales)):
        assert p.is_file()
        paquete.append(dict(ruta=str(p.relative_to(RAIZ)),bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest()))
    (DESTINO/'INVENTARIO_OFFLINE.json').write_text(json.dumps(dict(
        alcance='Inventario local comprobado; no copia a equipo de exposición ni SHA final de entrega.',
        archivos=paquete),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in resumen.items() if k!='entradas'},ensure_ascii=False,indent=2))
    print('Archivos offline comprobados:',len(paquete))


if __name__=='__main__':
    main()
