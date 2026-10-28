"""Generación prescrita no negativa, constante en el tiempo, en W/m³.

No es un modelo de cinética de hidratación. La fuente es independiente de T.
Las cajas se integran por intersección con cada celda, no por máscara de centros.
"""
from numbers import Real

import numpy as np

from .difusion_2d import Parametros2D, _real_finito
from .difusion_3d import Parametros3D


def preparar_fuente_W_m3(fuente, forma, centros_por_eje):
    """Escalar, campo [y,x]/[z,y,x] o función espacial f(X,Y[,Z]).

    Devuelve una copia con un promedio volumétrico por celda. Para una función
    arbitraria se muestrea en centros; para cajas usar fuente_desde_config,
    que integra exactamente la fracción activa de cada celda.
    """
    if callable(fuente):
        grillas = np.meshgrid(*centros_por_eje, indexing='ij')
        fuente = fuente(*reversed(grillas))
    if isinstance(fuente, Real) and not isinstance(fuente, bool):
        _real_finito('fuente_W_m3', fuente)
        campo = np.full(forma, fuente, dtype=float)
    else:
        dato = np.asarray(fuente)
        if dato.dtype.kind not in 'fiu':
            raise ValueError('fuente_W_m3 debe contener números reales, no booleanos ni texto.')
        campo = np.array(dato, dtype=float, copy=True)
    if campo.shape != forma or not np.isfinite(campo).all() or (campo < 0).any():
        raise ValueError('fuente_W_m3 requiere valores finitos >= 0, uno por celda o un escalar.')
    return campo


def fuente_desde_config(config, parametros):
    """JSON: tipo uniforme o caja, valor_W_m3; caja incluye limites_m.

    En 2D la caja ocupa todo el espesor. El campo devuelve W/m³ promediados
    sobre cada celda: q_i = q_activo * volumen_intersección/volumen_celda.
    Por tanto sum(q_i*V) = q_activo*volumen_caja, con cualquier refinamiento.
    """
    if isinstance(parametros, Parametros2D):
        ejes = 'xy'
    elif isinstance(parametros, Parametros3D):
        ejes = 'xyz'
    else:
        raise ValueError('Usar Parametros2D o Parametros3D.')
    tipo = config.get('tipo')
    esperadas = {'tipo', 'valor_W_m3'} | ({'limites_m'} if tipo == 'caja' else set())
    if tipo not in ('uniforme', 'caja') or set(config) != esperadas:
        raise ValueError('Fuente: tipo uniforme/caja, valor_W_m3 y limites_m solo para caja.')
    valor = config['valor_W_m3']
    _real_finito('valor_W_m3', valor)
    if valor < 0:
        raise ValueError('valor_W_m3 debe ser >= 0 (generación).')
    if tipo == 'uniforme':
        return float(valor)
    limites = config['limites_m']
    if not isinstance(limites, dict) or set(limites) != set(ejes):
        raise ValueError(f'limites_m debe declarar exactamente los ejes {ejes}.')
    fracciones = []
    for eje in reversed(ejes):
        L, n = getattr(parametros, f'longitud_{eje}_m'), getattr(parametros, f'celdas_{eje}')
        par = limites[eje]
        if not isinstance(par, (list, tuple)) or len(par) != 2:
            raise ValueError('Cada intervalo debe ser [mínimo, máximo] en metros.')
        minimo, maximo = par
        _real_finito('mínimo', minimo)
        _real_finito('máximo', maximo)
        if not 0 <= minimo < maximo <= L:
            raise ValueError(f'Intervalo {eje} fuera del dominio o sin volumen.')
        d = L/n
        izquierda = np.arange(n)*d
        fracciones.append(np.maximum(0., np.minimum(izquierda+d, maximo)-np.maximum(izquierda, minimo))/d)
    forma = tuple(len(f) for f in fracciones)
    campo = np.full(forma, float(valor))
    for i, fraccion in enumerate(fracciones):
        forma_eje = [1]*len(forma)
        forma_eje[i] = len(fraccion)
        campo *= fraccion.reshape(forma_eje)
    return campo
