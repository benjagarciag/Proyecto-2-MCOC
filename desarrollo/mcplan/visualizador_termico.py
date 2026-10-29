"""Cálculo y verificaciones compartidas por el visualizador térmico y pytest."""
from dataclasses import dataclass
from math import ceil

import numpy as np

from .difusion_1d import Parametros1D, resolver_1d
from .difusion_2d import Parametros2D
from .difusion_3d import Parametros3D
from .bordes_termicos import Dirichlet, Neumann, Robin
from .difusion_bordes import resolver_2d_bordes, resolver_3d_bordes
from .barra_fuente_3d import CASOS_BARRA, calcular_barra


CASOS = {'seno_1d': 'Solución exacta 1D', 'seno_2d': 'Seno 2D', 'seno_3d': 'Seno 3D',
         'adiabatico': 'Conservación adiabática', 'fuente': 'Fuente uniforme',
         'neumann': 'Flujo Neumann', 'robin': 'Convección Robin'}
CASOS.update(CASOS_BARRA)


def predeterminados(caso):
    c = dict(dimension=int(caso[-2]) if caso.startswith('seno') else 2,
                Lx=1., Ly=1., Lz=1., nx=30 if caso != 'seno_3d' else 16,
                ny=30 if caso != 'seno_3d' else 16, nz=16,
                k=2., rho=2400., cp=900., alpha_1d=1e-4,
                tf_s=1500. if caso == 'seno_1d' else 86400., dt_s=None,
                T0=30. if caso == 'robin' else 20., A=50. if caso.startswith('seno') else 10.,
                q=600. if caso == 'fuente' else 10., h=10., Tamb=20., tolerancia_K=.15)
    c.update(Qmax=5001.,duracion_h=12.,beta=-5.,fuente_x=0.,fuente_y=0.,fuente_z=0.,
             tam_x=1.,tam_y=1.,tam_z=1.,punto_x=0.,punto_y=0.,punto_z=0.)
    if caso in CASOS_BARRA:
        c.update(dimension=3,Lx=3.,Ly=3.,Lz=6.,nx=15,ny=15,nz=31,
                 tf_s=48*3600.,dt_s=300.,T0=20.,A=0.)
    return c


@dataclass
class Vista:
    caso: str
    config: dict
    tiempos: np.ndarray
    campos: np.ndarray
    coordenadas: tuple
    dt: float
    dt_limite: float
    media_exacta: np.ndarray | None
    campo_exacto: np.ndarray | None
    energia: np.ndarray | None
    balance: np.ndarray | None
    potencia_inicial: float | None
    potencia_esperada: float | None
    extras: dict | None = None


def calcular(caso, c):
    """No escribe archivos; solo calcula cuando lo solicita el usuario."""
    if caso not in CASOS:
        raise ValueError('Caso desconocido.')
    if caso in CASOS_BARRA:
        return Vista(**calcular_barra(caso,c))
    dim = c['dimension']
    if caso.startswith('seno') and dim != int(caso[-2]):
        raise ValueError('La dimensión debe coincidir con el caso sinusoidal.')
    if not caso.startswith('seno') and dim not in (2, 3):
        raise ValueError('Para bordes/fuentes elegir 2D o 3D.')
    if not np.isfinite(c['tolerancia_K']) or c['tolerancia_K'] <= 0:
        raise ValueError('La tolerancia de temperatura debe ser positiva.')
    if c['tf_s'] <= 0:
        raise ValueError('El tiempo final debe ser positivo para reproducir una evolución.')
    if dim == 1:
        p = Parametros1D(longitud_m=c['Lx'], n_intervalos=c['nx'], difusividad_m2_s=c['alpha_1d'],
                         tiempo_final_s=c['tf_s'], paso_tiempo_s=c['dt_s'],
                         temperatura_izquierda_C=c['T0'], temperatura_derecha_C=c['T0'],
                         perfil_inicial='seno', amplitud_inicial_K=c['A'])
        if p.n_pasos > 200000 or (p.n_pasos+1)*(p.n_intervalos+1) > 15000000:
            raise ValueError('Caso demasiado grande para esta ventana; reducir malla o duración.')
        r = resolver_1d(p)
        ids = np.unique(np.rint(np.linspace(0, len(r.tiempos_s)-1, min(81, len(r.tiempos_s)))).astype(int))
        t, campos = r.tiempos_s[ids], r.temperatura_C[ids]
        exacta = c['T0']+c['A']*np.sin(np.pi*r.x_m[None, :]/c['Lx'])*np.exp(-p.alpha_m2_s*(np.pi/c['Lx'])**2*t[:, None])
        return Vista(caso, dict(c), t, campos, (r.x_m,), p.dt_s, p.dt_max_s,
                     exacta.mean(axis=1), exacta, None, None, None, None)
    valores = dict(longitud_x_m=c['Lx'], longitud_y_m=c['Ly'], celdas_x=c['nx'], celdas_y=c['ny'],
                   conductividad_W_mK=c['k'], densidad_kg_m3=c['rho'], calor_especifico_J_kgK=c['cp'],
                   tiempo_final_s=c['tf_s'], paso_tiempo_s=c['dt_s'])
    if dim == 2:
        p, solver = Parametros2D(**valores), resolver_2d_bordes
    else:
        p, solver = Parametros3D(longitud_z_m=c['Lz'], celdas_z=c['nz'], **valores), resolver_3d_bordes
    longueurs = (c['Lx'], c['Ly'], c['Lz'])[:dim]
    cellules = (c['nx'], c['ny'], c['nz'])[:dim]
    # Evitar bloquear la ventana por un cambio accidental excesivo.
    from .difusion_bordes import paso_maximo_bordes_s
    bordes = {f'{e}_{lado}': Neumann(0) for e in 'xyz'[:dim] for lado in ('min', 'max')}
    inicial = c['T0']
    if caso.startswith('seno'):
        bordes = {cara: Dirichlet(c['T0']) for cara in bordes}
        def inicial(*xyz):
            return c['T0']+c['A']*np.prod([np.sin(np.pi*x/L) for x, L in zip(xyz, longueurs)], axis=0)
    elif caso == 'adiabatico':
        def inicial(*xyz):
            return c['T0']+c['A']*np.prod([np.cos(np.pi*x/L) for x, L in zip(xyz, longueurs)], axis=0)
    elif caso == 'neumann':
        bordes['x_min'] = Neumann(c['q'])
    elif caso == 'robin':
        bordes['x_max'] = Robin(c['h'], c['Tamb'])
    limite = paso_maximo_bordes_s(p, bordes)
    paso = c['dt_s'] if c['dt_s'] is not None else .9*limite
    n = ceil(c['tf_s']/paso) if paso > 0 else 200001
    if np.prod(cellules)*min(n+1, 81) > 15000000 or n > 200000 or np.prod(cellules)*n > 200000000:
        raise ValueError('Caso demasiado grande para esta ventana; reducir malla o duración.')
    q = c['q'] if caso == 'fuente' else 0
    r = solver(p, bordes, inicial, n_guardados=81, fuente_W_m3=q)
    coords = r.coordenadas_m
    t, campos = r.tiempos_s, r.temperatura_C
    V = np.prod(longueurs)  # Espesor uniforme 1 m en 2D.
    capacidad_total = c['rho']*c['cp']*V
    energia = r.energia_relativa_J-r.energia_relativa_J[0]
    exterior = np.r_[0., np.cumsum(r.dt_s*r.potencia_exterior_W[:-1])]
    balance = exterior + q*V*r.tiempos_historia_s
    exacta, media_exacta = None, None
    if caso.startswith('seno'):
        grillas = np.meshgrid(*reversed(coords), indexing='ij')
        forma = np.prod([np.sin(np.pi*x/L) for x, L in zip(reversed(grillas), longueurs)], axis=0)
        tasa = p.alpha_m2_s*np.pi**2*sum(1/L**2 for L in longueurs)
        exacta = c['T0']+c['A']*np.exp(-tasa*t).reshape((-1,)+(1,)*dim)*forma
        media_exacta = exacta.reshape(len(t), -1).mean(axis=1)
    elif caso == 'fuente':
        media_exacta = c['T0']+q*t/(c['rho']*c['cp'])
        exacta = np.broadcast_to(media_exacta.reshape((-1,)+(1,)*dim), campos.shape)
    elif caso == 'adiabatico':
        media_exacta = np.full_like(t, campos[0].mean())
    elif caso == 'neumann':
        area = c['Ly']*(c['Lz'] if dim == 3 else 1)
        media_exacta = c['T0']+c['q']*area*t/capacidad_total
        balance = c['q']*area*r.tiempos_historia_s
    potencia_esperada = None
    if caso == 'robin':
        area = c['Ly']*(c['Lz'] if dim == 3 else 1)
        dx = c['Lx']/c['nx']
        potencia_esperada = 0 if c['h'] == 0 else area*(c['Tamb']-c['T0'])/(dx/(2*c['k'])+1/c['h'])
    return Vista(caso, dict(c), t, campos, coords, r.dt_s, r.dt_max_s, media_exacta, exacta,
                 energia, balance, float(r.potencia_exterior_W[0]), potencia_esperada)


def verificar(v):
    """Mismas comprobaciones para la ventana y pytest; fallar conserva la vista."""
    mensajes, fallos = [], []
    def comprobar(condicion, texto):
        mensajes.append(('OK: ' if condicion else 'FALLO: ')+texto)
        if not condicion:
            fallos.append(texto)
    if v.campo_exacto is not None:
        error = float(np.max(abs(v.campos-v.campo_exacto)))
        comprobar(error <= v.config['tolerancia_K'],
                   f'Error máximo en los cuadros guardados = {error:.6g} K; tolerancia = {v.config["tolerancia_K"]:g} K.')
    if v.energia is not None:
        residuo = float(np.max(abs(v.energia-v.balance)))
        escala = max(1., float(np.max(abs(v.balance))),
                     v.config['rho']*v.config['cp']*np.prod([v.config[k] for k in ('Lx','Ly','Lz')[:v.config['dimension']]])*max(1.,abs(v.config['T0'])))
        comprobar(residuo <= 1e-10*escala, f'Residuo de balance energético = {residuo:.6g} J (tolerancia relativa 1e-10).')
    if v.caso == 'robin':
        comprobar(np.isclose(v.potencia_inicial, v.potencia_esperada, rtol=1e-10, atol=1e-9),
                   f'Potencia inicial = {v.potencia_inicial:.6g} W; referencia independiente = {v.potencia_esperada:.6g} W.')
        minimo, maximo = sorted((v.config['T0'], v.config['Tamb']))
        comprobar(v.campos.min() >= minimo-1e-8 and v.campos.max() <= maximo+1e-8,
                   'Temperaturas entre el estado inicial y el ambiente.')
    if v.caso in ('adiabatico', 'neumann') and v.media_exacta is not None:
        error = np.max(abs(v.campos.reshape(len(v.tiempos),-1).mean(axis=1)-v.media_exacta))
        comprobar(error <= v.config['tolerancia_K'], f'Error máximo de temperatura media = {error:.6g} K.')
    if v.extras is not None:
        e = v.extras
        if e['adiabatico']:
            residuo = np.max(abs(v.energia-e['energia_generada']))
            comprobar(residuo <= 1e-10*escala,
                       f'Adiabático: cambio de energía igual al calor generado, residuo={residuo:.6g} J.')
        mensajes += ['INFO: '+nota for nota in e['notas']]
        mensajes.append('INFO: Se verifica el balance; no se afirma una solución exacta transiente de esta fuente localizada.')
    return not fallos, mensajes
