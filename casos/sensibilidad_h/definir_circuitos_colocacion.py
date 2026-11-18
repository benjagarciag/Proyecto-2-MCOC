"""Esquema de circuitos/capas desde IFC; cálculos geométricos, sin solver térmico."""
import json
import os
from pathlib import Path
import sys
from hashlib import sha256

import numpy as np
from shapely import set_precision
from shapely.geometry import LineString, box
from shapely.ops import polygonize, unary_union

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(RAIZ/'desarrollo'))
from mcplan.bim import extraer_fundacion_ifc


def seccion(modelo, z):
    lineas = []
    for v in modelo.vertidas:
        if not v.bbox_min_m[2] < z < v.bbox_max_m[2]:
            continue
        for tri in v.vertices_m[v.triangulos]:
            puntos = []
            for a,b in zip(tri,np.roll(tri,-1,axis=0)):
                if (a[2]-z)*(b[2]-z) < 0:
                    p = a+(b-a)*(z-a[2])/(b[2]-a[2])
                    puntos.append(p[:2])
            if len(puntos) == 2 and np.linalg.norm(puntos[0]-puntos[1]) > 1e-8:
                lineas.append(set_precision(LineString(puntos),1e-6))
    if not lineas:
        raise ValueError(f'Sección vacía a z={z}.')
    poligonos = list(polygonize(unary_union(lineas)))
    if not poligonos:
        raise ValueError(f'No se cerró la sección IFC a z={z}.')
    return unary_union(poligonos)


def volumen_entre(modelo, a, b):
    # Secciones entre alturas de vértices: área cuadrática por tramos;
    # Gauss3 evita evaluar exactamente interfaces coincidentes de sólidos.
    cortes = sorted({a,b,*[float(z) for v in modelo.vertidas for z in np.unique(v.vertices_m[:,2]) if a<z<b]})
    nodos,pesos = np.polynomial.legendre.leggauss(3)
    total = 0.
    for x,y in zip(cortes,cortes[1:]):
        if y-x < 1e-6:
            continue
        for n,w in zip(nodos,pesos):
            z = (x+y)/2+n*(y-x)/2
            total += w*(y-x)/2*seccion(modelo,z).area
    return total


def serpentina(region, paso):
    xmin,ymin,xmax,ymax = region.bounds
    filas = np.arange(ymin+paso/2,ymax, paso)
    puntos = []
    for fila,y in enumerate(filas):
        linea = region.intersection(LineString([(xmin-1,y),(xmax+1,y)]))
        if linea.is_empty:
            continue
        if linea.geom_type != 'LineString':
            raise ValueError('Se esperaba una región convexa con una rama por fila.')
        a,b = list(linea.coords)[0],list(linea.coords)[-1]
        puntos.extend([a,b] if fila%2==0 else [b,a])
    ruta = LineString(puntos)
    assert region.buffer(1e-5).covers(ruta)
    return ruta


def main():
    ruta_config = Path(__file__).with_suffix('.json').with_name('circuitos_colocacion.json')
    cfg = json.loads(ruta_config.read_text(encoding='utf-8'))
    modelo = extraer_fundacion_ifc(RAIZ/'desarrollo/fundacion/fundacion.ifc')
    circuitos = []
    secciones = []
    for nivel in cfg['niveles']:
        z,n = nivel['z_m'],nivel['circuitos']
        pol = seccion(modelo,z)
        interior = pol.buffer(-cfg['margen_horizontal_eje_m'])
        xmin,ymin,xmax,ymax = interior.bounds
        for j in range(n):
            region = interior.intersection(box(xmin+(xmax-xmin)*j/n,ymin-1,xmin+(xmax-xmin)*(j+1)/n,ymax+1)).buffer(-.08)
            linea = serpentina(region,cfg['separacion_ramas_m'])
            circuitos.append(dict(id=f'C{len(circuitos)+1:02}',z_m=z,
                caudal_L_min=cfg['caudal_circuito_L_min'],longitud_esquema_m=linea.length,
                xy_m=[list(p) for p in linea.coords]))
        secciones.append((z,pol,n))
    capas = []
    altura = float(modelo.bbox_max_m[2])
    a = 0.
    while a < altura-1e-6:
        b = min(a+cfg['espesor_max_capa_m'],altura)
        vol = volumen_entre(modelo,a,b)
        inicio = sum(c['duracion_h'] for c in capas)
        capas.append(dict(id=len(capas)+1,z_inferior_m=a,z_superior_m=b,volumen_m3=vol,
            inicio_h=inicio,fin_h=inicio+vol/cfg['caudal_hormigon_total_m3_h'],
            duracion_h=vol/cfg['caudal_hormigon_total_m3_h']))
        a = b
    volumen = sum(c['volumen_m3'] for c in capas)
    assert abs(volumen-modelo.volumen_total_mallas_m3) < .01, (volumen,modelo.volumen_total_mallas_m3)
    q = cfg['caudal_circuito_L_min']/60000
    velocidad = q/(np.pi*cfg['diametro_interior_calculo_m']**2/4)
    resumen = dict(ifc_sha256=modelo.sha256_ifc,config_sha256=sha256(ruta_config.read_bytes()).hexdigest(),
        script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),configuracion=cfg,
        caudal_total_L_min=len(circuitos)*cfg['caudal_circuito_L_min'],
        velocidad_agua_m_s=velocidad,longitud_interior_esquema_m=sum(c['longitud_esquema_m'] for c in circuitos),
        volumen_ifc_m3=modelo.volumen_total_mallas_m3,volumen_capas_m3=volumen,
        duracion_total_h=volumen/cfg['caudal_hormigon_total_m3_h'],circuitos=circuitos,capas=capas)
    salida = RAIZ/'resultados/diseno_circuitos_colocacion'
    salida.mkdir(parents=True,exist_ok=True)
    (salida/'esquema.json').write_text(json.dumps(resumen,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    os.environ.setdefault('MPLCONFIGDIR',str(RAIZ/'.venv/cache/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes = plt.subplots(2,2,figsize=(11,10),layout='constrained')
    colores = plt.get_cmap('tab10')
    for ax,(z,pol,n) in zip(axes.ravel(),secciones):
        x,y = pol.exterior.xy
        ax.fill(x,y,color='#e8ecef')
        ax.plot(x,y,color='#53616d',lw=1)
        for c in circuitos:
            if c['z_m'] != z: continue
            xy = np.array(c['xy_m']);color = colores((int(c['id'][1:])-1)%10)
            ax.plot(xy[:,0],xy[:,1],color=color,lw=1.7,label=f'{c["id"]} · {c["longitud_esquema_m"]:.0f} m')
            ax.scatter(xy[[0,-1],0],xy[[0,-1],1],s=24,color=color)
        ax.axvline(0,color='#8994a0',ls=':',lw=1)
        ax.set(title=f'Nivel z={z:.2f} m · {n} circuito(s)',xlabel='x [m]',ylabel='y [m]',aspect='equal',xlim=(-10,10),ylim=(-10,10))
        ax.legend(fontsize=8,loc='upper right')
        ax.grid(alpha=.12)
    fig.suptitle('Propuesta de circuitos en paralelo sobre secciones del IFC\n'
        '9 circuitos × 18 L/min = 162 L/min · agua ideal a 18 °C',fontsize=14)
    fig.savefig(salida/'circuitos_planta.png',dpi=150)
    plt.close(fig)
    fig,ax = plt.subplots(figsize=(10,6))
    anchos = []
    for c in capas:
        z = (c['z_inferior_m']+c['z_superior_m'])/2
        pol = seccion(modelo,z)
        ancho = pol.bounds[2]-pol.bounds[0]
        ax.add_patch(plt.Rectangle((-ancho/2,c['z_inferior_m']),ancho,c['z_superior_m']-c['z_inferior_m'],
            facecolor=plt.get_cmap('Blues')(.25+.5*c['id']/len(capas)),edgecolor='white'))
        ax.text(10,c['z_inferior_m']+.03,f'Capa {c["id"]:02} · {c["fin_h"]:.2f} h',fontsize=9)
    for nivel in cfg['niveles']:
        ax.axhline(nivel['z_m'],xmin=.02,xmax=.68,color='#b34e34',ls='--',lw=1)
    ax.set(xlim=(-10,15),ylim=(0,4.6),xlabel='x esquemático [m]',ylabel='Altura z [m]',
        title='Colocación continua por capas de hasta 0,40 m\nDos frentes coordinados: 60 m³/h totales · fin ≈10,61 h')
    ax.text(-9.8,4.4,'Escalones esquemáticos; no representan la pendiente exacta del IFC.',fontsize=8)
    fig.tight_layout()
    fig.savefig(salida/'capas_colocacion.png',dpi=150)
    plt.close(fig)
    print(json.dumps({k:resumen[k] for k in ['caudal_total_L_min','velocidad_agua_m_s','longitud_interior_esquema_m','volumen_capas_m3','duracion_total_h']},ensure_ascii=False))
    print('Circuitos:',[(c['id'],round(c['longitud_esquema_m'],1)) for c in circuitos])
    print('Capas:',[(c['id'],round(c['volumen_m3'],2),round(c['duracion_h'],3)) for c in capas])
    print('Sin simulaciones térmicas; IFC no modificado. Salida:',salida)


if __name__ == '__main__':
    main()
