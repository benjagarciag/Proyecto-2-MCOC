"""Práctica E05: cambiar las tablas de parámetros y ejecutar con pytest -s.

No genera archivos ni figuras. Las referencias son soluciones analíticas,
balances globales o límites físicos independientes de las actualizaciones.
Las propiedades pequeñas en 2D/3D son sintéticas para ejecutar rápido.
"""
from dataclasses import replace

import numpy as np
import pytest

from mcplan.difusion_1d import Parametros1D, resolver_1d
from mcplan.difusion_2d import Parametros2D, Dirichlet2D, resolver_2d
from mcplan.difusion_3d import Parametros3D, Dirichlet3D, resolver_3d
from mcplan.bordes_termicos import Dirichlet, Neumann, Robin
from mcplan.difusion_bordes import resolver_2d_bordes, resolver_3d_bordes
from mcplan.difusion_2d import paso_maximo_s
from mcplan.difusion_3d import paso_maximo_3d_s


@pytest.mark.parametrize('n,L,alpha,A,base', [
    (40, 1., 1e-4, 50., 20.),
    (80, 1., 1e-4, 50., 20.),
    (40, 2., 2e-4, -30., 40.),
])
def test_e05_1d(n, L, alpha, A, base):
    p = Parametros1D(longitud_m=L, n_intervalos=n, difusividad_m2_s=alpha,
                     tiempo_final_s=1500, temperatura_izquierda_C=base,
                     temperatura_derecha_C=base, amplitud_inicial_K=A,
                     perfil_inicial='seno')
    r = resolver_1d(p)
    # Referencia escrita directamente, sin usar solucion_exacta del paquete.
    exacta = base+A*np.sin(np.pi*r.x_m/L)*np.exp(-alpha*(np.pi/L)**2*1500)
    error = np.max(abs(r.temperatura_C[-1]-exacta))
    assert error/abs(A) < .002
    print(f'\n1D: n={n}, L={L:g} m, alpha={alpha:g}, A={A:g} K, '
          f'dx={p.dx_m:g} m, dt={p.dt_s:.6g} s, error final={error:.6g} K')


@pytest.mark.parametrize('nx,ny,Lx,Ly,k,A', [
    (12, 10, 1., 1.7, 1., 10.),
    (24, 20, 1., 1.7, 1., 10.),
    (24, 16, 2., 1., 2., -8.),
])
def test_e05_2d(nx, ny, Lx, Ly, k, A):
    p = Parametros2D(longitud_x_m=Lx, longitud_y_m=Ly, celdas_x=nx, celdas_y=ny,
                     conductividad_W_mK=k, densidad_kg_m3=2, calor_especifico_J_kgK=5,
                     tiempo_final_s=.2)
    def inicial(X, Y):
        return 20+A*np.sin(np.pi*X/Lx)*np.sin(np.pi*Y/Ly)
    r = resolver_2d(p, Dirichlet2D(), inicial)
    X, Y = np.meshgrid(r.x_m, r.y_m)
    exacta = 20+(inicial(X, Y)-20)*np.exp(-p.alpha_m2_s*np.pi**2*(1/Lx**2+1/Ly**2)*.2)
    error = np.max(abs(r.temperatura_C[-1]-exacta))
    assert error/abs(A) < .005
    print(f'\n2D: malla={nx}x{ny}, L={Lx:g}x{Ly:g} m, k={k:g}, A={A:g} K, '
          f'dt={r.dt_s:.6g} s, error final={error:.6g} K')


@pytest.mark.parametrize('nx,ny,nz,Lx,Ly,Lz,k,A', [
    (12, 10, 8, 1., 1.3, .7, 1., 10.),
    (24, 20, 16, 1., 1.3, .7, 1., 10.),
    (16, 12, 10, 2., 1., 1.5, 2., -8.),
])
def test_e05_3d(nx, ny, nz, Lx, Ly, Lz, k, A):
    p = Parametros3D(longitud_x_m=Lx, longitud_y_m=Ly, longitud_z_m=Lz,
                     celdas_x=nx, celdas_y=ny, celdas_z=nz,
                     conductividad_W_mK=k, densidad_kg_m3=2, calor_especifico_J_kgK=5,
                     tiempo_final_s=.1)
    def inicial(X, Y, Z):
        return 20+A*np.sin(np.pi*X/Lx)*np.sin(np.pi*Y/Ly)*np.sin(np.pi*Z/Lz)
    r = resolver_3d(p, Dirichlet3D(), inicial)
    Z, Y, X = np.meshgrid(r.z_m, r.y_m, r.x_m, indexing='ij')
    exacta = 20+(inicial(X, Y, Z)-20)*np.exp(-p.alpha_m2_s*np.pi**2*(1/Lx**2+1/Ly**2+1/Lz**2)*.1)
    error = np.max(abs(r.temperatura_C[-1]-exacta))
    assert error/abs(A) < .005
    print(f'\n3D: malla={nx}x{ny}x{nz}, L={Lx:g}x{Ly:g}x{Lz:g} m, k={k:g}, '
          f'A={A:g} K, dt={r.dt_s:.6g} s, error final={error:.6g} K')


def configurar(dim, **cambios):
    valores = dict(longitud_x_m=3, longitud_y_m=2, celdas_x=6, celdas_y=4,
                   conductividad_W_mK=2, densidad_kg_m3=3, calor_especifico_J_kgK=4,
                   tiempo_final_s=.05, paso_tiempo_s=.01)
    if dim == 2:
        p, solver = Parametros2D(espesor_m=.7, **valores), resolver_2d_bordes
    else:
        p, solver = Parametros3D(longitud_z_m=1.5, celdas_z=3, **valores), resolver_3d_bordes
    p = replace(p, **cambios)
    caras = {f'{e}_{lado}': Neumann(0) for e in 'xyz'[:dim] for lado in ('min', 'max')}
    return p, solver, caras


@pytest.mark.parametrize('dim,k,tf', [(2, 1., 1.), (2, 3., 3.), (3, 1., 1.)])
def test_e05_adiabatico(dim, k, tf):
    p, solver, caras = configurar(dim, conductividad_W_mK=k, tiempo_final_s=tf)
    r = solver(p, caras, lambda *xyz: 30+5*np.cos(np.pi*xyz[0]/3)+2*np.sin(np.pi*xyz[1]/2),
               n_guardados=10000)
    # Energía recalculada a partir de los campos y la capacidad de celda.
    V = p.dx_m*p.dy_m*p.espesor_m if dim == 2 else np.prod(p.pasos_espaciales_m)
    energia = p.densidad_kg_m3*p.calor_especifico_J_kgK*V*r.temperatura_C.reshape(len(r.tiempos_s), -1).sum(axis=1)
    residuo = np.max(abs(energia-energia[0]))
    assert residuo < 1e-9
    assert np.ptp(r.temperatura_C[-1]) < np.ptp(r.temperatura_C[0])
    print(f'\nAdiabático {dim}D: k={k:g}, tf={tf:g} s, '
          f'variación máxima de energía={residuo:.3g} J, '
          f'rango térmico {np.ptp(r.temperatura_C[0]):.6g} -> {np.ptp(r.temperatura_C[-1]):.6g} K')


@pytest.mark.parametrize('dim,q,rho,cp', [(2, 60., 2., 3.), (2, 120., 2., 3.),
                                        (2, 60., 4., 3.), (3, 60., 2., 3.)])
def test_e05_fuente(dim, q, rho, cp):
    p, solver, caras = configurar(dim, densidad_kg_m3=rho, calor_especifico_J_kgK=cp,
                                  tiempo_final_s=.08)
    r = solver(p, caras, 20, fuente_W_m3=q, n_guardados=10000)
    exacta = 20+q*r.tiempos_s/(rho*cp)
    error = np.max(abs(r.temperatura_C-exacta.reshape((-1,)+(1,)*dim)))
    assert error < 1e-10
    print(f'\nFuente {dim}D: q={q:g} W/m³, rho={rho:g}, cp={cp:g}, '
          f'pendiente exacta={q/(rho*cp):g} K/s, '
          f'Tfinal={r.temperatura_C[-1].mean():.6g} °C, error={error:.3g} K')


@pytest.mark.parametrize('dim', [2, 3])
@pytest.mark.parametrize('q', [7., -7., 14.])
def test_e05_neumann(dim, q):
    p, solver, caras = configurar(dim)
    caras['x_min'] = Neumann(q)  # Convención del código: positivo entrante.
    r = solver(p, caras, 30, n_guardados=10000)
    area = p.longitud_y_m*(p.espesor_m if dim == 2 else p.longitud_z_m)
    delta_E = r.energia_relativa_J-r.energia_relativa_J[0]
    exacta = q*area*r.tiempos_historia_s
    error = np.max(abs(delta_E-exacta))
    assert error < 1e-10
    # Primer paso: estado inicialmente uniforme, sin intercambio interior.
    dx = p.longitud_x_m/p.celdas_x
    esperado_cara = 30+q*r.dt_s/(p.densidad_kg_m3*p.calor_especifico_J_kgK*dx)
    np.testing.assert_allclose(r.temperatura_C[1][..., 0], esperado_cara, atol=1e-12)
    print(f'\nNeumann {dim}D: q_entrante={q:g} W/m², área={area:g} m², '
          f'DeltaE={delta_E[-1]:.6g} J, esperado={exacta[-1]:.6g} J, error={error:.3g} J')


@pytest.mark.parametrize('dim,h,ambiente', [(2, 0., 20.), (2, 5., 20.),
                                          (2, 20., 20.), (3, 5., 40.)])
def test_e05_robin(dim, h, ambiente):
    # Todas las caras salvo x_max son adiabáticas; permite calcular la
    # potencia del primer instante de forma independiente y sin esquinas.
    p, solver, caras = configurar(dim)
    caras['x_max'] = Robin(h, ambiente)
    r = solver(p, caras, 30, n_guardados=10000)
    area = p.longitud_y_m*(p.espesor_m if dim == 2 else p.longitud_z_m)
    dx = p.longitud_x_m/p.celdas_x
    q = 0 if h == 0 else (ambiente-30)/(dx/(2*p.conductividad_W_mK)+1/h)
    esperado = q*area
    assert r.potencia_exterior_W[0] == pytest.approx(esperado, abs=1e-12)
    delta = np.diff(r.energia_relativa_J)
    np.testing.assert_allclose(delta, r.dt_s*r.potencia_exterior_W[:-1], atol=1e-10)
    if h == 0:
        np.testing.assert_array_equal(r.temperatura_C, 30)
    else:
        assert np.sign(r.temperatura_C[-1].mean()-30) == np.sign(ambiente-30)
    print(f'\nRobin {dim}D: h={h:g} W/(m² K), Tamb={ambiente:g} °C, '
          f'potencia inicial={r.potencia_exterior_W[0]:.6g} W '
          f'(exacta={esperado:.6g}), Tmedia final={r.temperatura_C[-1].mean():.8g} °C')


@pytest.mark.parametrize('dim', [1, 2, 3])
def test_e05_estabilidad(dim):
    if dim == 1:
        p = Parametros1D(n_intervalos=40, tiempo_final_s=10)
        limite = p.dt_max_s
        ejecutar = lambda: resolver_1d(replace(p, paso_tiempo_s=1.01*limite))
    elif dim == 2:
        p = Parametros2D(celdas_x=20, celdas_y=20, tiempo_final_s=10)
        limite = paso_maximo_s(p)
        ejecutar = lambda: resolver_2d(replace(p, paso_tiempo_s=1.01*limite), Dirichlet2D())
    else:
        p = Parametros3D(celdas_x=20, celdas_y=20, celdas_z=20, tiempo_final_s=10)
        limite = paso_maximo_3d_s(p)
        ejecutar = lambda: resolver_3d(replace(p, paso_tiempo_s=1.01*limite), Dirichlet3D())
    with pytest.raises(ValueError, match='inestable'):
        ejecutar()
    print(f'\nEstabilidad {dim}D: límite={limite:.6g} s; '
          f'propuesto={1.01*limite:.6g} s -> rechazo esperado, test aprobado')
