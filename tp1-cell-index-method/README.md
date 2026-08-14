# SdS TP1 — Búsqueda Eficiente de Partículas Vecinas (Cell Index Method)

Motor de simulación en **Java** + análisis y visualización en **Python**.
El contexto completo del trabajo práctico está en [AGENTS.md](AGENTS.md).

## Requisitos

- Java 21 y Maven
- Python 3.10+ con `matplotlib` y `numpy`

## Compilar

El proyecto es un módulo del multi-módulo Maven de la raíz del repo y depende de la librería
compartida `common` (que contiene el CIM, el modelo de partículas y el IO de archivos).

```bash
# Desde la raíz del repositorio (compila common + todos los TPs)
mvn package          # genera tp1-cell-index-method/cim-java/target/cim.jar
```

## Correr una simulación

```bash
# Desde la raíz del repo
java -jar cim-java/target/cim.jar --N 1000 --M 13 --rc 1.0 --seed 42 --reps 10 --verify \
     --out output/demo
```

Opciones principales (`--help` lista todas):

| Flag | Descripción | Default |
|---|---|---|
| `--N` | cantidad de partículas | 1000 |
| `--L` | lado del área | 20 |
| `--M` | celdas por lado de la grilla | el máximo válido |
| `--rc` | radio de interacción | 1.0 |
| `--rmin` / `--rmax` | rango de radios | 0.23 / 0.26 |
| `--pbc` | activa condiciones periódicas de contorno | desactivadas |
| `--seed` | semilla del generador | 42 |
| `--reps` | repeticiones cronometradas | 10 |
| `--brute` | usa fuerza bruta en lugar del CIM | — |
| `--verify` | compara el CIM contra fuerza bruta | — |
| `--input <dir>` | carga `static.txt` + `dynamic.txt` en vez de generar | — |
| `--out <dir>` | directorio de salida | `output/<auto>` |

Cada corrida deja en `--out`:

- `static.txt` — `N`, `L` y el radio/color de cada partícula
- `dynamic.txt` — posiciones y velocidades en `t=0`
- `neighbors.txt` — por cada partícula, los ids de sus vecinas a distancia borde-borde `< rc`
- `run.json` — parámetros, tiempo de cada repetición, promedio y desvío

## Barridos de tiempo de cómputo (puntos 3 y 4)

`BenchmarkRunner` cronometra la búsqueda de vecinos variando un parámetro y escribe un CSV con
**una fila por repetición** (no promedios), para poder recalcular estadísticos sin volver a correr
nada. Antes de medir hace repeticiones de calentamiento hasta que el JIT compiló el bucle caliente.

```bash
# Punto 3: tiempo vs M, para un N intermedio y el máximo de la geometría
java -cp cim-java/target/cim.jar ar.edu.itba.sds.bench.BenchmarkRunner \
     --sweep M --N 500,1060 --reps 100 --seeds 3 --out output/bench/bench_M.csv

# Punto 4.1: tiempo vs N con L fijo (la densidad crece con N)
java -cp cim-java/target/cim.jar ar.edu.itba.sds.bench.BenchmarkRunner \
     --sweep N --M 13 --reps 100 --seeds 3 --points 12 --out output/bench/bench_N_libre.csv

# Punto 4.2: tiempo vs N manteniendo la densidad rho = N/L^2 constante
java -cp cim-java/target/cim.jar ar.edu.itba.sds.bench.BenchmarkRunner \
     --sweep density --M 13 --rho 1.25 --reps 100 --seeds 3 --points 12 \
     --out output/bench/bench_N_densidad_fija.csv

# Fuerza bruta: el mismo barrido del punto 4.1 pero con M=1 (una sola celda = todas contra todas)
java -cp cim-java/target/cim.jar ar.edu.itba.sds.bench.BenchmarkRunner \
     --sweep N --M 1 --reps 100 --seeds 3 --points 12 --out output/bench/bench_N_bruta.csv

# Fuerza bruta con densidad fija: como el punto 4.2 pero con M=1 (--fixedM evita escalar M con L)
java -cp cim-java/target/cim.jar ar.edu.itba.sds.bench.BenchmarkRunner \
     --sweep density --M 1 --fixedM --rho 1.25 --reps 100 --seeds 3 --points 12 \
     --out output/bench/bench_N_densidad_fija_bruta.csv
```

Flags propios del barrido (`--help` lista todos):

| Flag | Descripción | Default |
|---|---|---|
| `--sweep` | `M`, `N` (densidad libre) o `density` (densidad fija) | `M` |
| `--N` | valores de N separados por coma | según el barrido |
| `--Nmin` / `--Nmax` / `--points` | rango y cantidad de valores de N log-espaciados | 10 / máximo de la geometría / 12 |
| `--M` | M óptimo hallado en el punto 3 | el máximo válido |
| `--rho` | densidad a mantener constante en `--sweep density` | 1.25 |
| `--fixedM` | mantiene M constante en vez del lado de celda | — |
| `--reps` | repeticiones cronometradas por configuración | 100 |
| `--seeds` | configuraciones de partículas distintas por punto | 1 |

Columnas del CSV: `experiment,N,L,M,rc,pbc,seed,repetition,time_ns,neighbor_pairs`.

## Visualizar

```bash
pip install -r analysis/requirements.txt

# Demo interactiva: clic sobre una partícula y se colorean sus vecinas
python3 analysis/demo_interactiva.py output/demo --grid

# Figura estática con una partícula pasada como input
python3 analysis/plot_static.py output/demo --id 42 --grid

# Punto 3: tiempo vs M (imprime además la tabla de medias y desvíos)
python3 analysis/plot_m.py output/bench/bench_M.csv

# Punto 4: tiempo vs N, con las curvas de densidad libre y fija superpuestas
python3 analysis/plot_n.py output/bench/bench_N_libre.csv output/bench/bench_N_densidad_fija.csv

# CIM (M óptimo) contra fuerza bruta (M=1): imprime además el speedup por cada N
python3 analysis/plot_versus.py output/bench/bench_N_libre.csv output/bench/bench_N_bruta.csv

# Ídem pero con densidad fija (cada CSV es una serie: es fuerza bruta si todo el barrido usó M=1)
python3 analysis/plot_versus.py output/bench/bench_N_densidad_fija.csv \
    output/bench/bench_N_densidad_fija_bruta.csv
```

Los ejes son lineales y equiespaciados: en `plot_n.py` el eje `N` es categórico (un lugar por valor
medido) y el de tiempos lleva ticks uniformes. `--log` (en `plot_n.py` y `plot_versus.py`) y `--log-y` / `--log-x` (en
`plot_m.py`) vuelven a la escala logarítmica, que separa mejor los puntos cuando los tiempos abarcan
varios órdenes de magnitud.

Controles de la demo: **clic izquierdo** elige partícula (clic en el vacío deselecciona),
**`n`** elige una al azar, **`g`** muestra/oculta la grilla de celdas, **`q`** sale.

Los scripts de Python **sólo leen y grafican**: los vecinos salen del `neighbors.txt` que produjo
el CIM, nunca se recalculan.

## Verificar que el CIM funciona

```bash
# Compara contra fuerza bruta O(N^2); imprime OK o falla con exit code 2
java -jar cim-java/target/cim.jar --N 1000 --M 13 --verify --out /tmp/check
java -jar cim-java/target/cim.jar --N 1000 --M 13 --pbc --verify --out /tmp/check
```

El resultado es independiente de `M`: con los mismos `N`, `L`, `rc` y semilla, todos los `M`
válidos devuelven exactamente el mismo conjunto de vecinos.

## Límites conocidos

- **`M` máximo:** `floor(L / (rc + 2*rMax))`. Con `L=20`, `rc=1`, `rMax=0.26` → **`M = 13`**.
  Pedir más es un error (el programa aborta con mensaje explícito).
- **`N` máximo con `L=20`:** ~**1067** partículas. Es el límite del muestreo por rechazo
  (~50% del área ocupada); más allá, ninguna posición candidata queda libre.
  Se puede empujar un poco con `--maxAttempts`. Los barridos usan **1060**, que es la estimación
  automática (`ParticleGenerator.estimateMaxParticles`) y el default de `--Nmax`.

## Resultados

Ver [docs/informe.md](docs/informe.md) para el análisis completo, las tablas y la respuesta a la
pregunta conceptual sobre el criterio `L/M > rc` con partículas de radio no nulo.
