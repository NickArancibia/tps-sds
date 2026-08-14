# SdS TP1 — Búsqueda eficiente de partículas vecinas (Cell Index Method)

Informe de resultados. El contexto y las decisiones de diseño están en
[AGENTS.md](../AGENTS.md); las instrucciones de uso, en [README.md](../README.md).

Todas las mediciones de este informe se hicieron con `L = 20`, `rc = 1`,
`r_i ~ U[0.23, 0.26]`, sin contorno periódico, **300 mediciones por punto**
(100 repeticiones cronometradas × 3 configuraciones de partículas distintas, semillas 42-44).
Las barras de error de todos los gráficos son el **desvío estándar muestral**.

---

## 1. Implementación y validación

El motor está en Java (`cim-java/`) y el análisis en Python (`analysis/`). La simulación corre
offline: Java escribe `static.txt`, `dynamic.txt`, `neighbors.txt` y `run.json`, y los scripts de
Python **sólo leen y grafican** — nunca recalculan vecindades.

Dos partículas son vecinas cuando su distancia **borde a borde** es menor que `rc`:

```
sqrt((x_i - x_j)² + (y_i - y_j)²) - r_i - r_j  <  rc
```

Con contorno periódico las diferencias se toman por imagen mínima
(`Δx -= L·round(Δx/L)`), lo que convierte al dominio en un toro.

**Validación.** `BruteForce` (O(N²)) recorre todos los pares y sirve de referencia: para cualquier
`M` válido, con y sin contorno periódico, el CIM devuelve **exactamente el mismo** conjunto de
vecinos. Es la red de seguridad del TP y se corre con `--verify`:

```bash
java -jar cim-java/target/cim.jar --N 1000 --M 13 --verify --out /tmp/check
java -jar cim-java/target/cim.jar --N 1000 --M 13 --pbc --verify --out /tmp/check
```

**Generación sin solapamiento.** Muestreo por rechazo: se sortea una posición candidata y, si se
solapa con alguna partícula ya colocada, se descarta y se sortea otra. El chequeo usa una grilla
auxiliar de celdas de lado `2·rMax`, así que cuesta O(1) por intento en vez de O(N). Con `L = 20`
el método satura alrededor de **1067 partículas** (≈50% del área ocupada, consistente con el límite
de *random sequential adsorption* para discos); los barridos usan **N = 1060** como máximo.

---

## 2. Pregunta conceptual: ¿cómo cambia el criterio `L/M > rc` con `r_i > 0`?

Para partículas **puntuales**, el CIM exige que el lado de celda sea mayor que el radio de
interacción:

```
L/M > rc
```

La razón es que sólo se revisan las 8 celdas adyacentes más la propia: si la celda fuera más chica
que `rc`, una vecina legítima podría estar en una celda a dos posiciones de distancia y el método
no la encontraría.

Con partículas de **radio no nulo** el criterio de vecindad ya no es sobre la distancia entre
centros sino sobre la distancia **borde a borde**. Reescribiéndolo en términos de los centros:

```
dist(centros) < rc + r_i + r_j  ≤  rc + 2·r_max
```

Es decir: **el alcance efectivo entre centros crece en `2·r_max`**. El borde de una vecina puede
caer dentro del alcance aunque su centro esté mucho más lejos que `rc`. Para que siga alcanzando
con mirar las celdas adyacentes, la celda tiene que ser más grande que ese alcance efectivo:

```
L/M > rc + 2·r_max        →        M_max = floor( L / (rc + 2·r_max) )
```

Con los valores del enunciado (`L = 20`, `rc = 1`, `r_max = 0.26`) queda `L/M > 1.52` y por lo
tanto **`M_max = 13`**.

Dos observaciones importantes:

- Se usa `r_max` —el radio **máximo presente en el sistema**— y no el radio medio, porque el
  criterio tiene que valer para el **peor par posible**: dos partículas ambas de radio máximo.
  Usar el promedio dejaría escapar vecindades en la cola de la distribución de radios.
- El programa **valida esto y aborta con un mensaje explícito** si se pide un `M` mayor, tal como
  pide el enunciado. No se "arregla" silenciosamente ampliando el radio de búsqueda a 2 celdas:
  eso escondería el error conceptual y cambiaría el costo del método.

```
$ java -jar cim-java/target/cim.jar --N 500 --M 14
ERROR: M=14 es inválido para L=20.0000, rc=1.0000 y rMax=0.2600: el lado de celda
L/M=1.4286 es menor que rc + 2*rMax = 1.5200. El máximo M permitido es 13.
```

---

## 3. Punto 3 — Variación de `M`

![Tiempo vs M](../output/bench/tiempo_vs_M.png)

Barrido `M = 1 … 13` sobre **la misma** configuración de partículas, para un `N` intermedio (500) y
el máximo de la geometría (1060). Ambos ejes son lineales y equiespaciados: `M` recorre enteros
consecutivos y los tiempos llevan ticks uniformes. Con `--log-y` se obtiene la misma figura en
escala logarítmica, que separa mejor la curva de `N = 500` en la zona de `M` grande.

| M | N = 500 [ms] | desvío | N = 1060 [ms] | desvío |
|---:|---:|---:|---:|---:|
| 1 | 0.5571 | 0.2273 | 1.7513 | 0.0558 |
| 2 | 0.8104 | 0.2634 | 2.8345 | 0.1373 |
| 3 | 0.4932 | 0.1352 | 1.8540 | 0.0601 |
| 4 | 0.3372 | 0.0637 | 1.3236 | 0.0944 |
| 5 | 0.2316 | 0.0323 | 0.9841 | 0.0424 |
| 6 | 0.1803 | 0.0174 | 0.7741 | 0.0288 |
| 7 | 0.1423 | 0.0097 | 0.6756 | 0.0893 |
| 8 | 0.1214 | 0.0107 | 0.5471 | 0.0448 |
| 9 | 0.1045 | 0.0067 | 0.4693 | 0.0217 |
| 10 | 0.0973 | 0.0129 | 0.4215 | 0.0278 |
| 11 | 0.0883 | 0.0086 | 0.3855 | 0.0178 |
| 12 | 0.0794 | 0.0065 | 0.3585 | 0.0247 |
| **13** | **0.0758** | 0.0042 | **0.3333** | 0.0144 |

**El `M` óptimo es 13, o sea el máximo que permite el método.** El tiempo baja monótonamente a
partir de `M = 3`, sin llegar nunca a un mínimo interior.

Eso tiene una explicación clara. El costo del CIM tiene dos términos: uno proporcional a `M²`
(recorrer todas las celdas, incluso las vacías) y otro proporcional a la cantidad de comparaciones,
que va como `N · (partículas por celda) ≈ N²/M²`. El óptimo teórico está donde ambos se equilibran,
en `M ~ N^(1/4)·algo`, es decir con del orden de una partícula por celda. Pero acá el criterio de
§2 **corta el barrido antes de llegar a ese punto**: con `M = 13` todavía hay `1060/169 ≈ 6.3`
partículas por celda para el `N` máximo (y `≈ 3` para `N = 500`), muy lejos del régimen donde el
recorrido de celdas vacías empezaría a dominar. Para llegar ahí haría falta `M ≈ 32`, prohibido por
`M_max = 13`.

**Ganancia respecto de la fuerza bruta** (`M = 1`, una sola celda con todas las partículas):
**7.3×** para `N = 500` y **5.3×** para `N = 1060`.

**Por qué `M = 2` es el peor caso.** Es el único punto que rompe la monotonía, y no es un artefacto.
Con `M = 2` hay 4 celdas y la vecindad de cada una cubre a **todas** las demás: se hacen exactamente
las mismas comparaciones que en fuerza bruta, pero además se paga construir la grilla y recorrer las
listas enlazadas, con peor localidad de memoria que el doble bucle directo. `M = 3` es el primer
valor en el que la grilla realmente descarta pares.

---

## 4. Punto 4 — Variación de `N`

![Tiempo vs N](../output/bench/tiempo_vs_N.png)

Ambas curvas usan el `M` óptimo del punto 3.

**Cómo leer el gráfico.** El eje `N` es categórico: los 12 valores medidos están log-espaciados, así
que se los dibuja equiespaciados y cada uno lleva su etiqueta. El eje de tiempos es lineal con
ticks uniformes. Dos consecuencias a tener presentes:

- Los puntos con `N ≤ 194` quedan comprimidos contra el cero, porque el rango de tiempos abarca casi
  tres órdenes de magnitud (de 0.0006 ms a 0.26 ms). Los valores están en la tabla de abajo, y
  `python3 analysis/plot_n.py ... --log` produce la misma figura en escala log-log, donde se
  distinguen todos los puntos.
- Como el eje `N` está espaciado logarítmicamente pero el de tiempos no, **la curva se ve
  exponencial aunque sea una ley de potencia** de exponente ≈ 1.2. Los exponentes reportados abajo
  salen del ajuste sobre los datos, no de la pendiente visual de esta figura.

| N | densidad libre [ms] | desvío | densidad fija [ms] | desvío |
|---:|---:|---:|---:|---:|
| 10 | 0.00466 | 0.00282 | 0.00062 | 0.00192 |
| 15 | 0.00567 | 0.00134 | 0.00133 | 0.00148 |
| 23 | 0.00629 | 0.00320 | 0.00211 | 0.00020 |
| 36 | 0.00674 | 0.00142 | 0.00347 | 0.00016 |
| 55 | 0.01064 | 0.00348 | 0.00529 | 0.00031 |
| 83 | 0.01327 | 0.00347 | 0.00885 | 0.00053 |
| 127 | 0.01588 | 0.00194 | 0.01496 | 0.01056 |
| 194 | 0.02721 | 0.00381 | 0.02126 | 0.00115 |
| 297 | 0.04096 | 0.00597 | 0.03694 | 0.00612 |
| 454 | 0.06341 | 0.00617 | 0.05974 | 0.00370 |
| 694 | 0.13794 | 0.01265 | 0.11142 | 0.02328 |
| 1060 | 0.25739 | 0.00810 | 0.17026 | 0.00682 |

### 4.1 Densidad libre (`L = 20` fijo, `M = 13`)

12 valores de `N` log-espaciados entre 10 y 1060. Como `L` no cambia, la densidad `ρ = N/L²` crece
con `N`: va de 0.025 a 2.65.

La curva tiene **dos regímenes**. Para `N ≲ 100` el tiempo es casi plano: con 169 celdas y unas
pocas decenas de partículas, lo que domina es el **costo fijo de recorrer las `M² = 169` celdas y
sus vecindades**, la mayoría vacías. Para `N` grande manda la cantidad de comparaciones y la curva
crece como **`t ~ N^1.29`**, superlineal: al aumentar `N` con `L` fijo crece también la cantidad de
partículas por celda, así que cada partícula tiene más candidatas que revisar.

### 4.2 Densidad fija (`ρ = 1.25`, `L = √(N/ρ)`)

Se tomó como densidad intermedia la del sistema de `N = 500` con `L = 20`, o sea `ρ = 1.25`, y se
hizo crecer `L` junto con `N` para mantenerla constante.

Una aclaración de método: el enunciado pide usar "el `M` óptimo del punto 3", pero ese óptimo es en
realidad un **tamaño de celda** óptimo. Como acá `L` cambia, dejar `M` constante cambiaría el lado
de celda `L/M` y con él la cantidad de partículas por celda, que es justamente lo que determina el
costo. Por eso el barrido **escala `M` con `L`** para conservar el lado de celda del punto 3
(≈ 1.53); el lado de celda resultante se mantiene entre 1.53 y 1.79 en todo el rango. Con
`--fixedM` se puede forzar el `M` constante.

El resultado es el esperado: la curva crece **más despacio que la de densidad libre**
(**`t ~ N^1.19`** contra `N^1.29`) y se separa claramente de ella en la última década, donde la
densidad libre llega a `ρ = 2.65` — más del doble de la densidad fija. A densidad constante el
número de vecinos por partícula no cambia, así que el trabajo por partícula es aproximadamente
constante y el escalamiento se acerca al lineal; el exceso sobre `N^1` que queda se explica por la
jerarquía de memoria (con `N` grande los arrays de posiciones dejan de caber en los niveles más
rápidos de caché).

A `N` chico la relación se invierte y la densidad fija resulta **más rápida**: con `ρ` constante y
`N = 10` el dominio es de `L = 2.83` y la grilla tiene una sola celda, mientras que la corrida de
densidad libre tiene que recorrer las 169 celdas casi vacías de un dominio de `L = 20`. No es una
ventaja del método sino la misma observación del régimen de costo fijo de §4.1.

Los tres o cuatro puntos de `N` más chico a densidad fija tienen desvíos comparables a la media:
esos tiempos son de ~1 µs, ya en el límite de resolución práctica de `System.nanoTime()` y muy
sensibles al ruido del sistema operativo. Los puntos con `N ≥ 100`, que son los que importan para el
escalamiento, tienen desvíos del orden del 5%.

---

## 5. Conclusiones

1. Con partículas de radio no nulo, el criterio del CIM pasa de `L/M > rc` a
   **`L/M > rc + 2·r_max`**, porque el alcance efectivo entre centros crece en `2·r_max`. Con los
   valores del enunciado eso da `M_max = 13`.
2. El `M` óptimo resulta ser **el máximo permitido**: el criterio de validez corta el barrido antes
   de que el costo de recorrer celdas vacías compense el ahorro en comparaciones.
3. El CIM con `M = 13` es entre **5× y 7× más rápido** que la fuerza bruta en el rango estudiado, y
   la ventaja crece con la densidad.
4. A **densidad constante** el CIM escala casi linealmente con `N` (`t ~ N^1.19`), que es la
   propiedad que lo hace útil: es el escenario de una simulación dinámica real, donde el método se
   reinvoca en cada paso temporal. A **densidad creciente** el escalamiento se degrada
   (`t ~ N^1.29`) porque crece la ocupación de cada celda.

---

## 6. Reproducir estos resultados

```bash
cd cim-java && mvn package && cd ..

java -cp cim-java/target/cim.jar ar.edu.itba.sds.bench.BenchmarkRunner \
     --sweep M --N 500,1060 --reps 100 --seeds 3 --out output/bench/bench_M.csv
java -cp cim-java/target/cim.jar ar.edu.itba.sds.bench.BenchmarkRunner \
     --sweep N --M 13 --reps 100 --seeds 3 --points 12 --out output/bench/bench_N_libre.csv
java -cp cim-java/target/cim.jar ar.edu.itba.sds.bench.BenchmarkRunner \
     --sweep density --M 13 --rho 1.25 --reps 100 --seeds 3 --points 12 \
     --out output/bench/bench_N_densidad_fija.csv

python3 analysis/plot_m.py output/bench/bench_M.csv
python3 analysis/plot_n.py output/bench/bench_N_libre.csv output/bench/bench_N_densidad_fija.csv
```

Los tiempos absolutos dependen de la máquina; las tendencias y las relaciones entre curvas, no.
