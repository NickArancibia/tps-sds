# AGENTS.md — SdS TP1: Búsqueda Eficiente de Partículas Vecinas

Contexto completo del trabajo práctico para cualquier agente/LLM que abra este repositorio por
primera vez. Leer este archivo **antes** de escribir código o proponer cambios.

---

## 1. De qué se trata

Materia: **Simulación de Sistemas (SdS) — ITBA**.
Trabajo Práctico Nro. 1: **Búsqueda eficiente de partículas vecinas** mediante el algoritmo
**Cell Index Method (CIM)**.

El sistema es un área **cuadrada de lado `L`** que contiene **`N` partículas** con radios
`r_i > 0` y un **radio de interacción `r_c`**. Dos partículas son vecinas si la distancia
**borde a borde** entre ellas es menor que `r_c`.

Valores por defecto del enunciado (usar salvo indicación contraria):

| Parámetro | Valor por defecto |
|---|---|
| `L` (lado del área) | `20` |
| `r_c` (radio de interacción) | `1` |
| `r_i` (radio de partícula) | `U[0.23, 0.26]` (uniforme) |
| `M` | grilla de `M × M` celdas, variable de estudio |
| `N` | variable de estudio |

**Fechas de demo en vivo: 7 y 10 de agosto de 2026** (la demo es dinámica: se generan partículas
en el momento con distintos `N`, `L`, `M`, `r_c` y se muestran los outputs).

El enunciado original está en `/home/nick/Descargas/TP1_Enunciado.pdf` (fuera del repo). Este
archivo resume su contenido; si hay conflicto, **el PDF manda**.

---

## 2. Consigna, punto por punto

### Punto 1 — Implementar el CIM

**Inputs:** posiciones y radios de `N` partículas + los parámetros `N`, `L`, `M`, `r_c`, y un flag
de **condiciones periódicas de contorno (PBC)**.

**Outputs:**
1. Una lista que, para cada partícula, indique cuáles son sus vecinas a distancia (borde a borde)
   menor que `r_c`.
2. El **tiempo de ejecución** del cálculo de vecinos.
3. Una **figura** con las posiciones de todas las partículas, con una partícula elegida (pasada
   como input) de un color y sus vecinas de otro.

Las partículas se generan **aleatoriamente y sin solaparse** dentro del área de lado `L`.

Dos variantes obligatorias:
- **a)** Sin PBC (las paredes son bordes reales del dominio).
- **b)** Con PBC (el dominio es un toro; se usa convención de imagen mínima).

**Pregunta conceptual a responder en el informe:** ¿cómo se modifica el criterio `L/M > r_c`
cuando las partículas no son puntuales (`r_i > 0`)? → ver §5.3 y la §2 de `docs/informe.md`.

### Punto 2 — Demostración en vivo

En clase. Debe poder generarse en el momento un sistema con distintos `(N, L, M, r_c)` y mostrar
los outputs del punto 1. La demo se hace con **Matplotlib interactivo**: se hace **clic con el
mouse** sobre una partícula y se colorean las vecinas **leídas del output del CIM** (no
recalculadas en el visualizador — el visualizador sólo pinta).

### Punto 3 — Variación de `M`

Con `L=20`, `r_c=1`, `r_i = U[0.23, 0.26]`:
- Tomar **dos valores de `N`**: uno intermedio y el **más alto posible** para la geometría.
- Para cada uno, variar `M` desde `1` (equivalente a fuerza bruta) hasta el **máximo permitido por
  el método**. Si `M` supera ese máximo, el programa **debe dar error** (ver §5.3).
- Graficar **tiempo de cómputo vs. `M`**, promediando **varias corridas** (10, 100 o 1000) con
  **barras de error = desvío estándar**.
- Usar **escala logarítmica** en los ejes que varíen en distintos órdenes de magnitud.

### Punto 4 — Variación de `N`

Usando el **`M` óptimo** hallado en el punto 3:

- **4.1 — Densidad libre:** `L=20` fijo, al menos **10 valores de `N`** desde `N=10` hasta el
  máximo generable en la geometría. Graficar tiempo promedio vs. `N` (con desvío).
- **4.2 — Densidad fija:** elegir una densidad intermedia de 4.1 y **aumentar `L` junto con `N`**
  manteniendo `ρ = N/L²` constante. Graficar tiempo promedio vs. `N` y **superponer** esta curva
  a la de 4.1, con colores/símbolos y leyendas distintas: `"densidad fija"` vs `"densidad libre"`.

### Punto 5 — Formatos de archivo

Ver §6. Son los formatos estándar de la cátedra (estático + dinámico) y se reutilizarán en los TPs
siguientes.

---

## 3. Decisiones técnicas del grupo

| Aspecto | Decisión |
|---|---|
| Motor de simulación (CIM, generador, IO) | **Java** (build con Maven) |
| Análisis, gráficos y demo | **Python** (NumPy + Matplotlib) |
| Demo interactiva | **Matplotlib con evento `button_press_event`** |
| Acoplamiento entre ambos | **Ninguno en tiempo real**: Java escribe archivos, Python los lee |

**Principio rector (importante):** la simulación se corre **OFFLINE**. La animación y todos los
observables **surgen de los archivos** que la simulación produjo. Por lo tanto:

> **Imprimir toda la información relevante de cada corrida** (inputs, resultados parciales,
> outputs, tiempos) para no tener que volver a correr toda la simulación cuando se quiera analizar
> otro aspecto.

Concretamente: cada corrida deja en `output/` los archivos estático/dinámico usados, el archivo de
vecinos, y un archivo de metadatos con los parámetros y tiempos. Los scripts de Python **nunca**
recalculan vecinos ni regeneran partículas.

---

## 4. Estructura del repositorio

**Estado actual:** los cuatro puntos están implementados, verificados y documentados. Lo que queda
es la presentación en vivo (punto 2, en clase) y armar las slides a partir de `docs/informe.md`.

```
SdS-TP1/
├── AGENTS.md                    # este archivo
├── README.md                    # instrucciones de uso para humanos
├── cim-java/                    # motor de simulación
│   ├── pom.xml
│   └── src/main/java/ar/edu/itba/sds/
│       ├── Main.java                  # CLI: parsea args, orquesta, escribe outputs
│       ├── cli/
│       │   └── CliArgs.java           # parseo de --flags, compartido por los dos ejecutables
│       ├── model/
│       │   ├── Particle.java          # id, x, y, r, (vx, vy para el futuro)
│       │   ├── NeighborLists.java     # resultado con arrays primitivos (sin boxing)
│       │   └── SystemConfig.java      # N, L, M, rc, pbc, seed, rMin, rMax
│       ├── generator/
│       │   └── ParticleGenerator.java # generación aleatoria sin solapamiento
│       ├── neighbors/
│       │   ├── NeighborFinder.java    # interfaz común
│       │   ├── CellIndexMethod.java   # CIM (con y sin PBC)
│       │   └── BruteForce.java        # O(N²), baseline de validación
│       ├── io/
│       │   ├── StaticFileIO.java      # lectura/escritura del archivo estático
│       │   ├── DynamicFileIO.java     # lectura/escritura del archivo dinámico
│       │   └── OutputWriter.java      # archivo de vecinos + metadatos
│       └── bench/
│           └── BenchmarkRunner.java   # barridos de M y de N → CSV
├── analysis/                    # Python
│   ├── requirements.txt
│   ├── demo_interactiva.py      # punto 2: clic → colorea vecinos
│   ├── plot_static.py           # punto 1: figura partícula elegida + vecinos
│   ├── plot_m.py                # punto 3: tiempo vs M
│   ├── plot_n.py                # punto 4: tiempo vs N (densidad fija y libre)
│   └── common/
│       ├── parsers.py           # lectores de static/dynamic/neighbors/run.json
│       ├── bench.py             # lectura y agregación de los CSV de benchmark
│       ├── axes.py              # etiquetado de los ejes logarítmicos
│       └── render.py            # dibujo del sistema + selección de partícula
├── output/                      # artefactos de corridas (gitignoreado salvo los usados en el informe)
│   └── bench/                   # CSV y figuras de los puntos 3 y 4
└── docs/
    └── informe.md               # resultados, tablas y respuesta a la pregunta conceptual
```

**Convención de nombres en `output/`:** una carpeta por corrida, con los parámetros en el nombre,
p. ej. `output/N1000_L20_M10_rc1.0_pbc-false_seed42/` conteniendo `static.txt`, `dynamic.txt`,
`neighbors.txt`, `run.json`.

---

## 5. El algoritmo, en detalle

### 5.1 Generación de partículas sin solapamiento

- Sortear `(x, y)` uniforme en `[r_i, L - r_i]²` (sin PBC) o en `[0, L)²` (con PBC), y
  `r_i ~ U[0.23, 0.26]`.
- **Rechazo:** si la nueva partícula se solapa con alguna ya colocada
  (`dist(centros) < r_i + r_j`), **se descarta y se sortea otra**. No se "empuja" ni se relaja.
- Con PBC, el chequeo de solapamiento también debe usar **imagen mínima**.
- El generador debe aceptar una **semilla** para reproducibilidad y tener un **límite de intentos**
  que aborte con error claro cuando la densidad pedida es irrealizable (esto define el "máximo `N`
  generable en la geometría" que pide el punto 4).
- Para `N` grande el rechazo ingenuo es O(N²) por intento: se usa una **grilla auxiliar** (celdas de
  lado `2·rMax`) para chequear solapamiento sólo contra las celdas cercanas.

**Límite medido:** con `L=20` y `r_i = U[0.23, 0.26]`, el muestreo por rechazo satura en
**~1067 partículas** (≈50% del área ocupada, consistente con el límite teórico del *random
sequential adsorption* para discos). Ese es el "máximo N generable en la geometría" que piden los
puntos 3 y 4 para `L=20`.

### 5.2 Distancia borde a borde

```
d_ij = sqrt((x_i - x_j)² + (y_i - y_j)²) - r_i - r_j
```

`i` y `j` son vecinas ⟺ `d_ij < r_c`.

Con **PBC**, las diferencias `Δx`, `Δy` se toman por **imagen mínima**:
`Δx -= L * round(Δx / L)` (idem `Δy`).

### 5.3 Criterio sobre el tamaño de celda (`L/M`) — la pregunta conceptual del TP

Para partículas **puntuales**, el CIM exige `L/M > r_c` para que baste con revisar las 8 celdas
adyacentes (más la propia).

Con partículas de **radio no nulo**, el criterio de vecindad involucra los radios:

```
dist(centros) < r_c + r_i + r_j  ≤  r_c + 2·r_max
```

El **centro** de una vecina puede estar más lejos que `r_c` aunque su **borde** caiga en la celda
contigua. Por lo tanto el criterio se corrige a:

```
L/M  >  r_c + 2·r_max            →       M_max = floor( L / (r_c + 2·r_max) )
```

con `r_max` el radio máximo presente en el sistema (con `r_i = U[0.23, 0.26]` → `r_max = 0.26`,
luego `L/M > 1.52` y con `L=20` queda `M_max = 13`).

**El programa debe validar esto y fallar con un mensaje explícito** si el `M` pedido supera
`M_max` (lo pide textualmente el punto 3). No hay que "arreglarlo" silenciosamente ampliando el
radio de búsqueda de celdas.

### 5.4 Cell Index Method

1. Construir una grilla de `M × M` celdas de lado `L/M`.
2. Asignar cada partícula a su celda: `cx = floor(x·M/L)`, `cy = floor(y·M/L)` (clampear en el
   borde para evitar índice `M` por errores de punto flotante).
3. Para cada celda, comparar sus partículas contra las de la propia celda y las **vecinas**.
   - **Optimización estándar:** recorrer sólo **la mitad** de las celdas vecinas (p. ej. arriba,
     arriba-derecha, derecha, abajo-derecha) y registrar cada par encontrado en **ambas**
     direcciones. La relación de vecindad es simétrica: hacerlo así evita duplicar trabajo.
   - **Sin PBC:** los índices fuera de `[0, M)` simplemente no existen.
   - **Con PBC:** los índices se toman módulo `M` y la distancia usa imagen mínima.
4. `M = 1` degenera en **fuerza bruta** (todas contra todas) — así lo pide el punto 3.

### 5.5 Validación

`BruteForce` (O(N²)) existe para **verificar que el CIM da exactamente el mismo conjunto de
vecinos**, con y sin PBC. Cualquier cambio en el CIM debe seguir pasando esa comparación. Es la
red de seguridad principal del TP.

### 5.6 Medición de tiempos

- Cronometrar **únicamente la búsqueda de vecinos**: no la generación de partículas, no la
  construcción de la grilla si se quiere aislar el barrido (documentar qué se incluye y ser
  consistente), y **nunca** la escritura de archivos.
- Usar `System.nanoTime()`.
- Repetir la búsqueda **muchas veces** (10 / 100 / 1000 según el costo) sobre la **misma**
  configuración de partículas, descartando algunas iteraciones iniciales de **warm-up** (la JVM
  necesita JIT antes de dar tiempos estables — esto es crítico para que los gráficos no muestren
  artefactos).
- Reportar **promedio** y **desvío estándar** por punto.
- El `BenchmarkRunner` escribe un **CSV** con una fila por corrida individual (no sólo el
  promedio), para que el análisis en Python pueda recalcular estadísticos sin volver a correr nada.

Formato del CSV:

```csv
experiment,N,L,M,rc,pbc,seed,repetition,time_ns,neighbor_pairs
```

`experiment` vale `M` (punto 3), `N_free` (punto 4.1) o `N_fixed_density` (punto 4.2).

El calentamiento corta por **cantidad de repeticiones y por tiempo mínimo** (200 ms): con `N` chico
cada búsqueda dura microsegundos y unas decenas de repeticiones no alcanzan para que el JIT
compile, con lo que justo los puntos más baratos del barrido salían un orden de magnitud más lentos.

### 5.7 Resultados medidos (para no volver a correrlos)

Con `L=20`, `rc=1`, `r_i = U[0.23, 0.26]`, sin PBC, 300 mediciones por punto:

- **`M` óptimo = 13**, o sea `M_max`: el tiempo baja monótonamente desde `M=3` y el criterio de
  §5.3 corta el barrido antes del mínimo interior (con `M=13` todavía hay ~6 partículas por celda).
- **`M = 2` es el peor caso**, más lento que fuerza bruta: su vecindad cubre todas las celdas, así
  que hace las mismas comparaciones más el costo de la grilla.
- Ganancia sobre fuerza bruta: **7.3×** con `N=500`, **5.3×** con `N=1060`.
- Escalamiento con `N` (para `N ≥ 100`): `t ~ N^1.19` a densidad fija, `t ~ N^1.29` a densidad libre.

El detalle completo, con tablas y explicaciones, está en `docs/informe.md`.

### 5.8 Mirando hacia adelante (TPs siguientes)

Esto es una **"foto estática"**: un único instante `t0`. En los TPs siguientes habrá una
**simulación dinámica** donde el CIM se invoca **en cada paso temporal** para saber quién es vecino
de quién. Diseñar en consecuencia:

- El CIM debe ser invocable como función pura sobre un estado `(posiciones, radios)`, sin efectos
  globales.
- Evitar reasignar memoria en cada llamada: la grilla debe poder **reutilizarse/limpiarse** entre
  pasos.
- El modelo `Particle` ya incluye `vx, vy` aunque en el TP1 se escriban en cero.
- Los formatos de archivo (§6) ya soportan múltiples tiempos.

---

## 6. Formatos de archivo

Son los formatos de la cátedra. **El número de fila es la identidad de la partícula** (1, 2, ..., N).

### 6.1 Archivo estático (`static.txt`) — información constante en el tiempo

```
N
L
r1 c1
r2 c2
...
rN cN
```

- Línea 1: `N`, número total de partículas.
- Línea 2: `L`, longitud del lado del área de simulación.
- Líneas siguientes: `radio` y `propiedad` de cada partícula (la cátedra la llama "propiedad";
  acá se usa como **color**).

### 6.2 Archivo dinámico (`dynamic.txt`) — información por instante

```
t1
x1 y1 vx1 vy1
x2 y2 vx2 vy2
...
xN yN vxN vyN
t2
x1 y1 vx1 vy1
...
xN yN vxN vyN
```

En el TP1 hay **un único tiempo `t0`** y las velocidades son `0`, pero el parser debe soportar
múltiples bloques desde ya.

Alternativa admitida por el enunciado: **un archivo por tiempo**, nombrado con las cifras del
tiempo (`1.txt`, `5.txt`, `10.txt`, ...). No se usa en el TP1.

### 6.3 Archivo de output (`neighbors.txt`)

Una línea por partícula: el id de la partícula seguido de los ids de sus vecinas (distancia
borde-borde `< r_c`):

```
1 5 12 40
2 7
3
...
```

### 6.4 Metadatos de corrida (`run.json`)

Todo lo necesario para reproducir e interpretar la corrida sin re-ejecutarla: `N`, `L`, `M`, `rc`,
`pbc`, `seed`, `M_max`, tiempo de generación, tiempos de búsqueda (todas las repeticiones),
promedio, desvío, cantidad de pares vecinos, versión del código.

---

## 7. Cómo correr (objetivo)

Ver [README.md](README.md) para la lista completa de flags. Lo esencial:

```bash
# Motor
cd cim-java && mvn -q package && cd ..

# Punto 1: generar sistema + calcular vecinos + escribir outputs (con verificación)
java -jar cim-java/target/cim.jar --N 1000 --M 13 --rc 1.0 --seed 42 --reps 10 --verify \
     --out output/demo
java -jar cim-java/target/cim.jar --N 1000 --M 13 --pbc --verify --out output/demo_pbc

# Punto 2: demo interactiva (clic sobre una partícula)
python3 analysis/demo_interactiva.py output/demo --grid

# Punto 1 (figura): partícula pasada como input
python3 analysis/plot_static.py output/demo --id 42 --grid

# Punto 3: barrido de M → CSV → figura
java -cp cim-java/target/cim.jar ar.edu.itba.sds.bench.BenchmarkRunner \
     --sweep M --N 500,1060 --reps 100 --seeds 3 --out output/bench/bench_M.csv
python3 analysis/plot_m.py output/bench/bench_M.csv

# Punto 4: barridos de N (densidad libre y fija) → CSV → figura superpuesta
java -cp cim-java/target/cim.jar ar.edu.itba.sds.bench.BenchmarkRunner \
     --sweep N --M 13 --reps 100 --seeds 3 --points 12 --out output/bench/bench_N_libre.csv
java -cp cim-java/target/cim.jar ar.edu.itba.sds.bench.BenchmarkRunner \
     --sweep density --M 13 --rho 1.25 --reps 100 --seeds 3 --points 12 \
     --out output/bench/bench_N_densidad_fija.csv
python3 analysis/plot_n.py output/bench/bench_N_libre.csv output/bench/bench_N_densidad_fija.csv
```

**Mantener este bloque actualizado** si cambian los flags.

---

## 8. Convenciones y expectativas para agentes

- **Idioma:** español en documentación, informe y mensajes al usuario. Identificadores de código en
  inglés.
- **Reproducibilidad:** todo lo aleatorio pasa por una semilla explícita. Nunca `Math.random()`
  suelto.
- **No mezclar responsabilidades:** Java calcula y escribe archivos; Python sólo lee y grafica.
  Si un script de Python empieza a calcular vecindades, algo se hizo mal.
- **No borrar `output/`** sin preguntar: puede contener las corridas usadas en el informe.
- **Antes de tocar el CIM**, correr la comparación contra `BruteForce` (§5.5) y volver a correrla
  después.
- **Los gráficos siempre llevan** barras de error (desvío estándar) y etiquetas de ejes con
  unidades. Los ejes son **lineales y equiespaciados** por decisión del grupo: el eje `N` es
  categórico (un lugar por valor medido) y el de tiempos usa ticks uniformes, para que las
  etiquetas queden parejas y cada punto se pueda ubicar. Los flags `--log` / `--log-y` reproducen
  la vista logarítmica que pide el enunciado, con los ticks menores también etiquetados
  (`common/axes.py`). Ver la advertencia de lectura en la §4 de `docs/informe.md`.
- **Rendimiento:** el TP mide tiempos; evitar introducir logging, asserts o allocations dentro del
  bucle cronometrado.

---

## 9. Checklist de entrega

- [x] Generador de partículas aleatorias sin solapamiento, con semilla y límite de intentos.
- [x] CIM sin PBC, validado contra fuerza bruta.
- [x] CIM con PBC, validado contra fuerza bruta.
- [x] Validación de `M ≤ M_max = floor(L/(r_c + 2·r_max))` con error explícito.
- [x] Lectura/escritura de archivos estático y dinámico en el formato de la cátedra.
- [x] Archivo de output de vecinos + metadatos de corrida.
- [x] Figura del punto 1: partícula elegida + vecinos coloreados.
- [x] Demo interactiva con clic del mouse (punto 2).
- [x] Punto 3: tiempo vs `M` para dos valores de `N`, con promedio y desvío.
- [x] Punto 4.1: tiempo vs `N` a `L=20` (≥10 valores, desde `N=10` al máximo).
- [x] Punto 4.2: tiempo vs `N` a densidad constante, superpuesto a 4.1 con leyendas.
- [x] Respuesta escrita a la pregunta conceptual sobre `L/M > r_c` con `r_i > 0` (§2 del informe).
- [x] Informe con resultados y tablas en `docs/informe.md`.
- [ ] Slides de la presentación (a partir de `docs/informe.md`).
