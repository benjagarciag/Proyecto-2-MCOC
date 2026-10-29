"""Definición S25 y máximos temporales; referencias sintéticas independientes."""
import numpy as np
import pytest
from mcplan.difusion_3d import Parametros3D
from mcplan.bordes_termicos import Dirichlet,Neumann
from mcplan.criterios_termicos import preparar_s25,minimo_s25,resumir_criterios


def test_s25_no_es_rango_de_temperaturas_de_los_centros():
    p=Parametros3D(longitud_x_m=3,longitud_y_m=3,longitud_z_m=6,celdas_x=15,celdas_y=15,celdas_z=31)
    bordes={f'{e}_{lado}':Dirichlet(20) for e in 'xyz' for lado in ('min','max')}
    T=np.full(p.forma_zyx,80.)
    prep=preparar_s25(p,bordes)
    minimo,maximo=minimo_s25(T,prep,incluir_maximo=True)
    # En la esquina de S25 la interpolación tensorial de tres caras a20
    # y el centro a80 produce este producto independiente.
    esperado=20+60*np.prod([.025/(d/2) for d in p.pasos_espaciales_m])
    assert minimo==pytest.approx(esperado)
    assert maximo==80
    assert np.ptp(T)==0 and maximo-minimo>20
    assert not prep[2]


def test_adiabatico_uniforme_tiene_delta_cero():
    p=Parametros3D(celdas_x=4,celdas_y=4,celdas_z=4)
    bordes={f'{e}_{lado}':Neumann(0) for e in 'xyz' for lado in ('min','max')}
    s25,tmax=minimo_s25(np.full(p.forma_zyx,60.),preparar_s25(p,bordes),incluir_maximo=True)
    assert s25==60 and tmax-s25==0


def test_maximos_de_T_y_delta_pueden_ocurrir_en_instantes_distintos():
    r=resumir_criterios(np.array([0,3600,7200]),np.array([60,71,69]),np.array([10,60,20]),False)
    assert r['Tmax_C']==71 and r['tiempo_Tmax_h']==1
    assert r['DeltaTmax_K']==50 and r['tiempo_DeltaTmax_h']==0
    assert not r['cumple_Tmax'] and not r['cumple_Delta']
    assert not r['horizonte_14dias']
