"""Convierte la elevación adiabática por edad en una fuente térmica volumétrica.

Recibe curvas configuradas por material y el ProgramaConstruccion de Etapa 5.
Devuelve elevación en K, generación W/m³ y energía por intervalo en J/m³ o J
por voxel. Las edades de cada vertida son independientes; inactivos generan cero.
Reutiliza edades de construccion.py y validación de fuentes_volumetricas.py.
Modelo de la guía §§23–25: theta=theta_inf*(1-exp(-a/tau)), q=rho*cp*dtheta/da.
Los parámetros M1 del caso son didácticos; aquí no hay conducción ni cinética por T.
"""
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

import numpy as np

from .construccion import ProgramaConstruccion, EstadoConstruccion, _real, _solo_lectura
from .fuentes_volumetricas import preparar_fuente_W_m3


def _edades(valores):
    datos = np.asarray(valores)
    if datos.dtype.kind not in 'fiu' or not np.isfinite(datos).all():
        raise ValueError('Las edades deben ser números reales finitos en segundos.')
    return np.array(datos,dtype=float,copy=True)


@dataclass(frozen=True)
class CurvaAdiabatica:
    """Curva exponencial con theta_infinito_K [K], tau_s [s], rho [kg/m³] y cp [J/(kg K)].
    """
    theta_infinito_K: float
    tau_s: float
    densidad_kg_m3: float
    calor_especifico_J_kgK: float

    def __post_init__(self):
        for nombre,valor in vars(self).items():
            valor = _real(nombre,valor)
            if valor<0 or (nombre!='theta_infinito_K' and valor==0):
                raise ValueError('Theta debe ser >=0; tau, densidad y cp deben ser >0.')
            object.__setattr__(self,nombre,valor)
        if not all(np.isfinite(v) for v in (self.capacidad_volumetrica_J_m3K,
                                            self.energia_final_J_m3,self.q_inicial_W_m3)):
            raise ValueError('Los parámetros exceden el rango numérico representable.')

    @property
    def capacidad_volumetrica_J_m3K(self):
        return self.densidad_kg_m3*self.calor_especifico_J_kgK

    @property
    def energia_final_J_m3(self):
        return self.capacidad_volumetrica_J_m3K*self.theta_infinito_K

    @property
    def q_inicial_W_m3(self):
        return self.energia_final_J_m3/self.tau_s

    def elevacion_K(self, edad_s):
        """Elevación acumulada; cero antes de colocar, no temperatura absoluta.

        Entrada: edad escalar o array [s]; salida: elevación theta_ad [K].
        Usa -expm1(-a/tau) para precisión cerca del origen y cero si la edad es negativa.
        """
        a = np.maximum(_edades(edad_s),0.)
        with np.errstate(over='ignore',under='ignore'):
            return self.theta_infinito_K*(-np.expm1(-a/self.tau_s))

    def valor(self, edad_s):
        """Fuente instantánea W/m³. Misma interfaz que PulsoTermico.valor.

        Entrada: edad desde colocación [s]; salida q [W/m³].
        q=rho*cp*theta_inf/tau*exp(-a/tau), cero antes de colocar.
        En a=0 q es finita aunque la energía acumulada sea todavía cero.
        """
        edad = _edades(edad_s)
        with np.errstate(over='ignore',under='ignore'):
            q = self.q_inicial_W_m3*np.exp(-np.maximum(edad,0.)/self.tau_s)
        return np.where(edad>=0,q,0.)

    def acumulada_J_m3(self, edad_s):
        """Integral desde la colocación; interfaz del pulso temporal existente.

        Entrada: edad [s]; salida H=rho*cp*theta_ad [J/m³].
        Es energía por volumen, no una potencia ni temperatura absoluta.
        """
        return self.capacidad_volumetrica_J_m3K*self.elevacion_K(edad_s)

    def energia_intervalo_J_m3(self, edad_inicio_s, edad_fin_s):
        """Integral exacta, sin restar acumuladas casi iguales en edades avanzadas.

        Las edades negativas se recortan a cero: nunca se genera antes de colocar.
        Se admiten intervalos nulos y entradas escalares o arrays compatibles.

        Entradas: edades inicial/final [s], escalares o arrays compatibles.
        Salida: energía integrada [J/m³], sin dependencia del tamaño de voxel.
        Se recorta la edad negativa a cero y se usa expm1 para conservar incrementos tardíos pequeños.
        """
        inicio,fin = np.broadcast_arrays(_edades(edad_inicio_s),_edades(edad_fin_s))
        if (fin<inicio).any():
            raise ValueError('El intervalo de edad no puede retroceder.')
        a,b = np.maximum(inicio,0.),np.maximum(fin,0.)
        with np.errstate(over='ignore',under='ignore'):
            return self.energia_final_J_m3*np.exp(-a/self.tau_s)*(-np.expm1(-(b-a)/self.tau_s))


@dataclass(frozen=True)
class HidratacionVertidas:
    """Relaciona un programa de construcción con curvas por material; no confunde material e ID.
    """
    programa: ProgramaConstruccion
    curvas_por_material: Mapping[str,CurvaAdiabatica]

    def __post_init__(self):
        if not isinstance(self.programa,ProgramaConstruccion):
            raise ValueError('Se requiere el ProgramaConstruccion de Etapa 5.')
        try:
            curvas = dict(self.curvas_por_material)
        except (ValueError,TypeError) as error:
            raise ValueError('Declarar una curva por etiqueta de material.') from error
        materiales = {c.material for c in self.programa.colocaciones}
        if set(curvas)!=materiales or not all(isinstance(c,CurvaAdiabatica) for c in curvas.values()):
            raise ValueError('Declarar exactamente una CurvaAdiabatica por material del programa.')
        object.__setattr__(self,'curvas_por_material',MappingProxyType(curvas))

    def _validar_campo(self,campo):
        g = self.programa.asignacion_final.voxelizacion.grilla
        # Reutiliza forma ZYX, finitud, no negatividad y unidades del módulo E04.
        return _solo_lectura(preparar_fuente_W_m3(campo,g.forma_zyx,g.centros_xyz_m[::-1]))

    def fuente_W_m3(self, estado):
        """Cero fuera de celdas activas; usa sus edades independientes de Etapa 5.

        Recibe EstadoConstruccion del mismo programa; devuelve fuente ZYX [W/m³].
        La edad ya está calculada en avanzar_construccion. Solo se evalúan celdas
        activas: NaN de no colocados nunca entra en la curva ni genera calor.
        """
        if not isinstance(estado,EstadoConstruccion) or estado.programa is not self.programa:
            raise ValueError('El estado debe pertenecer al mismo programa de construcción.')
        campo = np.zeros(estado.activos.shape)
        for material,curva in self.curvas_por_material.items():
            mascara = estado.activos&(self.programa.material==material)
            # Se evalúa SOLO la edad construida; las celdas futuras no aportan fuente.
            campo[mascara] = curva.valor(estado.edad_s[mascara])
        return self._validar_campo(campo)

    def energia_volumetrica_intervalo_J_m3(self, tiempo_inicio_s, tiempo_fin_s):
        """Integra por ID y horario real, incluso si el intervalo cruza colocaciones.

        No usa la máscara del inicio del paso: perdería vertidas recién colocadas.
        No incluye energía sensible de T_colocación ni modifica el campo T.

        Entradas: extremos globales del intervalo [s]. Devuelve campo ZYX [J/m³].
        Resta el inicio de CADA vertida antes de integrar, incluso si aparece durante el paso;
        la máscara del comienzo por sí sola excluiría incorrectamente ese hormigón nuevo.
        """
        inicio,fin = _real('tiempo_inicio_s',tiempo_inicio_s),_real('tiempo_fin_s',tiempo_fin_s)
        if fin<inicio:
            raise ValueError('El intervalo temporal no puede retroceder.')
        ids = self.programa.asignacion_final.vertida_id
        campo = np.zeros(ids.shape)
        for c in self.programa.colocaciones:
            curva = self.curvas_por_material[c.material]
            # Restar este inicio permite integrar un paso que cruza la colocación.
            campo[ids==c.vertida_id] = curva.energia_intervalo_J_m3(inicio-c.inicio_s,fin-c.inicio_s)
        return _solo_lectura(campo)

    def energia_intervalo_J(self, tiempo_inicio_s, tiempo_fin_s):
        """Energía por voxel = integral(q''' da)*V_voxel [J]. Sumar para el total.

        Entradas: tiempos globales [s]; salida: energía por celda [J].
        E_i=V_i*integral(q_i dt). Sumar el campo da la energía total;
        no incluye energía sensible de colocación ni modifica temperaturas.
        """
        V = self.programa.asignacion_final.voxelizacion.grilla.volumen_celda_m3
        return _solo_lectura(self.energia_volumetrica_intervalo_J_m3(tiempo_inicio_s,tiempo_fin_s)*V)

    def fuente_media_W_m3(self, tiempo_inicio_s, tiempo_fin_s):
        """Promedio exacto del intervalo; dt debe ser positivo. No es q(t_inicio).

        Entradas: tiempos globales [s] de duración positiva; salida fuente media ZYX [W/m³].
        Multiplicarla por dt*V recupera exactamente la energía de hidratación del intervalo.
        """
        inicio,fin = _real('tiempo_inicio_s',tiempo_inicio_s),_real('tiempo_fin_s',tiempo_fin_s)
        if fin<=inicio:
            raise ValueError('La fuente media necesita un intervalo de duración positiva.')
        campo = self.energia_volumetrica_intervalo_J_m3(inicio,fin)/(fin-inicio)
        return self._validar_campo(campo)
