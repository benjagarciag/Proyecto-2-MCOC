"""Etapa 5: eventos exactos, campos persistentes y contactos construidos."""
from dataclasses import replace
from hashlib import sha256

import numpy as np
import pytest

from mcplan.bim import extraer_fundacion_ifc
from mcplan.voxel import voxelizar_fundacion
from mcplan.vertidas_voxel import asignar_vertidas
from mcplan.superficies_voxel import clasificar_caras
from mcplan.construccion import (preparar_construccion,iniciar_construccion,avanzar_construccion,
                                superficies_construidas,mascaras_contactos_activos,
                                proxima_colocacion_s,limitar_paso_por_colocacion_s)
from mcplan.balance_cartesiano import _caras
from mcplan.bordes_termicos import Neumann,preparar_operador,potencia_con_bordes_W
from test_voxel import IFC,caja,modelo


@pytest.fixture(scope='module')
def real():
    f = extraer_fundacion_ifc(IFC)
    a = asignar_vertidas(f,voxelizar_fundacion(f))
    return f,a,preparar_construccion(f,a)


def dos_vertidas(inicios=(0,6),materiales=('M1','M1')):
    v,t = caja()
    f = modelo((v,t),(v+[0,0,1],t))
    vertidas = tuple(replace(p,propiedades={'Inicio_h':hora,'TemperaturaColocacion_C':19-i,
                                          'TipoHormigon':materiales[i]})
                     for i,(p,hora) in enumerate(zip(f.vertidas,inicios)))
    f = replace(f,vertidas=vertidas)
    a = asignar_vertidas(f,voxelizar_fundacion(f,(1,1,1)))
    return f,a,preparar_construccion(f,a)


def test_calendario_y_materiales_proceden_del_ifc(real):
    _,a,p = real
    assert [c.inicio_s for c in p.colocaciones] == [0,21600,43200,64800,86400]
    assert [c.temperatura_C for c in p.colocaciones] == [19,18,18,18,18]
    assert p.ids_sin_voxeles == ()
    assert np.all(p.material[a.voxelizacion.ocupacion]=='M1')
    assert np.all(p.material[~a.voxelizacion.ocupacion]=='')
    assert np.isnan(p.inicio_s[~a.voxelizacion.ocupacion]).all()
    for c in p.colocaciones:
        assert np.all(p.inicio_s[a.vertida_id==c.vertida_id]==c.inicio_s)


def test_estado_previo_no_es_hormigon_a_cero_grados(real):
    e = iniciar_construccion(real[2])
    assert e.tiempo_s==-1 and not e.activos.any() and not e.nuevos.any()
    assert np.isnan(e.temperatura_C).all() and np.isnan(e.edad_s).all()
    s = superficies_construidas(e)
    assert s.caras.exteriores.cantidad==s.caras.internas.cantidad==s.caras.interfaces.cantidad==0
    assert all(not m.any() for m in mascaras_contactos_activos(e))


@pytest.mark.parametrize('numero',[1,2,3,4,5])
def test_inmediatamente_antes_durante_y_despues_de_cada_colocacion(real,numero):
    p = real[2]
    t = p.colocaciones[numero-1].inicio_s
    e = iniciar_construccion(p)
    antes = avanzar_construccion(e,np.nextafter(t,-np.inf))
    assert set(np.unique(antes.ids_activos))-{0}==set(range(1,numero))
    justo = avanzar_construccion(antes,t)
    assert set(np.unique(justo.ids_activos))-{0}==set(range(1,numero+1))
    np.testing.assert_array_equal(justo.nuevos,justo.vertida_id==numero)
    assert np.all(justo.edad_s[justo.nuevos]==0)
    despues = avanzar_construccion(justo,np.nextafter(t,np.inf))
    assert not despues.nuevos.any()
    np.testing.assert_array_equal(justo.activos,despues.activos)


def test_nueva_vertida_no_reinicia_temperaturas_anteriores(real):
    e = iniciar_construccion(real[2])
    for c in e.programa.colocaciones:
        entrada = np.full(e.activos.shape,-999.)
        entrada[e.activos] = 30+e.vertida_id[e.activos]+np.arange(e.activos.sum())*.001
        copia = entrada.copy()
        siguiente = avanzar_construccion(e,c.inicio_s,temperatura_actual_C=entrada)
        np.testing.assert_array_equal(siguiente.temperatura_C[e.activos],entrada[e.activos])
        assert np.all(siguiente.temperatura_C[siguiente.nuevos]==c.temperatura_C)
        assert np.isnan(siguiente.temperatura_C[~siguiente.activos]).all()
        np.testing.assert_array_equal(entrada,copia)
        assert np.isnan(e.temperatura_C[~e.activos]).all()
        e = siguiente


def test_repetir_el_instante_no_reinicializa_y_sin_solver_no_evoluciona(real):
    e = avanzar_construccion(iniciar_construccion(real[2]),21600)
    entrada = e.temperatura_C.copy()
    entrada[e.activos] = 47
    e = avanzar_construccion(e,21600,temperatura_actual_C=entrada)
    assert not e.nuevos.any() and np.all(e.temperatura_C[e.activos]==47)
    posterior = avanzar_construccion(e,23000)
    np.testing.assert_array_equal(e.temperatura_C,posterior.temperatura_C)


@pytest.mark.parametrize('hora',[0,6,12,24,30])
def test_edades_solo_despues_de_colocar(real,hora):
    e = avanzar_construccion(iniciar_construccion(real[2]),hora*3600)
    for c in e.programa.colocaciones:
        mascara = e.vertida_id==c.vertida_id
        if c.inicio_s<=hora*3600:
            np.testing.assert_allclose(e.edad_s[mascara],hora*3600-c.inicio_s)
        else:
            assert np.isnan(e.edad_s[mascara]).all()
    assert np.isnan(e.edad_s[~e.ocupacion_final]).all()


def test_cara_expuesta_se_convierte_en_interfaz_activa():
    _,a,p = dos_vertidas()
    primero = avanzar_construccion(iniciar_construccion(p),0)
    s1 = superficies_construidas(primero)
    assert s1.caras.exteriores.cantidad==6 and s1.caras.interfaces.cantidad==0
    assert s1.expuestas_a_no_colocado.sum()==1
    np.testing.assert_array_equal(s1.caras.exteriores.normal_xyz[s1.expuestas_a_no_colocado],[[0,0,1]])
    assert s1.id_vecino_final[s1.expuestas_a_no_colocado][0]==2
    assert all(not m.any() for m in mascaras_contactos_activos(primero))
    segundo = avanzar_construccion(primero,21600)
    s2 = superficies_construidas(segundo)
    assert s2.caras.exteriores.cantidad==10 and s2.caras.interfaces.cantidad==1
    assert not s2.expuestas_a_no_colocado.any()
    assert s2.caras.contactos_por_par[0].par==(1,2)
    np.testing.assert_array_equal(a.vertida_id,[[[1]],[[2]]])


@pytest.mark.parametrize('hora',[0,6,12,18,24])
def test_fundacion_contactos_solo_entre_celdas_activas(real,hora):
    e = avanzar_construccion(iniciar_construccion(real[2]),hora*3600)
    s = superficies_construidas(e)
    for caras in (s.caras.internas,s.caras.interfaces):
        assert e.activos[tuple(caras.celda_a_zyx.T)].all()
        assert e.activos[tuple(caras.celda_b_zyx.T)].all()
        assert np.isfinite(e.temperatura_C[tuple(caras.celda_b_zyx.T)]).all()
    masks = mascaras_contactos_activos(e)
    assert sum(int(m.sum()) for m in masks)==s.caras.internas.cantidad+s.caras.interfaces.cantidad
    for eje,m in enumerate(masks):
        a,b,_,_ = _caras(eje,3)
        assert (e.activos[a][m]&e.activos[b][m]).all()
    n = int(e.activos.sum())
    assert 6*n==s.caras.exteriores.cantidad+2*(s.caras.internas.cantidad+s.caras.interfaces.cantidad)


def test_ultimo_estado_recupera_exactamente_superficies_etapa4(real):
    e = avanzar_construccion(iniciar_construccion(real[2]),86400)
    previo = clasificar_caras(real[1])
    ahora = superficies_construidas(e)
    np.testing.assert_array_equal(e.activos,e.ocupacion_final)
    assert not ahora.expuestas_a_no_colocado.any()
    for nombre in ('exteriores','internas','interfaces'):
        for campo in ('celda_a_zyx','celda_b_zyx','id_a','id_b','normal_xyz','area_m2'):
            np.testing.assert_array_equal(getattr(getattr(ahora.caras,nombre),campo),
                                          getattr(getattr(previo,nombre),campo))


def test_orden_de_eventos_independiente_de_id_y_colocaciones_simultaneas():
    _,_,p = dos_vertidas(inicios=(6,0),materiales=('Hormigon_tipo_largo','M2'))
    e = avanzar_construccion(iniciar_construccion(p),0)
    assert set(e.ids_activos.ravel())=={0,2}
    assert 'Hormigon_tipo_largo' in p.material
    _,_,p = dos_vertidas(inicios=(0,0))
    e = avanzar_construccion(iniciar_construccion(p),0)
    assert e.activos.all() and e.nuevos.all()
    assert superficies_construidas(e).caras.interfaces.cantidad==1


@pytest.mark.parametrize('hora,paso,esperado',[(0,30000,21600),(5,10000,3600),(6,30000,21600),(24,1000,1000)])
def test_paso_no_cruza_colocaciones(real,hora,paso,esperado):
    e = avanzar_construccion(iniciar_construccion(real[2]),hora*3600)
    assert limitar_paso_por_colocacion_s(e,paso)==esperado
    assert proxima_colocacion_s(e)==(None if hora==24 else (6 if hora<6 else 12)*3600)


def test_compatibilidad_de_enlaces_con_balance_e04():
    _,_,p = dos_vertidas()
    e = avanzar_construccion(iniciar_construccion(p),21600)
    T = np.array([[[40.]],[[18.]]])
    e = avanzar_construccion(e,21600,temperatura_actual_C=T)
    G,bordes,_ = preparar_operador((2,1,1),(1,1,1),(1,1,1),2.,((Neumann(),Neumann()),)*3)
    potencia,_ = potencia_con_bordes_W(T,G,bordes)
    # Mismo intercambio conservativo y mismas formas de enlaces ZYX que E04.
    reconstruida = np.zeros_like(T)
    for eje,mascara in enumerate(mascaras_contactos_activos(e)):
        a,b,_,_ = _caras(eje,3)
        flujo = np.zeros(mascara.shape)
        flujo[mascara] = G[eje]*(T[b][mascara]-T[a][mascara])
        reconstruida[a] += flujo
        reconstruida[b] -= flujo
    np.testing.assert_allclose(reconstruida,potencia)
    assert reconstruida.sum()==0
    # k=2 corresponde SOLO a este ensayo sintético, no al M1 del IFC.


def test_geometria_final_e_ifc_inmutables_y_estado_solo_lectura(real):
    _,a,p = real
    antes = sha256(IFC.read_bytes()).hexdigest()
    ids,ocupados = a.vertida_id.copy(),a.voxelizacion.ocupacion.copy()
    e = avanzar_construccion(iniciar_construccion(p),21600)
    superficies_construidas(e)
    np.testing.assert_array_equal(a.vertida_id,ids)
    np.testing.assert_array_equal(a.voxelizacion.ocupacion,ocupados)
    assert sha256(IFC.read_bytes()).hexdigest()==antes
    for array in (p.material,p.inicio_s,p.temperatura_colocacion_C,e.activos,e.nuevos,e.edad_s,e.temperatura_C):
        assert not array.flags.writeable


@pytest.mark.parametrize('tiempo',[float('nan'),float('inf'),True,'6',-2])
def test_rechaza_tiempo_invalido_o_retroceso(real,tiempo):
    with pytest.raises(ValueError):
        avanzar_construccion(iniciar_construccion(real[2]),tiempo)


@pytest.mark.parametrize('defecto',['forma','nan_activo','infinito_activo','texto','complejo'])
def test_rechaza_temperatura_incompatible(real,defecto):
    e = avanzar_construccion(iniciar_construccion(real[2]),0)
    T = e.temperatura_C.copy()
    if defecto=='forma':T=np.zeros(2)
    elif defecto=='nan_activo':T[e.activos]=np.nan
    elif defecto=='infinito_activo':T[e.activos]=np.inf
    elif defecto=='texto':T=np.full(e.activos.shape,'19')
    else:T=T.astype(complex)
    with pytest.raises(ValueError):
        avanzar_construccion(e,21600,temperatura_actual_C=T)


@pytest.mark.parametrize('paso',[0,-1,float('inf'),True])
def test_rechaza_paso_invalido(real,paso):
    with pytest.raises(ValueError):
        limitar_paso_por_colocacion_s(iniciar_construccion(real[2]),paso)


def test_capa_ausente_se_reporta_sin_repararla(real):
    f = real[0]
    a = asignar_vertidas(f,voxelizar_fundacion(f,(1,1,1)))
    p = preparar_construccion(f,a)
    assert p.ids_sin_voxeles==(2,)
    e = avanzar_construccion(iniciar_construccion(p),21600)
    assert not (e.vertida_id[e.activos]==2).any()


@pytest.mark.parametrize('defecto',['hash','inicio','material','temperatura'])
def test_rechaza_calendario_incompatible(real,defecto):
    f,a,_ = real
    if defecto=='hash':f=replace(f,sha256_ifc='otra_version')
    else:
        valores=dict(f.vertidas[0].propiedades)
        valores[{'inicio':'Inicio_h','material':'TipoHormigon','temperatura':'TemperaturaColocacion_C'}[defecto]]={'inicio':-1,'material':'','temperatura':np.inf}[defecto]
        f=replace(f,vertidas=(replace(f.vertidas[0],propiedades=valores),*f.vertidas[1:]))
    with pytest.raises(ValueError):
        preparar_construccion(f,a)
