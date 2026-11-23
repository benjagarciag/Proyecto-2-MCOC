# E07 — Etapa 6: modelo didáctico de hidratación

Trabajo exclusivo en `E07_pruebas`. Se conservan los módulos y resultados de
Etapas 1–5, el IFC y los solvers. No se instala nada ni se publica en GitHub.
Esta etapa calcula curvas y fuentes por edad; no simula la temperatura espacial
de la fundación, clima, pérdidas de borde ni hidratación dependiente de T.

## Referencias del profesor revisadas antes de programar

- `Enunciados e Instrucciones/Guias/DIFUSION_DE_CALOR_1D_2D_3D.md`, §§23–24:
  transformación de elevación adiabática a fuente y ejemplo exponencial.
- La misma guía, §25: la dependencia de temperatura y edad equivalente se
  introduce después de verificar la hidratación simple; no se incorpora aquí.
- `Guias/G05_DIFUSION_TERMICA_FD.md`, sección fuente volumétrica frente a borde:
  hidratación en W/m³, distinta del flujo superficial en W/m².
- `Instrucciones/Proyecto 2 - Introducción General.txt` y
  `Instrucciones/Caso base, criterios y referencias.txt`: propiedades y curva
  justificadas, y límites de transferir parámetros de un caso real al docente.

## Modelo y parámetros configurables

Para edad cronológica `a=t-t_colocacion`, en segundos:

```
θ_ad(a) = θ∞ [1 − exp(−a/τ)]                    [K]
q'''(a) = ρ cp (θ∞/τ) exp(−a/τ)               [W/m³]
H(a) = ρ cp θ_ad(a)                            [J/m³]
```

Para a<0, las tres expresiones valen cero: todavía no se ha colocado.
En a=0 la elevación y energía acumulada son cero y la fuente instantánea es
finita, no nula. No hay un impulso de energía en el instante de colocación.

| Parámetro | Valor del caso | Procedencia |
| --- | ---: | --- |
| ρ | 2400 kg/m³ | Ejemplo pedagógico §24 |
| cp | 900 J/(kg·K) | Ejemplo pedagógico §24 |
| θ∞ | 45 K de elevación | Ejemplo pedagógico §24 |
| τ | 108000 s = 30 h | Ejemplo pedagógico §24 |

**Son parámetros sintéticos didácticos, no mediciones ni calibración de M1.**
Se declaran externamente en `casos/e07/hidratacion.json`; no se cambian las
propiedades IFC. Se usa densidad y cp constantes. No se necesita k para calcular
la fuente; sí será necesario para la conducción posterior.

De estas unidades resultan:

```
ρ cp = 2 160 000 J/(m³ K)
q'''(0) = 900 W/m³
H(∞) = 97 200 000 J/m³ = 97,2 MJ/m³
```

Una elevación de 1 K equivale a una diferencia de 1 °C; θ no es una temperatura
absoluta. El modelo exponencial comienza con su tasa máxima y luego decae:
no reproduce período de inducción ni pico retardado de una mezcla experimental.
La colocación a 19 °C o 18 °C no altera su cinética en esta simplificación.

## Energía exacta durante cada intervalo

Para una vertida que empieza en s, definir A=max(t0−s,0), B=max(t1−s,0):

```
ΔH = ρ cp θ∞ exp(−A/τ) [1−exp(−(B−A)/τ)]        [J/m³]
E_i = ΔH_i V_i                                 [J por voxel]
q'''_medio = ΔH / (t1−t0)                       [W/m³]
```

Se exige t1≥t0 y duración positiva para pedir la fuente media. Un intervalo
nulo tiene energía cero. Las operaciones usan `expm1` para evitar cancelación
cerca de a=0 y en intervalos tardíos, donde restar dos energías acumuladas
redondeadas podría perder un incremento todavía representable.

Un paso 5–7 h integra la Vertida 02 solo entre 6 y 7 h. Se usa su calendario,
no solamente la máscara activa al comienzo, que la excluiría incorrectamente.
Si el intervalo termina justo en 6 h, la energía de 02 es cero, aunque su fuente
instantánea al activarse sea 900 W/m³. Las sumas de intervalos son aditivas.

Multiplicar W/m³ por m³ da W; integrar W en segundos da J. Para transformar
esta energía en un aumento adiabático se divide por `ρ cp V`, recuperando Δθ,
independientemente del tamaño de voxel. No se incluye la energía sensible
asociada a ingresar hormigón a su temperatura de colocación.

## Reutilización y API

Nuevo módulo `desarrollo/mcplan/hidratacion.py`:

| API | Resultado |
| --- | --- |
| `CurvaAdiabatica(...)` | Exponencial con θ∞, τ, ρ y cp configurables. |
| `.elevacion_K(edad_s)` | Elevación adiabática ideal escalar o array. |
| `.valor(edad_s)` | Fuente instantánea en W/m³. |
| `.acumulada_J_m3(edad_s)` | Energía acumulada por volumen. |
| `.energia_intervalo_J_m3(a0,a1)` | Integral analítica por edad. |
| `HidratacionVertidas(programa, curvas_por_material)` | Vincula calendario de Etapa 5 y curvas por etiqueta de hormigón. |
| `.fuente_W_m3(estado)` | Campo ZYX, finito y no negativo; cero en todo inactivo/vacío. |
| `.energia_volumetrica_intervalo_J_m3(t0,t1)` | Energía por volumen, para cada voxel. |
| `.energia_intervalo_J(t0,t1)` | Campo de energía por voxel; sumar para obtener la energía total. |
| `.fuente_media_W_m3(t0,t1)` | Campo promedio exacto durante un intervalo positivo. |

Se reutilizan `ProgramaConstruccion`, `EstadoConstruccion` y sus edades, sin
reinicializar ni modificar temperaturas. Las cinco vertidas tienen diferentes
IDs y edades, pero usan una sola curva porque comparten el material M1.
La API admite curvas distintas para etiquetas diferentes sin confundir
`vertida_id` con material. Se rechazan estados de otro programa y etiquetas
sin curva. Los mapas y campos devueltos son de solo lectura.

Se reutiliza `preparar_fuente_W_m3` de E04 para validar forma, finitud y
no negatividad. `valor` y `acumulada_J_m3` implementan la misma interfaz que
`PulsoTermico` en `fuente_temporal_2d.py`; el solver temporal 3D existente
puede consumir una curva para el ensayo adiabático de una sola edad uniforme.
No se sustituye el pulso existente, no se altera su ley y no se crea otro solver.

## Resultados didácticos

En t=24 h, las edades y fuentes son distintas aunque el material sea el mismo:

| Vertida | Edad [h] | Elevación ideal [K] | Fuente [W/m³] |
| --- | ---: | ---: | ---: |
| 01 | 24 | 24,780 | 404,396 |
| 02 | 18 | 20,303 | 493,930 |
| 03 | 12 | 14,836 | 603,288 |
| 04 | 6 | 8,157 | 736,858 |
| 05 | 0 | 0 | 900 |

Resultados integrados usando los volúmenes **voxelizados** de h=0,5 m:

| Tiempo | Potencia total instantánea [kW] | Energía generada acumulada [GJ] |
| --- | ---: | ---: |
| 0 h | 121,050 | 0 |
| 24 h | 374,087 | 22,049599 |
| 72 h | 75,527 | 54,294098 |
| 168 h | 3,079 | 62,118507 |
| 336 h | 0,011384 | 62,449770 |

El límite asintótico es 62,451 GJ para 642,5 m³. El total hereda el error del
volumen voxelizado: no es una predicción experimental ni un cálculo con los
636,775 m³ exactos de las mallas IFC. Ningún resultado representa Tmax de
la fundación ni permite concluir cumplimiento de los límites térmicos.

## Ejecutar y resultados gráficos

Desde la raíz de esta copia, con el Python existente:

```powershell
# Terminal con el entorno del proyecto activado
python -B casos/e07/hidratar_vertidas.py
```

También puede ejecutarse ese archivo en VS Code seleccionando dicho intérprete.
`--parametros ruta.json` cambia la configuración; `--solo-datos` omite figuras.
El horizonte por defecto es de 336 h (14 días). El paso de muestreo de 0,25 h
es solo para curvas: no es un paso de integración de un solver térmico.

Nuevas salidas fijas en `resultados/e07/hidratacion/`:

- `curva_adiabatica_y_fuente.png`: elevación y fuente de la mezcla didáctica.
- `hidratacion_por_vertida.png`: cinco curvas desplazadas por sus horarios IFC.
- `energia_hidratacion.png`: energía acumulada por vertida y por intervalos;
  los intervalos de las barras tienen duraciones diferentes, indicadas en el eje.
- `resumen_hidratacion.json`: parámetros y procedencia, SHA del IFC, calendario,
  volumen usado, edades, fuentes, potencias, energías y residuo de la suma.

El ejecutor reutiliza extracción/asignación para preparar el caso, pero no
ejecuta sus scripts ni regenera ningún PNG anterior. Solo guarda estas salidas.

## Pruebas

**528 pruebas aprobadas: 481 anteriores y 47 nuevas.**
`desarrollo/tests/test_hidratacion.py` comprueba unidades y valores del ejemplo,
derivadas, cuadratura independiente, colas numéricas, parámetros inválidos,
escalado con ρ/cp/θ∞, tasas por edad, activaciones, intervalos que cruzan eventos,
aditividad, fuente media, refinamiento de cubos exactos y conservación de archivos.

Incluye un ensayo adiabático de ocho celdas con el solver temporal 3D existente:
verifica `T=T0+θ_ad` y aumento de energía igual al calor generado. Es una prueba
unitaria sintética, no una simulación de la fundación.

```powershell
python -B -m pytest -q -p no:cacheprovider --basetemp=.venv/cache/pytest_etapa6_02
```

## Límites y pendientes antes de Etapa 7

- Obtener datos de M1 y calibrar o sustituir esta curva; justificar también
  k, ρ y cp físicos y mantener una única capacidad térmica coherente al acoplar.
- Revisar la resolución: h=1 m pierde V02; h=0,5 m mantiene el error local
  importante de V04. La generación no corrige esos errores de geometría.
- Autorizar el acoplamiento con conducción 3D sobre geometría irregular,
  bordes construidos y colocaciones. Usar la energía exacta o fuente media y
  evitar contarla dos veces; inicializar nuevos voxeles en el instante correcto.
- Respetar el límite de estabilidad del operador de conducción y cortar pasos
  en los eventos. La integración exacta de la fuente no elimina ese requisito.
- Dependencia con temperatura, edad equivalente/Arrhenius, clima y simulación
  térmica completa permanecen fuera de esta etapa.
