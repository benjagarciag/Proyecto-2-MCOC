"""Guía §§23–25: unidades, integración exacta y edades por colocación."""
from dataclasses import replace
from hashlib import sha256

import numpy as np
import pytest

from mcplan.bim import extraer_fundacion_ifc
from mcplan.voxel import voxelizar_fundacion
from mcplan.vertidas_voxel import asignar_vertidas
from mcplan.construccion import preparar_construccion,iniciar_construccion,avanzar_construccion
from mcplan.hidratacion import CurvaAdiabatica,HidratacionVertidas
from mcplan.difusion_3d import Parametros3D
from mcplan.bordes_termicos import Neumann
from mcplan.fuente_temporal_3d import resolver_fuente_temporal_3d
from test_construccion import dos_vertidas
from test_voxel import IFC


@pytest.fixture
def curva():
    return CurvaAdiabatica(45.,30*3600.,2400.,900.)


@pytest.fixture(scope='module')
def real():
    f=extraer_fundacion_ifc(IFC)
    a=asignar_vertidas(f,voxelizar_fundacion(f))
    p=preparar_construccion(f,a)
    h=HidratacionVertidas(p,{'M1':CurvaAdiabatica(45.,108000.,2400.,900.)})
    return f,a,p,h


def test_unidades_y_valores_de_referencia_guia(curva):
    assert curva.capacidad_volumetrica_J_m3K==2160000
    assert curva.energia_final_J_m3==97200000  # J/m³, no W/m³.
    assert curva.q_inicial_W_m3==900           # 97.2 MJ/m³ / 108000 s.
    assert curva.elevacion_K(0)==0
    assert curva.valor(0)==900
    assert curva.elevacion_K(108000)==pytest.approx(45*(1-1/np.e))
    assert curva.valor(108000)==pytest.approx(900/np.e)


def test_antes_de_colocar_cero_y_limite_de_energia(curva):
    edades=np.array([-86400,-1,0,108000,10800000])
    theta=curva.elevacion_K(edades)
    q=curva.valor(edades)
    assert np.all(theta[:3]==0) and np.all(q[:2]==0)
    assert np.all(np.diff(theta)>=0) and theta[-1]==pytest.approx(45)
    assert curva.acumulada_J_m3(edades)[-1]==pytest.approx(97.2e6)
    assert np.all(np.diff(q[2:])<=0)


@pytest.mark.parametrize('edad_h',[1,30,90])
def test_derivada_de_elevacion_equivale_a_fuente(curva,edad_h):
    t=edad_h*3600
    derivada=(curva.elevacion_K(t+1)-curva.elevacion_K(t-1))/2
    assert curva.valor(t)==pytest.approx(2400*900*derivada,rel=2e-9)


def test_integral_analitica_contra_cuadratura_independiente(curva):
    tiempos=np.linspace(3600,35*3600,20001)
    integral=np.trapezoid(curva.valor(tiempos),tiempos)
    assert curva.energia_intervalo_J_m3(tiempos[0],tiempos[-1])==pytest.approx(integral,rel=1e-9)


def test_intervalos_antes_de_colocar_nulos_y_cruzados(curva):
    assert curva.energia_intervalo_J_m3(-100,-1)==0
    assert curva.energia_intervalo_J_m3(0,0)==0
    assert curva.energia_intervalo_J_m3(-100,3600)==pytest.approx(curva.acumulada_J_m3(3600))
    np.testing.assert_allclose(curva.energia_intervalo_J_m3([-1,0,3600],[0,3600,7200]),
                               [0,curva.acumulada_J_m3(3600),curva.acumulada_J_m3(7200)-curva.acumulada_J_m3(3600)])


def test_integral_estable_en_cola_donde_acumuladas_redondean_igual(curva):
    a=50*curva.tau_s
    assert curva.acumulada_J_m3(a+1)-curva.acumulada_J_m3(a)==0
    exacta=curva.energia_intervalo_J_m3(a,a+1)
    assert exacta>0
    assert exacta==pytest.approx(97200000*np.exp(-50)*(-np.expm1(-1/108000)),rel=1e-14,abs=0)


@pytest.mark.parametrize('campo',['densidad_kg_m3','calor_especifico_J_kgK','theta_infinito_K'])
def test_escala_de_energia_y_fuente(curva,campo):
    doble=replace(curva,**{campo:2*getattr(curva,campo)})
    assert doble.valor(1800)==pytest.approx(2*curva.valor(1800))
    assert doble.acumulada_J_m3(3600)==pytest.approx(2*curva.acumulada_J_m3(3600))


def test_tau_controla_ritmo_no_energia_final_y_theta_cero(curva):
    lenta=replace(curva,tau_s=2*curva.tau_s)
    assert lenta.valor(0)==450 and lenta.energia_final_J_m3==curva.energia_final_J_m3
    cero=replace(curva,theta_infinito_K=0)
    assert cero.valor(0)==cero.energia_intervalo_J_m3(0,86400)==cero.elevacion_K(86400)==0


@pytest.mark.parametrize('hora',[0,6,12,18,24])
def test_cada_vertida_genera_solo_desde_su_activacion(real,hora):
    _,a,p,h=real
    t=hora*3600
    antes=avanzar_construccion(iniciar_construccion(p),np.nextafter(t,-np.inf))
    e=avanzar_construccion(antes,t)
    q=h.fuente_W_m3(e)
    nueva=int(hora/6)+1
    assert np.all(h.fuente_W_m3(antes)[a.vertida_id==nueva]==0)
    assert np.all(q[a.vertida_id==nueva]==900)
    assert np.all(q[~e.activos]==0) and np.isfinite(q).all()
    for c in p.colocaciones:
        esperado=900*np.exp(-(t-c.inicio_s)/108000) if t>=c.inicio_s else 0
        np.testing.assert_allclose(q[a.vertida_id==c.vertida_id],esperado)


def test_edades_independientes_y_temperaturas_no_modificadas(real):
    _,a,p,h=real
    e=avanzar_construccion(iniciar_construccion(p),86400)
    T=e.temperatura_C.copy()
    q=h.fuente_W_m3(e)
    valores=[]
    for c,edad_h in zip(p.colocaciones,[24,18,12,6,0]):
        mascara=a.vertida_id==c.vertida_id
        assert np.all(e.edad_s[mascara]==edad_h*3600)
        valores.append(q[mascara][0])
    assert np.all(np.diff(valores)>0)  # Mismo material, edades diferentes.
    np.testing.assert_array_equal(T,e.temperatura_C)


def test_intervalo_que_cruza_colocacion_no_usa_mascara_del_inicio(real):
    _,a,p,h=real
    E=h.energia_intervalo_J(5*3600,7*3600)
    V=a.voxelizacion.grilla.volumen_celda_m3
    # Vertida 02 genera una hora, no dos ni cero.
    esperado=97200000*(1-np.exp(-1/30))*V
    np.testing.assert_allclose(E[a.vertida_id==2],esperado)
    assert np.all(E[a.vertida_id>2]==0)
    assert np.all(h.energia_intervalo_J(5*3600,6*3600)[a.vertida_id==2]==0)
    assert np.all(h.fuente_W_m3(avanzar_construccion(iniciar_construccion(p),5*3600))[a.vertida_id==2]==0)


def test_energia_aditiva_independiente_del_numero_de_intervalos(real):
    h=real[3]
    tiempos=np.array([-1,0,3600,5*3600,6*3600,6*3600+1,12*3600,24*3600,60*3600])
    suma=sum((h.energia_intervalo_J(a,b) for a,b in zip(tiempos,tiempos[1:])))
    np.testing.assert_allclose(suma,h.energia_intervalo_J(tiempos[0],tiempos[-1]),rtol=3e-15)
    np.testing.assert_array_equal(h.energia_intervalo_J(0,0),0)


def test_fuente_media_multiplicada_por_dt_y_volumen_recupera_julios(real):
    a,h=real[1],real[3]
    E=h.energia_intervalo_J(0,86400)
    media=h.fuente_media_W_m3(0,86400)
    np.testing.assert_allclose(media*86400*a.voxelizacion.grilla.volumen_celda_m3,E,rtol=2e-16)
    assert np.all(media[a.vertida_id==5]==0)  # Se coloca justo al final: duración cero.


@pytest.mark.parametrize('paso',[1.,.5,.25])
def test_independencia_del_volumen_de_voxel_en_geometria_exacta(paso,curva):
    f,_,_=dos_vertidas()
    a=asignar_vertidas(f,voxelizar_fundacion(f,(paso,)*3))
    p=preparar_construccion(f,a)
    h=HidratacionVertidas(p,{'M1':curva})
    E=h.energia_intervalo_J(0,12*3600)
    esperado=curva.acumulada_J_m3(12*3600)+curva.acumulada_J_m3(6*3600)  # Dos cubos de 1 m³.
    assert E.sum()==pytest.approx(esperado,rel=2e-15)
    # Incremento adiabático por celda independiente de V.
    m=a.vertida_id==1
    incremento=E[m]/(2400*900*a.voxelizacion.grilla.volumen_celda_m3)
    np.testing.assert_allclose(incremento,curva.elevacion_K(12*3600))


def test_curvas_por_material_y_no_por_numero_de_vertida(curva):
    _,_,p=dos_vertidas(materiales=('M1','M2'))
    h=HidratacionVertidas(p,{'M1':curva,'M2':replace(curva,theta_infinito_K=20)})
    e=avanzar_construccion(iniciar_construccion(p),21600)
    assert h.fuente_W_m3(e)[e.vertida_id==2][0]==400


def test_verificacion_adiabatica_con_solver_3d_existente(curva):
    # Ensayo de ocho celdas, no simulación de la fundación.
    p=Parametros3D(celdas_x=2,celdas_y=2,celdas_z=2,tiempo_final_s=86400,paso_tiempo_s=3600)
    b={k:Neumann() for k in ('x_min','x_max','y_min','y_max','z_min','z_max')}
    r=resolver_fuente_temporal_3d(p,b,curva,temperatura_inicial_C=19,n_guardados=5)
    np.testing.assert_allclose(r.temperatura_C[:,0,0,0],19+curva.elevacion_K(r.tiempos_s),rtol=2e-15)
    np.testing.assert_allclose(r.energia_relativa_J-r.energia_relativa_J[0],r.calor_generado_J,atol=5e-8)


def test_preserva_ifc_estados_y_mapa_de_curvas(real,curva):
    antes=sha256(IFC.read_bytes()).hexdigest()
    _,a,p,h=real
    ids=a.vertida_id.copy()
    e=avanzar_construccion(iniciar_construccion(p),21600)
    T=e.temperatura_C.copy()
    q=h.fuente_W_m3(e)
    assert not q.flags.writeable and not h.energia_intervalo_J(0,86400).flags.writeable
    np.testing.assert_array_equal(ids,a.vertida_id)
    np.testing.assert_array_equal(T,e.temperatura_C)
    assert sha256(IFC.read_bytes()).hexdigest()==antes
    mapa={'M1':curva}
    m=HidratacionVertidas(p,mapa)
    mapa.clear()
    assert set(m.curvas_por_material)=={'M1'}


@pytest.mark.parametrize('campo,valor',[
    ('theta_infinito_K',-1),('theta_infinito_K',float('nan')),
    ('tau_s',0),('tau_s',-1),('tau_s',True),('tau_s','30'),
    ('densidad_kg_m3',0),('densidad_kg_m3',-2400),('densidad_kg_m3',float('inf')),
    ('calor_especifico_J_kgK',0),('calor_especifico_J_kgK',float('nan'))])
def test_rechaza_parametros_invalidos(curva,campo,valor):
    with pytest.raises(ValueError):replace(curva,**{campo:valor})


@pytest.mark.parametrize('edad',[float('nan'),float('inf'),True,'6',1j])
def test_rechaza_edades_no_reales_o_no_finitas(curva,edad):
    with pytest.raises(ValueError):curva.valor(edad)


@pytest.mark.parametrize('a,b',[(1,0),(float('nan'),1),(0,float('inf'))])
def test_rechaza_intervalos_invalidos(real,curva,a,b):
    with pytest.raises(ValueError):curva.energia_intervalo_J_m3(a,b)
    with pytest.raises(ValueError):real[3].energia_intervalo_J(a,b)


def test_rechaza_promedio_nulo_y_material_o_estado_incompatible(real,curva):
    with pytest.raises(ValueError):real[3].fuente_media_W_m3(0,0)
    with pytest.raises(ValueError):HidratacionVertidas(real[2],{'M2':curva})
    with pytest.raises(ValueError):HidratacionVertidas(real[2],{'M1':1.})
    otro=dos_vertidas()[2]
    with pytest.raises(ValueError):real[3].fuente_W_m3(iniciar_construccion(otro))
