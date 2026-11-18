"""Agregación independiente: conserva intacto el ejecutor cuya huella ya está guardada."""
from hashlib import sha256
import sensibilidad_radiacion as estudio


def main():
    f=estudio.f;f.iniciar()
    rutas=sorted(p for p in (estudio.SALIDA/'ambas/malla_0.4_paso300').glob('*.json') if p.name.startswith('M'))
    assert len(rutas)==24
    filas=[f.base.viento.leer(p)['corrida'] for p in rutas]
    f.base.comun.validar_filas(filas)
    matriz=dict(corridas=filas,riesgo_observado=f.ESTADO[0].riesgo(filas),
        riesgo_336=f.ESTADO[0].riesgo([dict(r['base_336h'],peso=r['peso'],clima=r['clima']) for r in filas]),
        picos_no_resueltos=sum(r['pico_no_resuelto'] for r in filas),
        archivos=[dict(ruta=str(p.relative_to(f.RAIZ)),sha256=sha256(p.read_bytes()).hexdigest()) for p in rutas],
        agregador_sha256=sha256(__import__('pathlib').Path(__file__).read_bytes()).hexdigest())
    f.base.escribir(estudio.SALIDA/'ambas/malla_0.4_paso300/matriz.json',matriz)
    print('Matriz24 pares:',matriz['riesgo_336'],matriz['riesgo_observado'],'alertas',matriz['picos_no_resueltos'])


if __name__=='__main__':main()
